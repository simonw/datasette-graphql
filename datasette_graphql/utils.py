from datasette.filters import Filters
from datasette.utils.asgi import Request
import graphene
import urllib
import sqlite_utils

types = {
    str: graphene.String(),
    float: graphene.Float(),
    int: graphene.Int(),
    bytes: graphene.String(),
}


class PageInfo(graphene.ObjectType):
    endCursor = graphene.String()
    hasNextPage = graphene.Boolean()


async def schema_for_database(datasette, database=None, tables=None):
    db = datasette.get_database(database)

    # For each table, expose a graphene.List
    to_add = []
    table_classes = {}
    for table in await db.table_names():
        # Perform all introspection in a single call to the execute_fn thread

        def introspect_table(conn):
            db = sqlite_utils.Database(conn)
            columns = db[table].columns_dict
            foreign_keys = db[table].foreign_keys
            pks = db[table].pks
            supports_fts = bool(db[table].detect_fts())
            return columns, foreign_keys, pks, supports_fts

        columns, foreign_keys, pks, supports_fts = await db.execute_fn(introspect_table)
        fks_by_column = {fk.column: fk for fk in foreign_keys}

        # Create a node class for this table
        table_dict = {}
        if pks == ["rowid"]:
            table_dict["rowid"] = graphene.Int()
        for colname, coltype in columns.items():
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

        table_node_class = type(table, (graphene.ObjectType,), table_dict)
        table_classes[table] = table_node_class

        # We also need a table collection class - this is the thing with the
        # nodes, edges, pageInfo and totalCount fields for that table
        table_collection_class = make_table_collection_class(
            table, table_node_class, pks
        )
        table_collection_kwargs = dict(
            filters=graphene.List(graphene.String),
            first=graphene.Int(),
            after=graphene.String(),
        )
        if supports_fts:
            table_collection_kwargs["search"] = graphene.String()

        to_add.append(
            (table, graphene.Field(table_collection_class, **table_collection_kwargs))
        )
        to_add.append(
            (
                "resolve_{}".format(table),
                make_table_resolver(
                    datasette, db.name, table, table_node_class, supports_fts
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


def make_table_resolver(datasette, database_name, table_name, klass, supports_fts):
    from datasette.views.table import TableView

    async def resolve_table(
        root, info, filters=None, first=None, after=None, search=None
    ):
        if first is None:
            first = 10

        pairs = []
        if filters:
            pairs = [f.split("=", 1) for f in filters]

        qs = {}
        qs.update(pairs)
        if after:
            qs["_next"] = after
        qs["_size"] = first

        if search and supports_fts:
            qs["_search"] = search

        path_with_query_string = "/{}/{}.json?{}".format(
            database_name, table_name, urllib.parse.urlencode(qs)
        )
        request = Request.fake(path_with_query_string)

        view = TableView(datasette)
        data, _, _ = await view.data(
            request, database=database_name, hash=None, table=table_name, _next=after
        )
        data["rows"] = [klass(**dict(r)) for r in data["rows"]]
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
