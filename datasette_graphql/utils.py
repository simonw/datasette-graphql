from base64 import b64decode, b64encode
from collections import namedtuple
from enum import Enum
from datasette.utils.asgi import Request
import graphene
import urllib
import sqlite_utils
import wrapt

TableMetadata = namedtuple(
    "TableMetadata", ("columns", "foreign_keys", "fks_back", "pks", "supports_fts")
)


class Bytes(graphene.Scalar):
    # Replace with graphene.Base64 after graphene 3.0 is released
    @staticmethod
    def serialize(value):
        if isinstance(value, bytes):
            return b64encode(value).decode("utf-8")
        return value

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if isinstance(value, bytes):
            return value
        else:
            return b64decode(value)


types = {
    str: graphene.String(),
    float: graphene.Float(),
    int: graphene.Int(),
    bytes: Bytes(),
}


class PageInfo(graphene.ObjectType):
    endCursor = graphene.String()
    hasNextPage = graphene.Boolean()


async def schema_for_database(datasette, database=None, tables=None):
    db = datasette.get_database(database)

    # Perform all introspection in a single call to the execute_fn thread
    def introspect_tables(conn):
        db = sqlite_utils.Database(conn)

        table_names = db.table_names()
        view_names = db.view_names()

        table_metadata = {}

        for table in table_names + view_names:
            columns = db[table].columns_dict
            foreign_keys = []
            pks = []
            supports_fts = False
            fks_back = []
            if hasattr(db[table], "foreign_keys"):
                # Views don't have this
                foreign_keys = db[table].foreign_keys
                pks = db[table].pks
                supports_fts = bool(db[table].detect_fts())
                # Gather all foreign keys pointing back here
                collected = []
                for t in db.tables:
                    collected.extend(t.foreign_keys)
                fks_back = [f for f in collected if f.other_table == table]
            table_metadata[table] = TableMetadata(
                columns, foreign_keys, fks_back, pks, supports_fts
            )

        return table_metadata

    table_metadata = await db.execute_fn(introspect_tables)

    # Construct the tableFilter classes
    table_filters = {
        table: make_table_filter_class(table, meta.columns)
        for table, meta in table_metadata.items()
    }
    # And the table_collection_kwargs
    table_collection_kwargs = {}
    for table, meta in table_metadata.items():
        column_names = meta.columns.keys()
        options = list(zip(column_names, column_names))
        sort_enum = graphene.Enum.from_enum(Enum("{}Sort".format(table), options))
        sort_desc_enum = graphene.Enum.from_enum(
            Enum("{}SortDesc".format(table), options)
        )
        kwargs = dict(
            filter=graphene.List(
                table_filters[table],
                description='Filters e.g. {name: {eq: "datasette"}}',
            ),
            where=graphene.String(
                description="Extra SQL where clauses, e.g. \"name='datasette'\""
            ),
            first=graphene.Int(description="Number of results to return"),
            after=graphene.String(
                description="Start at this pagination cursor (from tableInfo { endCursor })"
            ),
            sort=graphene.Argument(sort_enum, description="Sort by this column"),
            sort_desc=graphene.Argument(
                sort_desc_enum, description="Sort by this column descending"
            ),
        )
        if meta.supports_fts:
            kwargs["search"] = graphene.String(description="Search for this term")
        table_collection_kwargs[table] = kwargs

    # For each table, expose a graphene.List
    to_add = []
    table_classes = {}
    table_collection_classes = {}

    for (
        table,
        (columns, foreign_keys, fks_back, pks, supports_fts),
    ) in table_metadata.items():
        fks_by_column = {fk.column: fk for fk in foreign_keys}
        # Create a node class for this table
        table_dict = {}
        if pks == ["rowid"]:
            table_dict["rowid"] = graphene.Int()
        column_names = []
        for colname, coltype in columns.items():
            column_names.append(colname)
            if colname in fks_by_column:
                fk = fks_by_column[colname]
                table_dict[colname] = graphene.Field(
                    make_table_getter(table_classes, fk.other_table)
                )
                table_dict["resolve_{}".format(colname)] = make_fk_resolver(
                    db, table, table_classes, fk
                )
            else:
                table_dict[colname] = types[coltype]

        # Now add the backwards foreign key fields for related items
        for fk in fks_back:
            meta = table_metadata[fk.table]
            fk_table_columns = meta.columns
            filter_class = table_filters[fk.table]
            table_dict["{}_list".format(fk.table)] = graphene.Field(
                make_table_collection_getter(table_collection_classes, fk.table),
                **table_collection_kwargs[fk.table]
            )
            table_dict["resolve_{}_list".format(fk.table)] = make_table_resolver(
                datasette,
                db.name,
                fk.table,
                table_classes,
                meta.supports_fts,
                default_where="[{}] = ".format(fk.column)
                + "{root."
                + fk.other_column
                + "}",
            )

        table_node_class = type(table, (graphene.ObjectType,), table_dict)
        table_classes[table] = table_node_class

        # We also need a table collection class - this is the thing with the
        # nodes, edges, pageInfo and totalCount fields for that table
        table_collection_class = make_table_collection_class(
            table, table_node_class, pks
        )
        table_collection_classes[table] = table_collection_class
        to_add.append(
            (
                table,
                graphene.Field(
                    table_collection_class, **table_collection_kwargs[table]
                ),
            )
        )
        to_add.append(
            (
                "resolve_{}".format(table),
                make_table_resolver(
                    datasette, db.name, table, table_classes, supports_fts
                ),
            )
        )
        # *_get field
        table_get_kwargs = dict(table_collection_kwargs[table])
        table_get_kwargs.pop("first")
        # Add an argument for each primary key
        for pk in pks:
            if pk == "rowid" and pk not in columns:
                pk_column_type = graphene.Int()
            else:
                pk_column_type = types[columns[pk]]
            table_get_kwargs[pk] = pk_column_type
        to_add.append(
            (
                "{}_get".format(table),
                graphene.Field(table_node_class, **table_get_kwargs),
            )
        )
        to_add.append(
            (
                "resolve_{}_get".format(table),
                make_table_resolver(
                    datasette,
                    db.name,
                    table,
                    table_classes,
                    supports_fts,
                    pk_args=pks,
                    return_first_row=True,
                ),
            )
        )

    Query = type(
        "Query", (graphene.ObjectType,), {key: value for key, value in to_add},
    )
    return graphene.Schema(
        query=Query,
        auto_camelcase=(datasette.plugin_config("datasette-graphql") or {}).get(
            "auto_camelcase", False
        ),
    )


