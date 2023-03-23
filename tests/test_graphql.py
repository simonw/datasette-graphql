from datasette.app import Datasette
from datasette_graphql.utils import _schema_cache
import json
import pathlib
import pytest
import re
import urllib
import textwrap
from .fixtures import ds, db_path, db_path2

graphql_re = re.compile(r"```graphql(.*?)```", re.DOTALL)
json_re = re.compile(r"```json\n(.*?)```", re.DOTALL)
variables_re = re.compile(r"```json\+variables\n(.*?)```", re.DOTALL)
whitespace_re = re.compile(r"\s+")


def equal_no_whitespace(s1, s2):
    return whitespace_re.sub("", s1) == whitespace_re.sub("", s2)


@pytest.mark.asyncio
async def test_plugin_is_installed():
    ds = Datasette([], memory=True)
    response = await ds.client.get("/-/plugins.json")
    assert 200 == response.status_code
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-graphql" in installed_plugins


@pytest.mark.asyncio
async def test_menu():
    ds = Datasette([], memory=True)
    response = await ds.client.get("/")
    assert 200 == response.status_code
    assert '<li><a href="/graphql">GraphQL API</a></li>' in response.text


@pytest.mark.asyncio
async def test_graphiql():
    ds = Datasette([], memory=True)
    response = await ds.client.get("/graphql", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert "<title>GraphiQL</title>" in response.text
    # Check that bundled assets are all present
    paths = []
    paths.extend(re.findall(r'<link href="(.*?)"', response.text))
    paths.extend(re.findall(r'<script src="(.*?)"', response.text))
    # Check that those paths are all 200s
    for path in paths:
        assert path.startswith("/-/static-plugins/datasette_graphql/")
        response2 = await ds.client.get(path)
        assert response2.status_code == 200
    # Check that react/react-dom/grapihql are in order
    filenames_and_extensions = [
        (path.split("/")[-1].split(".")[0], path.split("/")[-1].split(".")[-1])
        for path in paths
    ]
    assert filenames_and_extensions == [
        ("graphiql", "css"),
        ("react", "js"),
        ("react-dom", "js"),
        ("graphiql", "js"),
    ]


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
    response = await ds.client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    fields = {
        f["name"] for f in response.json()["data"]["__schema"]["queryType"]["fields"]
    }
    assert fields == {
        "_1_images_row",
        "_1_images",
        "t_table_",
        "t_table__row",
        "issues_row",
        "issues",
        "licenses_row",
        "licenses",
        "repos_row",
        "repos",
        "table_with_compound_pk_row",
        "table_with_compound_pk",
        "table_with_pk_row",
        "table_with_pk",
        "table_with_rowid_row",
        "table_with_rowid",
        "type_compound_key",
        "type_compound_key_row",
        "table_with_reserved_columns",
        "table_with_reserved_columns_row",
        "users_row",
        "users",
        "view_on_table_with_pk_row",
        "view_on_table_with_pk",
        "view_on_repos_row",
        "view_on_repos",
        "bad_foreign_key",
        "bad_foreign_key_row",
        "table_with_dangerous_columns",
        "table_with_dangerous_columns_row",
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
                    "message": "Unknown argument 'search' on field 'Query.users'.",
                    "locations": [{"line": 2, "column": 23}],
                }
            ],
        ),
    ],
)
async def test_graphql_errors(ds, query, expected_errors):
    response = await ds.client.post("/graphql", json={"query": query})
    assert response.status_code == 500
    assert response.json()["errors"] == expected_errors


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", (pathlib.Path(__file__).parent.parent / "examples").glob("*.md")
)
async def test_graphql_examples(ds, path):
    content = path.read_text()
    query = graphql_re.search(content)[1]
    try:
        variables = variables_re.search(content)[1]
    except TypeError:
        variables = "{}"
    expected = json.loads(json_re.search(content)[1])
    response = await ds.client.post(
        "/graphql",
        json={
            "query": query,
            "variables": json.loads(variables),
        },
    )
    assert response.status_code == 200, response.json()
    if response.json()["data"] != expected:
        print("Actual:")
        print(json.dumps(response.json()["data"], indent=4))
    assert response.json()["data"] == expected


