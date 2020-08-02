from datasette.app import Datasette
from datasette_graphql.utils import schema_for_database
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql import graphql
import pytest
from .fixtures import ds, db_path


@pytest.mark.asyncio
async def test_schema(ds):
    schema = await schema_for_database(ds)

    query = """{
        users {
            name
            points
            score
        }
    }"""

    result = await graphql(
        schema, query, executor=AsyncioExecutor(), return_promise=True
    )
    assert result.data == {
        "users": [
            {"name": "cleopaws", "points": 5, "score": 51.5},
            {"name": "simonw", "points": 3, "score": 35.2},
        ]
    }
