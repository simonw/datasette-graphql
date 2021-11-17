from datasette_graphql.utils import schema_for_database
from graphql import graphql
import pytest
from .fixtures import ds, db_path


@pytest.mark.asyncio
async def test_schema(ds):
    schema = (await schema_for_database(ds)).schema

    query = """{
        users {
            totalCount
            nodes {
                name
                points
                score
            }
        }
    }"""

    result = await schema.execute_async(query)
    assert result.data == {
        "users": {
            "totalCount": 2,
            "nodes": [
                {"name": "cleopaws", "points": 5, "score": 51.5},
                {"name": "simonw", "points": 3, "score": 35.2},
            ],
        }
    }, result.errors