@pytest.mark.asyncio
async def test_graphql_error(ds):
    response = await ds.client.post(
        "/graphql",
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
                "message": "Cannot query field 'nam2' on type 'users'. Did you mean 'name'?",
                "locations": [{"line": 4, "column": 25}],
            }
        ],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "on,expected",
    [
        (True, {"testTable": {"nodes": [{"fullName": "This is a full name"}]}}),
        (False, {"test_table": {"nodes": [{"full_name": "This is a full name"}]}}),
    ],
)
async def test_graphql_auto_camelcase(db_path2, on, expected):
    _schema_cache.clear()
    ds = Datasette(
        [str(db_path2)],
        metadata={"plugins": {"datasette-graphql": {"auto_camelcase": on}}},
    )
    query = """
    {
        TABLE {
            nodes {
                NAME
            }
        }
    }
    """.replace(
        "NAME", "fullName" if on else "full_name"
    ).replace(
        "TABLE", "testTable" if on else "test_table"
    )
    response = await ds.client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert response.json() == {"data": expected}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "table", ["table_with_pk", "table_with_rowid", "table_with_compound_pk"]
)
async def test_graphql_pagination(ds, table):
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
        response = await ds.client.post("/graphql", json={"query": query})
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
    ds = Datasette([str(db_path), str(db_path2)])
    query = """
    {
        test_table {
            nodes {
                full_name
            }
        }
    }
    """
    response = await ds.client.post("/graphql/test2", json={"query": query})
    assert response.status_code == 200, response.json()
    assert response.json() == {
        "data": {"test_table": {"nodes": [{"full_name": "This is a full name"}]}}
    }


@pytest.mark.asyncio
async def test_graphql_json_columns(db_path):
    _schema_cache.clear()
    ds = Datasette(
        [str(db_path)],
        metadata={
            "databases": {
                "test": {
                    "tables": {
                        "repos": {
                            "plugins": {"datasette-graphql": {"json_columns": ["tags"]}}
                        }
                    }
                }
            }
        },
    )
    query = """
    {
        repos {
            nodes {
                full_name
                tags
            }
        }
    }
    """
    response = await ds.client.post("/graphql", json={"query": query})
    assert response.status_code == 200, response.json()
    assert response.json() == {
        "data": {
            "repos": {
                "nodes": [
                    {
                        "full_name": "simonw/datasette",
                        "tags": ["databases", "apis"],
                    },
                    {"full_name": "cleopaws/dogspotter", "tags": ["dogs"]},
                    {"full_name": "simonw/private", "tags": []},
                ]
            }
        }
    }


@pytest.mark.asyncio
async def test_graphql_output_schema(ds):
    response = await ds.client.options("/graphql/test.graphql")
    assert response.status_code == 200
    bad = []
    for fragment in (
        "type Query {",
        "input IntegerOperations {",
        "users(\n",
        "filter: [usersFilter]",
        "): usersCollection",
        "users_row(\n",
        "type _1_images {",
        "type _1_imagesCollection {",
        "type _1_imagesEdge {",
        "input _1_imagesFilter {",
        "enum _1_imagesSort {",
        "enum _1_imagesSortDesc {",
    ):
        if fragment not in response.text:
            bad.append(fragment)
    assert not bad, bad


@pytest.mark.asyncio
@pytest.mark.parametrize("cors_enabled", [True, False])
async def test_cors_headers(db_path, cors_enabled):
    ds = Datasette(
        [str(db_path)],
        cors=cors_enabled,
    )
    response = await ds.client.options("/graphql")
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation_name,expected_status,expected_data",
    [
        ("Q1", 200, {"data": {"users_row": {"name": "cleopaws"}}}),
        ("Q2", 200, {"data": {"users_row": {"id": 1}}}),
        (
            "",
            500,
            {"data": None, "errors": [{"message": "Unknown operation named ''."}]},
        ),
    ],
)
async def test_operation_name(ds, operation_name, expected_status, expected_data):
    query = """
    query Q1 {
        users_row {
            name
        }
    }
    query Q2 {
        users_row {
            id
        }
    }
    """
    response = await ds.client.post(
        "/graphql",
        json={"query": query, "operationName": operation_name},
    )
    assert response.status_code == expected_status, response.json()
    assert response.json() == expected_data


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,extra_query_string,expected_data",
    [
        # Regular query
        (
            """
            {
                users_row {
                    name
                }
            }
            """,
            {},
            {"data": {"users_row": {"name": "cleopaws"}}},
        ),
        # operationName
        (
            """
            query Q1 {
                users_row {
                    name
                }
            }
            query Q2 {
                users_row {
                    id
                }
            }
            """,
            {"operationName": "Q2"},
            {"data": {"users_row": {"id": 1}}},
        ),
        # variables
        (
            """
            query specific_repo($name: String) {
                repos(filter: {name: {eq: $name}}) {
                    nodes {
                        name
                    }
                }
            }
            """,
            {"variables": json.dumps({"name": "datasette"})},
            {"data": {"repos": {"nodes": [{"name": "datasette"}]}}},
        ),
    ],
)
async def test_graphql_http_get(ds, query, extra_query_string, expected_data):
    params = dict(extra_query_string)
    params["query"] = query
    response = await ds.client.get("/graphql", params=params)
    assert response.status_code == 200
    assert response.json() == expected_data


