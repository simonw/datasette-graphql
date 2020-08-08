from click import ClickException
from datasette import hookimpl
from datasette.utils.asgi import Response, NotFound
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql.error import format_error
from graphql import graphql, print_schema
import json
from .utils import schema_for_database


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
    schema = await schema_for_database(datasette, database=database)
    return Response.text(print_schema(schema))


async def view_graphql(request, datasette):
    body = await post_body(request)
    database = request.url_vars.get("database")

    try:
        datasette.get_database(database)
    except KeyError:
        raise NotFound("Database does not exist")

    if not body:
        return Response.html(
            await datasette.render_template(
                "graphiql.html", {"database": database,}, request=request
            ),
            headers={
                "Access-Control-Allow-Headers": "content-type",
                "Access-Control-Allow-Method": "POST",
                "Access-Control-Allow-Origin": "*",
            }
            if datasette.cors
            else {},
        )
    schema = await schema_for_database(datasette, database=database)

    if request.args.get("schema"):
        return Response.text(print_schema(schema))

    incoming = {}
    if body:
        incoming = json.loads(body)
    query = incoming["query"]
    variables = incoming.get("variables")

    result = await graphql(
        schema,
        query,
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
            "Access-Control-Request-Method": "POST",
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
