from datasette.filters import Filters
import graphene
import urllib
import sqlite_utils


def path_from_row_pks(row, pks, use_rowid, quote=True):
    """ Generate an optionally URL-quoted unique identifier
        for a row from its primary keys."""
    if use_rowid:
        bits = [row["rowid"]]
    else:
        bits = [
            row[pk]["value"] if isinstance(row[pk], dict) else row[pk] for pk in pks
        ]
    if quote:
        bits = [urllib.parse.quote_plus(str(bit)) for bit in bits]
    else:
        bits = [str(bit) for bit in bits]

    return ",".join(bits)


types = {
    str: graphene.String(),
    float: graphene.Float(),
    int: graphene.Int(),
    bytes: graphene.String(),
}


class Repo(graphene.ObjectType):
    id = graphene.String()
    node_id = graphene.String()
    name = graphene.String()
    full_name = graphene.String()
    private = graphene.String()
    owner = graphene.String()
    html_url = graphene.String()
    description = graphene.String()
    fork = graphene.String()
    created_at = graphene.String()
    updated_at = graphene.String()
    pushed_at = graphene.String()
    homepage = graphene.String()
    size = graphene.String()
    stargazers_count = graphene.Int()


class RepoEdge(graphene.ObjectType):
    cursor = graphene.String()
    node = graphene.Field(Repo)


class PageInfo(graphene.ObjectType):
    endCursor = graphene.String()
    hasNextPage = graphene.Boolean()


class Repos(graphene.ObjectType):
    totalCount = graphene.Int()
    pageInfo = graphene.Field(PageInfo)
    nodes = graphene.List(Repo)
    edges = graphene.List(RepoEdge)

    def resolve_totalCount(parent, info):
        return len(parent)

    def resolve_nodes(parent, info):
        return parent

    def resolve_edges(parent, info):
        return [{
            "cursor": path_from_row_pks(row, ["id"], use_rowid=False),
            "node": row
        } for row in parent]

    def resolve_pageInfo(parent, info):
        last_row = parent[-1]
        return {
            "endCursor": path_from_row_pks(last_row, ["id"], use_rowid=False),
            "hasNextPage": False
        }



def make_collection(db, table, table_class):
    edge_class = type(
        "{}_edge".format(table),
        (graphene.ObjectType,),
        {"node": table_class, "cursor": graphene.String()},
    )

    async def total_count(parent, info):
        # TODO: include where clause
        return (await db.execute("select count(*) from [{}]{}".format(table))).first()[
            0
        ]

    collection = type(
        table,
        (graphene.ObjectType,),
        {
            "nodes": graphene.List(of_type=table_class,),
            "resolve_nodes": make_all_rows_resolver(db, table, table_class),
            "edges": graphene.List(of_type=edge_class,),
            "resolve_edges": make_all_rows_resolver(
                db, table, table_class, edge_class=edge_class
            ),
            "totalCount": graphene.Int(),
            "resolve_totalCount": total_count,
        },
    )
    return collection


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
            return columns, foreign_keys

        columns, foreign_keys = await db.execute_fn(introspect_table)
        fks_by_column = {fk.column: fk for fk in foreign_keys}

        # Create a class for this table
        table_dict = {}
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

        table_class = type(table, (graphene.ObjectType,), table_dict)
        table_classes[table] = table_class
        if table == "repos":
            continue
        to_add.append(
            (
                table,
                make_collection(db, table, table_class)()
            )
        )
        to_add.append(
            ("resolve_{}".format(table), make_all_rows_resolver(db, table, table_class))
        )

    # Special case for repos
    to_add.append(("repos", graphene.Field(Repos, filters=graphene.List(graphene.String))))

    async def resolve_repos(root, info, filters=None):
        table_name = "repos"
        print("filters = ", filters)
        where_clause = ""
        params = {}
        if filters:
            pairs = [f.split("=", 1) for f in filters]
            print("  pairs = ", pairs)
            filter_obj = Filters(pairs)
            where_clause_bits, params = filter_obj.build_where_clauses(table_name)
            print("  where_clause_bits={}, params={}".format(
                where_clause_bits, params
            ))
            where_clause = " where " + " and ".join(where_clause_bits)
        print("select * from [{}]{}".format(table_name, where_clause), params)
        results = await db.execute(
            "select * from [{}]{}".format(table_name, where_clause), params
        )
        print("len", len(results.rows))
        return [dict(row) for row in results.rows]

    to_add.append(("resolve_repos", resolve_repos))

    Query = type(
        "Query", (graphene.ObjectType,), {key: value for key, value in to_add},
    )
    return graphene.Schema(
        query=Query,
        auto_camelcase=(datasette.plugin_config("datasette-graphql") or {}).get(
            "auto_camelcase", False
        ),
    )


def make_all_rows_resolver(db, table, klass, edge_class=None):
    async def resolve(parent, info, filters=None):
        where_clause = ""
        params = {}
        if filters:
            pairs = [f.split("=", 1) for f in filters]
            filter_obj = Filters(pairs)
            where_clause_bits, params = filter_obj.build_where_clauses(table)
            where_clause = " where " + " and ".join(where_clause_bits)
        results = await db.execute(
            "select * from [{}]{}".format(table, where_clause), params
        )
        if edge_class:
            return [
                [
                    edge_class(node=klass(**dict(row)), cursor="CURSOR")
                    for row in result.rows
                ]
            ]
        else:
            return [klass(**dict(row)) for row in results.rows]

    return resolve


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
        return [fk_class(**dict(row)) for row in results.rows][0]

    return resolve_foreign_key


def make_table_getter(table_classes, table):
    def getter():
        return table_classes[table]

    return getter


def paginate(db, table, where=None, first=100, after=None):
    # Returns (rows_with_cursors, has_next_page)
    pass