def make_table_collection_class(table, table_class, pks):
    class _Edge(graphene.ObjectType):
        cursor = graphene.String()
        node = graphene.Field(table_class)

        class Meta:
            name = "{}Edge".format(table)

    class _TableCollection(graphene.ObjectType):
        totalCount = graphene.Int()
        pageInfo = graphene.Field(PageInfo)
        nodes = graphene.List(table_class)
        edges = graphene.List(_Edge)

        def resolve_totalCount(parent, info):
            return parent["filtered_table_rows_count"]

        def resolve_nodes(parent, info):
            return parent["rows"]

        def resolve_edges(parent, info):
            return [
                {"cursor": path_from_row_pks(row, pks, use_rowid=not pks), "node": row}
                for row in parent["rows"]
            ]

        def resolve_pageInfo(parent, info):
            return {
                "endCursor": parent["next"],
                "hasNextPage": parent["next"] is not None,
            }

        class Meta:
            name = "{}Collection".format(table)

    return _TableCollection


class StringOperations(graphene.InputObjectType):
    exact = graphene.String(name="eq", description="Exact match")
    not_ = graphene.String(name="not", description="Not exact match")
    contains = graphene.String(description="String contains")
    endswith = graphene.String(description="String ends with")
    startswith = graphene.String(description="String starts with")
    gt = graphene.String(description="is greater than")
    gte = graphene.String(description="is greater than or equal to")
    lt = graphene.String(description="is less than")
    lte = graphene.String(description="is less than or equal to")
    like = graphene.String(description=r"is like (% for wildcards)")
    notlike = graphene.String(description="is not like")
    glob = graphene.String(description="glob matches (* for wildcards)")
    in_ = graphene.List(graphene.String, name="in", description="in this list")
    notin = graphene.List(graphene.String, description="not in this list")
    arraycontains = graphene.String(description="JSON array contains this value")
    date = graphene.String(description="Value is a datetime on this date")
    isnull = graphene.Boolean(description="Value is null")
    notnull = graphene.Boolean(description="Value is not null")
    isblank = graphene.Boolean(description="Value is null or blank")
    notblank = graphene.Boolean(description="Value is not null or blank")


