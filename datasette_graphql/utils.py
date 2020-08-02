import graphene


async def schema_for_database(datasette, database=None, tables=None):
    db = datasette.get_database(database)

    # For each table, expose a graphene.List
    to_add = []
    for table in await db.table_names():
        # Create a class for this table
        columns = await db.table_columns(table)
        klass = type(
            table,
            (graphene.ObjectType,),
            {colname: graphene.String() for colname in columns},
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
