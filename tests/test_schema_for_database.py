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
        dogs {
            name
            age
        }
    }"""

    result = await graphql(
        schema, query, executor=AsyncioExecutor(), return_promise=True
    )
    assert result.data == {
        "dogs": [{"name": "Cleo", "age": "5"}, {"name": "Pancakes", "age": "4"}]
    }
