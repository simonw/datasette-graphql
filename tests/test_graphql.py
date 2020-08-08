from datasette.app import Datasette
import json
import pathlib
import pytest
import re
import httpx
from .fixtures import ds, db_path, db_path2


@pytest.mark.asyncio
async def test_plugin_is_installed():
    app = Datasette([], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/plugins.json")
        assert 200 == response.status_code
        installed_plugins = {p["name"] for p in response.json()}
        assert "datasette-graphql" in installed_plugins


@pytest.mark.asyncio
async def test_graphiql():
    app = Datasette([], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/graphql")
        assert 200 == response.status_code
        assert "<title>GraphiQL</title>" in response.text


@pytest.mark.asyncio
async def test_query_fields(ds):
    query = """
    {
        __schema {
            queryType {
                fields {
                    name
                }
            }
        }
    }
    """
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post("http://localhost/graphql", json={"query": query})
        assert response.status_code == 200
        fields = {
            f["name"]
            for f in response.json()["data"]["__schema"]["queryType"]["fields"]
        }
        assert fields == {
            "images_get",
            "images",
            "issues_get",
            "issues",
            "licenses_get",
            "licenses",
            "repos_get",
            "repos",
            "table_with_compound_pk_get",
            "table_with_compound_pk",
            "table_with_pk_get",
            "table_with_pk",
            "table_with_rowid_get",
            "table_with_rowid",
            "users_get",
            "users",
            "view_on_table_with_pk_get",
            "view_on_table_with_pk",
        }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,expected_errors",
    [
        # Search fails on table that doesn't support it
        (
            """{
                users(search:"cleopaws") {
                    nodes {
                        name
                    }
                }
            }""",
            [
                {
                    "message": 'Unknown argument "search" on field "users" of type "Query".',
                    "locations": [{"line": 2, "column": 23}],
                }
            ],
        ),
    ],
)
async def test_graphql_errors(ds, query, expected_errors):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post("http://localhost/graphql", json={"query": query})
        assert response.status_code == 500
        assert response.json()["errors"] == expected_errors


_graphql_re = re.compile(r"```graphql(.*?)```", re.DOTALL)
_json_re = re.compile(r"```json\n(.*?)```", re.DOTALL)
_variables_re = re.compile(r"```json\+variables\n(.*?)```", re.DOTALL)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", (pathlib.Path(__file__).parent.parent / "examples").glob("*.md")
)
async def test_graphql_examples(ds, path):
    content = path.read_text()
    query = _graphql_re.search(content)[1]
    try:
        variables = _variables_re.search(content)[1]
    except TypeError:
        variables = "{}"
    expected = json.loads(_json_re.search(content)[1])
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post(
            "http://localhost/graphql",
            json={"query": query, "variables": json.loads(variables),},
        )
        assert response.status_code == 200, response.json()
        if response.json()["data"] != expected:
            print("Actual:")
            print(json.dumps(response.json()["data"], indent=4))
        assert response.json()["data"] == expected


@pytest.mark.asyncio
async def test_graphql_error(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post(
            "http://localhost/graphql",
            json={
                "query": """{
                    users {
                        nodes {
                            nam2
                            score
                        }
                    }
                }"""
            },
        )
        assert response.status_code == 500
        assert response.json() == {
            "data": None,
            "errors": [
                {
                    "message": 'Cannot query field "nam2" on type "users". Did you mean "name"?',
                    "locations": [{"line": 4, "column": 29}],
                }
            ],
        }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "on,expected",
    [
        (
            True,
            {
                "repos": {
                    "nodes": [
                        {"id": 1, "fullName": "simonw/datasette"},
                        {"id": 2, "fullName": "cleopaws/dogspotter"},
                    ]
                }
            },
        ),
        (
            False,
            {
                "repos": {
                    "nodes": [
                        {"id": 1, "full_name": "simonw/datasette"},
                        {"id": 2, "full_name": "cleopaws/dogspotter"},
                    ]
                }
            },
        ),
    ],
)
async def test_graphql_auto_camelcase(db_path, on, expected):
    ds = Datasette(
        [db_path], metadata={"plugins": {"datasette-graphql": {"auto_camelcase": on}}}
    )
    query = """
    {
        repos {
            nodes {
                id
                NAME
            }
        }
    }
    """.replace(
        "NAME", "fullName" if on else "full_name"
    )
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post("http://localhost/graphql", json={"query": query})
        assert response.status_code == 200
        assert response.json() == {"data": expected}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "table", ["table_with_pk", "table_with_rowid", "table_with_compound_pk"]
)
async def test_graphql_auto_camelcase(ds, table):
    # Every table should have 21 items, so should paginate 3 times
    after = None
    names_from_nodes = []
    names_from_edges = []
    while True:
        args = ["first: 10"]
        if after:
            args.append('after: "{}"'.format(after))
        query = """
        {
            TABLE(ARGS) {
                totalCount
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    name
                }
                edges {
                    node {
                        name
                    }
                }
            }
        }
        """.replace(
            "TABLE", table
        ).replace(
            "ARGS", ", ".join(args)
        )
        async with httpx.AsyncClient(app=ds.app()) as client:
            response = await client.post(
                "http://localhost/graphql", json={"query": query}
            )
            assert response.status_code == 200
            data = response.json()["data"]
            names_from_nodes.extend([n["name"] for n in data[table]["nodes"]])
            names_from_edges.extend([e["node"]["name"] for e in data[table]["edges"]])
            after = data[table]["pageInfo"]["endCursor"]
            assert data[table]["pageInfo"]["hasNextPage"] == bool(after)
            assert data[table]["totalCount"] == 21
            if not after:
                break
    assert len(names_from_nodes) == 21
    assert len(names_from_edges) == 21
    assert len(set(names_from_nodes)) == 21
    assert len(set(names_from_edges)) == 21


@pytest.mark.asyncio
async def test_graphql_multiple_databases(db_path, db_path2):
    ds = Datasette([db_path, db_path2])
    query = """
    {
        test {
            nodes {
                body
            }
        }
    }
    """
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post(
            "http://localhost/graphql/test2", json={"query": query}
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "data": {"test": {"nodes": [{"body": "This is test two"}]}}
        }


@pytest.mark.asyncio
@pytest.mark.parametrize("cors_enabled", [True, False])
async def test_cors_headers(db_path, cors_enabled):
    ds = Datasette([db_path], cors=cors_enabled,)
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.options("http://localhost/graphql")
        assert response.status_code == 200
        desired_headers = {
            "access-control-allow-headers": "content-type",
            "access-control-allow-method": "POST",
            "access-control-allow-origin": "*",
        }.items()
        if cors_enabled:
            assert desired_headers <= dict(response.headers).items()
        else:
            assert not desired_headers <= dict(response.headers).items()
