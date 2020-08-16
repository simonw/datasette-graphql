from click import ClickException
from datasette import hookimpl
from datasette.utils.asgi import Response, NotFound
import graphene
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql.error import format_error
from graphql import graphql, print_schema
import json
from .utils import query_for_database


async def post_body(request):
    body = b""
    more_body = True
    while more_body:
        message = await request.receive()
        assert message["type"] == "http.request", message
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    return body


async def view_graphql_schema(request, datasette):
    database = request.url_vars.get("database")
    try:
        datasette.get_database(database)
    except KeyError:
        raise NotFound("Database does not exist")
    db_query = await query_for_database(datasette, database=database)
    schema = graphene.Schema(
        query=db_query,
        auto_camelcase=(datasette.plugin_config("datasette-graphql") or {}).get(
            "auto_camelcase", False
        ),
    )
    return Response.text(print_schema(schema))


async def view_graphql(request, datasette):
    body = await post_body(request)
    database = request.url_vars.get("database")

    try:
        datasette.get_database(database)
    except KeyError:
        raise NotFound("Database does not exist")

    if not body and "text/html" in request.headers.get("accept", ""):
        return Response.html(
            await datasette.render_template(
                "graphiql.html", {"database": database,}, request=request
            ),
            headers={
                "Access-Control-Allow-Headers": "content-type",
                "Access-Control-Allow-Method": "POST",
                "Access-Control-Allow-Origin": "*",
                "Vary": "accept",
            }
            if datasette.cors
            else {},
        )

    # Complex logic here for merging different databases
    db_query = await query_for_database(datasette, database=database)

    db_queries = {}
    for name in datasette.databases:
        db_queries[name] = await query_for_database(datasette, database=name)

    root_query_properties = {
        "{}_db".format(db_name): graphene.Field(
            db_query, resolver=lambda parent, info: {}
        )
        for db_name, db_query in db_queries.items()
    }
    RootQuery = type("RootQuery", (graphene.ObjectType,), root_query_properties)

    schema = graphene.Schema(
        query=RootQuery,
        auto_camelcase=(datasette.plugin_config("datasette-graphql") or {}).get(
            "auto_camelcase", False
        ),
    )

    incoming = {}
    if body:
        incoming = json.loads(body)
        query = incoming.get("query")
        variables = incoming.get("variables")
        operation_name = incoming.get("operationName")
    else:
        query = request.args.get("query")
        variables = request.args.get("variables", "")
        if variables:
            variables = json.loads(variables)
        operation_name = request.args.get("operationName")

    if not query:
        return Response.json(
            {"error": "Missing query"},
            status=400,
            headers={
                "Access-Control-Allow-Headers": "content-type",
                "Access-Control-Allow-Method": "POST",
                "Access-Control-Allow-Origin": "*",
            }
            if datasette.cors
            else {},
        )

    result = await graphql(
        schema,
        query,
        operation_name=operation_name,
        variable_values=variables,
        executor=AsyncioExecutor(),
        return_promise=True,
    )
    response = {"data": result.data}
    if result.errors:
        response["errors"] = [format_error(error) for error in result.errors]

    return Response.json(
        response,
        status=200 if not result.errors else 500,
        headers={
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Method": "POST",
            "Access-Control-Allow-Origin": "*",
        }
        if datasette.cors
        else {},
    )


@hookimpl
def register_routes():
    return [
        (r"^/graphql/(?P<database>[^/]+)\.graphql$", view_graphql_schema),
        (r"^/graphql/(?P<database>[^/]+)$", view_graphql),
        (r"^/graphql$", view_graphql),
    ]


@hookimpl
def startup(datasette):
    # Validate configuration
    config = datasette.plugin_config("datasette-graphql") or {}
    if "databases" in config:
        for database_name in config["databases"].keys():
            try:
                datasette.get_database(database_name)
            except KeyError:
                raise ClickException(
                    "datasette-graphql config error: '{}' is not a connected database".format(
                        database_name
                    )
                )
