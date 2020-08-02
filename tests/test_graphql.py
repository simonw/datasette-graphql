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
        assert response.json() == {
            "dogs": [{"name": "Cleo", "age": "5"}, {"name": "Pancakes", "age": "4"}]
        }
