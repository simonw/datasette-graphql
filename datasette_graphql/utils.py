import graphene
import sqlite_utils

types = {
    str: graphene.String(),
    float: graphene.Float(),
    int: graphene.Int(),
    bytes: graphene.String(),
}


async def schema_for_database(datasette, database=None, tables=None):
    db = datasette.get_database(database)

    # For each table, expose a graphene.List
    to_add = []
    for table in await db.table_names():
        # Create a class for this table
        def get_columns(conn):
            return sqlite_utils.Database(conn)[table].columns_dict

        columns = await db.execute_fn(get_columns)
        klass = type(
            table,
            (graphene.ObjectType,),
            {colname: types[coltype] for colname, coltype in columns.items()},
        )
        to_add.append((table, graphene.List(of_type=klass)))
        to_add.append(("resolve_{}".format(table), make_resolver(db, table, klass)))

    Query = type(
        "Query", (graphene.ObjectType,), {key: value for key, value in to_add},
    )
    return graphene.Schema(query=Query, auto_camelcase=False)


def make_resolver(db, table, klass):
    async def resolve(parent, info):
        results = await db.execute("select * from [{}]".format(table))
        return [klass(**dict(row)) for row in results.rows]

    return resolve
