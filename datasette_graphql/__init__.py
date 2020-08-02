from datasette import hookimpl
from datasette.utils.asgi import Response
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql.error import format_error
from graphql import graphql
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


async def view_graphql(request, datasette):
    body = await post_body(request)
    if not body:
        return Response.html(
            await datasette.render_template("graphiql.html", request=request)
        )

    incoming = json.loads(body)
    query = incoming["query"]

    schema = await schema_for_database(datasette)

    result = await graphql(
        schema, query, executor=AsyncioExecutor(), return_promise=True
    )
    response = {"data": result.data}
    if result.errors:
        response["errors"] = [format_error(error) for error in result.errors]

    return Response.json(response, status=200 if not result.errors else 500)


@hookimpl
def register_routes():
    return [
        (r"^/graphql$", view_graphql),
    ]
