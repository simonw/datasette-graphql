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
async def test_graphql_view(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post(
            "http://localhost/graphql",
            json={
                "query": """
        { dogs {
            name
            age
        } }
        """
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "data": {
                "dogs": [{"name": "Cleo", "age": "5"}, {"name": "Pancakes", "age": "4"}]
            }
        }


@pytest.mark.asyncio
async def test_graphql_error(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post(
            "http://localhost/graphql",
            json={
                "query": """
        { dogs {
            nam2
            age
        } }
        """
            },
        )
        assert response.status_code == 500
        assert response.json() == {
            "data": None,
            "errors": [
                {
                    "message": 'Cannot query field "nam2" on type "dogs". Did you mean "name"?',
                    "locations": [{"line": 3, "column": 13}],
                }
            ],
        }
