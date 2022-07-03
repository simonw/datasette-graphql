from datasette import hookimpl
from datasette.plugins import pm
from datasette.app import Datasette
import graphene
import pytest


@pytest.mark.asyncio
async def test_graphql_extra_fields_hook():
    class InfoPlugin:
        __name__ = "InfoPlugin"

        @hookimpl
        def graphql_extra_fields(self, datasette, database):
            class Info(graphene.ObjectType):
                "Extra information"
                key = graphene.String()
                value = graphene.String()

            async def info_resolver(root, info):
                db = datasette.get_database(database)
                result = await db.execute("select 1 + 1")
                return [
                    {
                        "key": "static",
                        "value": "static",
                    },
                    {
                        "key": "database",
                        "value": database,
                    },
                    {"key": "1+1", "value": result.single_value()},
                ]

            return [
                (
                    "info",
                    graphene.Field(
                        graphene.List(Info),
                        description="List of extra info",
                        resolver=info_resolver,
                    ),
                ),
            ]

    pm.register(InfoPlugin(), name="undo")
    try:
        ds = Datasette([], memory=True)
        response = await ds.client.post(
            "/graphql",
            json={
                "query": """{
                    info {
                        key
                        value
                    }
                }"""
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "data": {
                "info": [
                    {"key": "static", "value": "static"},
                    {"key": "database", "value": "_memory"},
                    {"key": "1+1", "value": "2"},
                ]
            }
        }
    finally:
        pm.unregister(name="undo")
