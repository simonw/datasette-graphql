from datasette.filters import Filters
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
        to_add.append(
            (
                table,
                graphene.List(
                    of_type=table_class,
                    args={"filters": graphene.List(graphene.String)},
                    required=False,
                ),
            )
        )
        to_add.append(
            ("resolve_{}".format(table), make_all_rows_resolver(db, table, table_class))
        )

    Query = type(
        "Query", (graphene.ObjectType,), {key: value for key, value in to_add},
    )
    return graphene.Schema(query=Query, auto_camelcase=False)


def make_all_rows_resolver(db, table, klass):
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
