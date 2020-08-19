from datasette.app import Datasette
from datasette_graphql.utils import schema_for_database, _schema_cache
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql import graphql
import sqlite_utils
import pytest
from unittest import mock
import httpx
from .fixtures import build_database


@pytest.mark.asyncio
@mock.patch("datasette_graphql.utils.schema_for_database")
async def test_schema_caching(mock_schema_for_database, tmp_path_factory):
    mock_schema_for_database.side_effect = schema_for_database
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "schema.db"
    db = sqlite_utils.Database(db_path)
    build_database(db)

    # Previous tests will have populated the cache
    _schema_cache.clear()

    assert len(_schema_cache) == 0

    # The first hit should call schema_for_database
    assert not mock_schema_for_database.called
    ds = Datasette([db_path])
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/graphql/schema.graphql")
        assert response.status_code == 200
        assert "view_on_table_with_pkSort" in response.text

    assert mock_schema_for_database.called

    assert len(_schema_cache) == 1

    mock_schema_for_database.reset_mock()

    # The secod hit should NOT call it
    assert not mock_schema_for_database.called
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/graphql/schema.graphql")
        assert response.status_code == 200
        assert "view_on_table_with_pkSort" in response.text
        assert "new_table" not in response.text

    assert not mock_schema_for_database.called

    current_keys = set(_schema_cache.keys())
    assert len(current_keys) == 1

    # We change the schema and it should be called again
    db["new_table"].insert({"new_column": 1})

    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/graphql/schema.graphql")
        assert response.status_code == 200
        assert "view_on_table_with_pkSort" in response.text
        assert "new_table" in response.text

    assert mock_schema_for_database.called

    assert len(_schema_cache) == 1
    assert set(_schema_cache.keys()) != current_keys