@pytest.mark.asyncio
async def test_configured_fts_search_for_view(db_path):
    _schema_cache.clear()
    ds = Datasette(
        [str(db_path)],
        metadata={
            "databases": {
                "test": {
                    "tables": {
                        "view_on_repos": {"fts_table": "repos_fts", "fts_pk": "id"}
                    }
                }
            }
        },
    )
    query = """
    {
        view_on_repos(search: "dogspotter") {
            nodes {
                id
                full_name
            }
        }
    }
    """
    response = await ds.client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "view_on_repos": {"nodes": [{"id": 2, "full_name": "cleopaws/dogspotter"}]}
        }
    }
    _schema_cache.clear()


@pytest.mark.asyncio
async def test_time_limit_ms(db_path):
    ds = Datasette(
        [str(db_path)],
        metadata={"plugins": {"datasette-graphql": {"time_limit_ms": 0.1}}},
    )
    query = """
    {
        repos(search: "dogspotter") {
            nodes {
                id
                full_name
            }
        }
    }
    """
    response = await ds.client.post("/graphql", json={"query": query})
    assert response.status_code == 500
    response_json = response.json()
    assert response_json["data"] == {"repos": None}
    assert len(response_json["errors"]) == 1
    assert response_json["errors"][0]["message"].startswith("Time limit exceeded: ")
    assert response_json["errors"][0]["message"].endswith(
        " > 0.1ms - /test/repos.json?_nofacet=1&_size=10&_search=dogspotter"
    )


@pytest.mark.asyncio
async def test_num_queries_limit(db_path):
    ds = Datasette(
        [str(db_path)],
        metadata={"plugins": {"datasette-graphql": {"num_queries_limit": 2}}},
    )
    query = """
    {
        users {
            nodes {
                id
                name
                repos_list {
                    nodes {
                        full_name
                    }
                }
            }
        }
    }
    """
    response = await ds.client.post("/graphql", json={"query": query})
    assert response.status_code == 500
    data_and_errors = response.json()
    data = data_and_errors["data"]
    errors = data_and_errors["errors"]
    users = data["users"]["nodes"]
    # One of the two users should have an empty repos_list
    assert (users[0]["repos_list"] is None) or (users[1]["repos_list"] is None)
    # Errors should say query limit was exceeded
    assert len(errors) == 1
    assert errors[0]["message"].startswith("Query limit exceeded: 3 > 2 - ")


