from datasette.app import Datasette
import pytest
import httpx
from .fixtures import ds, db_path


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
@pytest.mark.parametrize(
    "query,expected",
    [
        (
            """{
                users {
                    name
                    points
                    score
                }
            }""",
            {
                "users": [
                    {"name": "cleopaws", "points": 5, "score": 51.5},
                    {"name": "simonw", "points": 3, "score": 35.2},
                ]
            },
        ),
        # Nested query
        (
            """{
                issues {
                    title
                    user {
                        id
                        name
                    }
                    repo {
                        name
                        license {
                            key
                            name
                        }
                        owner {
                            id
                            name
                        }
                    }
                }
            }""",
            {
                "issues": [
                    {
                        "title": "Not enough dog stuff",
                        "user": {"id": 1, "name": "cleopaws"},
                        "repo": {
                            "name": "datasette",
                            "license": {"key": "apache2", "name": "Apache 2"},
                            "owner": {"id": 2, "name": "simonw"},
                        },
                    }
                ]
            },
        ),
        # Filters
        (
            """{
                users(filters:["score__gt=50"]) {
                    name
                    score
                }
            }""",
            {"users": [{"name": "cleopaws", "score": 51.5}]},
        ),
    ],
)
async def test_graphql_query(ds, query, expected):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post("http://localhost/graphql", json={"query": query},)
        assert response.status_code == 200
        assert response.json() == {"data": expected}


@pytest.mark.asyncio
async def test_graphql_variables(ds):
    query = """
    query specific_repo($filter: String) {
        repos(filters:[$filter]) {
            name
            license {
                key
            }
        }
    }
    """
    variables = {"filter": "name=datasette"}
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post(
            "http://localhost/graphql", json={"query": query, "variables": variables},
        )
        assert response.status_code == 200
        assert response.json() == {
            "data": {"repos": [{"name": "datasette", "license": {"key": "apache2"}}]}
        }


@pytest.mark.asyncio
async def test_graphql_error(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post(
            "http://localhost/graphql",
            json={
                "query": """{
                    users {
                        nam2
                        score
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
                    "locations": [{"line": 3, "column": 25}],
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
                "repos": [
                    {"id": 1, "fullName": "simonw/datasette"},
                    {"id": 2, "fullName": "cleopaws/dogspotter"},
                ]
            },
        ),
        (
            False,
            {
                "repos": [
                    {"id": 1, "full_name": "simonw/datasette"},
                    {"id": 2, "full_name": "cleopaws/dogspotter"},
                ]
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
            id
            NAME
        }
    }
    """.replace(
        "NAME", "fullName" if on else "full_name"
    )
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post("http://localhost/graphql", json={"query": query})
        assert response.status_code == 200
        assert response.json() == {"data": expected}
