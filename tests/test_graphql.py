from datasette.app import Datasette
import pytest
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
@pytest.mark.parametrize(
    "query,expected,errors",
    [
        (
            """{
                users {
                    nodes {
                        name
                        points
                        score
                    }
                }
            }""",
            {
                "users": {
                    "nodes": [
                        {"name": "cleopaws", "points": 5, "score": 51.5},
                        {"name": "simonw", "points": 3, "score": 35.2},
                    ]
                }
            },
            None,
        ),
        # Nested query with foreign keys
        (
            """{
                issues {
                    nodes {
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
                }
            }""",
            {
                "issues": {
                    "nodes": [
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
                }
            },
            None,
        ),
        # Nullable foreign key
        (
            """{
                repos {
                    nodes {
                        name
                        license {
                            key
                            name
                        }
                    }
                }
            }""",
            {
                "repos": {
                    "nodes": [
                        {
                            "name": "datasette",
                            "license": {"key": "apache2", "name": "Apache 2"},
                        },
                        {
                            "name": "dogspotter",
                            "license": {"key": "mit", "name": "MIT"},
                        },
                        {"name": "private", "license": None},
                    ]
                }
            },
            None,
        ),
        # Filters
        (
            """{
                users(filters:["score__gt=50"]) {
                    nodes {
                        name
                        score
                    }
                }
            }""",
            {"users": {"nodes": [{"name": "cleopaws", "score": 51.5}]}},
            None,
        ),
        # Search
        (
            """{
                repos(search:"cleopaws") {
                    nodes {
                        full_name
                    }
                }
            }""",
            {"repos": {"nodes": [{"full_name": "cleopaws/dogspotter"}]}},
            None,
        ),
        # Search fails on table that doesn't support it
        (
            """{
                users(search:"cleopaws") {
                    nodes {
                        name
                    }
                }
            }""",
            None,
            [
                {
                    "message": 'Unknown argument "search" on field "users" of type "Query".',
                    "locations": [{"line": 2, "column": 23}],
                }
            ],
        ),
        # sort
        (
            """{
                users(sort: points) {
                    nodes {
                        name
                        points
                    }
                }
            }""",
            {
                "users": {
                    "nodes": [
                        {"name": "simonw", "points": 3},
                        {"name": "cleopaws", "points": 5},
                    ]
                }
            },
            None,
        ),
        # sort_desc
        (
            """{
                users(sort_desc: points) {
                    nodes {
                        name
                        points
                    }
                }
            }""",
            {
                "users": {
                    "nodes": [
                        {"name": "cleopaws", "points": 5},
                        {"name": "simonw", "points": 3},
                    ]
                }
            },
            None,
        ),
        # SQL view
        (
            """{
                view_on_paginate_by_pk(first: 3) {
                    nodes {
                        pk
                        name
                    }
                }
            }""",
            {
                "view_on_paginate_by_pk": {
                    "nodes": [
                        {"pk": 1, "name": "Row 1"},
                        {"pk": 2, "name": "Row 2"},
                        {"pk": 3, "name": "Row 3"},
                    ]
                }
            },
            None,
        ),
    ],
)
async def test_graphql_query(ds, query, expected, errors):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post("http://localhost/graphql", json={"query": query})
        if errors:
            assert response.status_code == 500
            assert response.json()["errors"] == errors
        else:
            assert response.status_code == 200
        assert response.json()["data"] == expected


@pytest.mark.asyncio
async def test_graphql_variables(ds):
    query = """
    query specific_repo($filter: String) {
        repos(filters:[$filter]) {
            nodes {
                name
                license {
                    key
                }
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
            "data": {
                "repos": {
                    "nodes": [{"name": "datasette", "license": {"key": "apache2"}}]
                }
            }
        }


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
    "table", ["paginate_by_pk", "paginate_by_rowid", "paginate_by_compound_pk"]
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
    ds = Datasette(
        [db_path],
        metadata={"plugins": {"datasette-graphql": {"disable_cors": not cors_enabled}}},
    )
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
