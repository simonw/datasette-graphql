from datasette import hookimpl
from datasette.utils.asgi import Response
from graphql.execution.executors.asyncio import AsyncioExecutor
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
    print("here we go")
    body = await post_body(request)
    if not body:
        return Response.text("Hello from GraphQL")

    incoming = json.loads(body)
    query = incoming["query"]

    schema = await schema_for_database(datasette)

    result = await graphql(
        schema, query, executor=AsyncioExecutor(), return_promise=True
    )
    if result.errors:
        print(result.errors)
        return Response.json(
            json.loads(json.dumps(result.errors, default=repr)), status=500
        )
    else:
        print(result.data)
        return Response.json(result.data)


@hookimpl
def register_routes():
    return [
        (r"^/graphql$", view_graphql),
    ]