@pytest.mark.asyncio
async def test_time_limits_0(db_path):
    ds = Datasette(
        [str(db_path)],
        metadata={
            "plugins": {
                "datasette-graphql": {"num_queries_limit": 0, "time_limit_ms": 0}
            }
        },
    )
    query = """
    {
        users {
            nodes {
                id
                name
                repos_list {
                    nodes {
                        full_name
                    }
                }
            }
        }
    }
    """
    response = await ds.client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "users": {
                "nodes": [
                    {
                        "id": 1,
                        "name": "cleopaws",
                        "repos_list": {"nodes": [{"full_name": "cleopaws/dogspotter"}]},
                    },
                    {
                        "id": 2,
                        "name": "simonw",
                        "repos_list": {
                            "nodes": [
                                {"full_name": "simonw/datasette"},
                                {"full_name": "simonw/private"},
                            ]
                        },
                    },
                ]
            }
        }
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "metadata,expected",
    [
        (
            # Disallow all access to both authenticated and anonymous users
            {"allow": False},
            [
                # Authenticated?, Path, Expected status code
                (False, "/graphql", 403),
                (False, "/graphql/test", 403),
                (False, "/graphql/test.graphql", 403),
                (False, "/graphql/test2", 403),
                (False, "/graphql/test2.graphql", 403),
                (True, "/graphql", 403),
                (True, "/graphql/test", 403),
                (True, "/graphql/test.graphql", 403),
                (True, "/graphql/test2", 403),
                (True, "/graphql/test2.graphql", 403),
            ],
        ),
        (
            # Allow access to test, protect test2
            {"databases": {"test2": {"allow": {"id": "user"}}}},
            [
                # Authenticated?, Path, Expected status code
                (False, "/graphql", 200),
                (False, "/graphql/test", 200),
                (False, "/graphql/test.graphql", 200),
                (False, "/graphql/test2", 403),
                (False, "/graphql/test2.graphql", 403),
                (True, "/graphql", 200),
                (True, "/graphql/test", 200),
                (True, "/graphql/test.graphql", 200),
                (True, "/graphql/test2", 200),
                (True, "/graphql/test2.graphql", 200),
            ],
        ),
        (
            # Forbid database instance access, but allow access to test2
            {"allow": False, "databases": {"test2": {"allow": True}}},
            [
                # Authenticated?, Path, Expected status code
                (False, "/graphql", 403),
                (False, "/graphql/test", 403),
                (False, "/graphql/test.graphql", 403),
                (False, "/graphql/test2", 200),
                (False, "/graphql/test2.graphql", 200),
                (True, "/graphql", 403),
                (True, "/graphql/test", 403),
                (True, "/graphql/test.graphql", 403),
                (True, "/graphql/test2", 200),
                (True, "/graphql/test2.graphql", 200),
            ],
        ),
    ],
)
async def test_permissions(db_path, db_path2, metadata, expected):
    ds = Datasette([db_path, db_path2], metadata=metadata)
    for authenticated, path, expected_status in expected:
        ds._permission_checks.clear()
        cookies = {}
        if authenticated:
            cookies["ds_actor"] = ds.sign({"a": {"id": "user"}}, "actor")
        response = await ds.client.get(
            path,
            cookies=cookies,
            headers={"Accept": "text/html"},
        )
        assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_no_error_on_empty_schema():
    # https://github.com/simonw/datasette-graphql/issues/64
    ds = Datasette([], memory=True)
    response = await ds.client.get("/graphql", headers={"Accept": "text/html"})
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "table,graphql_table,columns",
    (
        (
            "repos",
            "repos",
            "id full_name name tags owner { id name } license { _key name }",
        ),
        (
            "_csv_progress_",
            "t_csv_progress_",
            "id filename bytes_todo bytes_done rows_done started completed error",
        ),
    ),
)
async def test_table_action(db_path, table, graphql_table, columns):
    ds = Datasette([str(db_path)])
    db = ds.get_database("test")
    await db.execute_write(
        """
        CREATE TABLE IF NOT EXISTS [_csv_progress_] (
            [id] TEXT PRIMARY KEY,
            [filename] TEXT,
            [bytes_todo] INTEGER,
            [bytes_done] INTEGER,
            [rows_done] INTEGER,
            [started] TEXT,
            [completed] TEXT,
            [error] TEXT
        )"""
    )
    response = await ds.client.get("/test/{}".format(table))
    html = response.text
    prefix = '<li><a href="/graphql/test?query='
    assert prefix in html
    example_query = html.split(prefix)[1].split('">')[0]
    assert equal_no_whitespace(
        urllib.parse.unquote(example_query),
        textwrap.dedent(
            """
        {
          TABLE {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              COLUMNS
            }
          }
        }
        """.replace(
                "TABLE", graphql_table
            ).replace(
                "COLUMNS", columns
            )
        ),
    )


@pytest.mark.asyncio
async def test_graphql_reserved_column_names(ds):
    response = await ds.client.post(
        "/graphql",
        json={
            "query": """{
                table_with_reserved_columns {
                    nodes {
                        id
                        if_
                        description_
                    }
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "table_with_reserved_columns": {
                "nodes": [
                    {"id": 1, "if_": "keyword if", "description_": "a description"}
                ]
            }
        }
    }


@pytest.mark.asyncio
async def test_graphql_dangerous_column_names(ds):
    response = await ds.client.post(
        "/graphql",
        json={
            "query": """{
                table_with_dangerous_columns {
                    nodes {
                        _0_Starts_With_Hash
                        _0_double_underscore
                    }
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "table_with_dangerous_columns": {
                "nodes": [{"_0_Starts_With_Hash": 2, "_0_double_underscore": 3}]
            }
        }
    }


@pytest.mark.asyncio
async def test_bad_foreign_keys(ds):
    # https://github.com/simonw/datasette-graphql/issues/79
    response = await ds.client.post(
        "/graphql",
        json={
            "query": """{
                bad_foreign_key {
                    nodes {
                        fk
                    }
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"bad_foreign_key": {"nodes": [{"fk": 1}]}}}


@pytest.mark.asyncio
async def test_alternative_graphql():
    graphql_path = "/-/graphql"
    ds = Datasette(
        [],
        memory=True,
        metadata={
            "plugins": {
                "datasette-graphql": {
                    "path": graphql_path,
                }
            }
        },
    )
    # First check for menu
    response = await ds.client.get("/")
    if graphql_path is None:
        assert "GraphQL API" not in response.text
    else:
        assert (
            '<li><a href="{}">GraphQL API</a></li>'.format(graphql_path)
            in response.text
        )
    # Now check for direct access
    if graphql_path is None:
        response = await ds.client.get("/graphql")
        assert response.status_code == 404
    else:
        response = await ds.client.get(graphql_path, headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert "GraphiQL" in response.text