class IntegerOperations(graphene.InputObjectType):
    exact = graphene.Int(name="eq", description="Exact match")
    not_ = graphene.Int(name="not", description="Not exact match")
    gt = graphene.Int(description="is greater than")
    gte = graphene.Int(description="is greater than or equal to")
    lt = graphene.Int(description="is less than")
    lte = graphene.Int(description="is less than or equal to")
    in_ = graphene.List(graphene.Int, name="in", description="in this list")
    notin = graphene.List(graphene.Int, description="not in this list")
    arraycontains = graphene.Int(description="JSON array contains this value")
    isnull = graphene.Boolean(description="Value is null")
    notnull = graphene.Boolean(description="Value is not null")
    isblank = graphene.Boolean(description="Value is null or blank")
    notblank = graphene.Boolean(description="Value is not null or blank")


types_to_operations = {
    str: StringOperations,
    int: IntegerOperations,
    float: IntegerOperations,
}


def make_table_filter_class(table, columns):
    return type(
        "{}Filter".format(table),
        (graphene.InputObjectType,),
        {
            column: (types_to_operations.get(column_type) or StringOperations)()
            for column, column_type in columns.items()
        },
    )


class DatasetteSpecialConfig(wrapt.ObjectProxy):
    def config(self, key):
        if key == "suggest_facets":
            return False
        return self.__wrapped__.config(key)


def make_table_resolver(
    datasette,
    database_name,
    table_name,
    table_classes,
    supports_fts,
    default_where=None,
    pk_args=None,
    return_first_row=False,
):
    from datasette.views.table import TableView

    async def resolve_table(
        root,
        info,
        filter=None,
        where=None,
        first=None,
        after=None,
        search=None,
        sort=None,
        sort_desc=None,
        **kwargs
    ):
        if first is None:
            first = 10

        if return_first_row:
            first = 1

        pairs = []
        for filter_ in filter or []:
            for column_name, operations in filter_.items():
                for operation_name, value in operations.items():
                    if isinstance(value, list):
                        value = ",".join(value)
                    pairs.append(
                        [
                            "{}__{}".format(column_name, operation_name.rstrip("_")),
                            value,
                        ]
                    )

        if pk_args is not None:
            for pk in pk_args:
                if kwargs.get(pk) is not None:
                    pairs.append([pk, kwargs[pk]])

        qs = {}
        qs.update(pairs)
        if after:
            qs["_next"] = after
        qs["_size"] = first

        if search and supports_fts:
            qs["_search"] = search

        if where:
            qs["_where"] = where

        if sort:
            qs["_sort"] = sort
        elif sort_desc:
            qs["_sort_desc"] = sort_desc

        if default_where:
            qs["_where"] = default_where.format(root=root)

        path_with_query_string = "/{}/{}.json?{}".format(
            database_name, table_name, urllib.parse.urlencode(qs)
        )
        request = Request.fake(path_with_query_string)

        view = TableView(DatasetteSpecialConfig(datasette))
        data, _, _ = await view.data(
            request, database=database_name, hash=None, table=table_name, _next=after
        )
        klass = table_classes[table_name]
        data["rows"] = [klass(**dict(r)) for r in data["rows"]]
        if return_first_row:
            try:
                return data["rows"][0]
            except IndexError:
                return None
        else:
            return data

    return resolve_table


def make_fk_resolver(db, table, table_classes, fk):
    async def resolve_foreign_key(parent, info):
        # retrieve the correct column from parent
        pk = getattr(parent, fk.column)
        sql = "select * from [{}] where [{}] = :v".format(
            fk.other_table, fk.other_column
        )
        params = {"v": pk}
        results = await db.execute(sql, params)
        fk_class = table_classes[fk.other_table]
        try:
            return [fk_class(**dict(row)) for row in results.rows][0]
        except IndexError:
            return None

    return resolve_foreign_key


def make_table_getter(table_classes, table):
    def getter():
        return table_classes[table]

    return getter


def make_table_collection_getter(table_collection_classes, table):
    def getter():
        return table_collection_classes[table]

    return getter


def path_from_row_pks(row, pks, use_rowid, quote=True):
    """ Generate an optionally URL-quoted unique identifier
        for a row from its primary keys."""
    if use_rowid:
        bits = [row.rowid]
    else:
        bits = [getattr(row, pk) for pk in pks]
    if quote:
        bits = [urllib.parse.quote_plus(str(bit)) for bit in bits]
    else:
        bits = [str(bit) for bit in bits]

    return ",".join(bits)
