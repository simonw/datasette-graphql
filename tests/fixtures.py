from datasette.app import Datasette
import pytest
import sqlite_utils


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    db["users"].insert_all(
        [
            {"id": 1, "name": "cleopaws", "points": 5, "score": 51.5},
            {"id": 2, "name": "simonw", "points": 3, "score": 35.2},
        ],
        pk="id",
    )
    db["licenses"].insert_all(
        [{"key": "mit", "name": "MIT"}, {"key": "apache2", "name": "Apache 2"},],
        pk="key",
    )
    db["repos"].insert_all(
        [
            {
                "id": 1,
                "full_name": "simonw/datasette",
                "name": "datasette",
                "owner": 2,
                "license": "apache2",
            },
            {
                "id": 2,
                "full_name": "cleopaws/dogspotter",
                "name": "dogspotter",
                "owner": 1,
                "license": "mit",
            },
        ],
        pk="id",
        foreign_keys=(("owner", "users"), ("license", "licenses")),
    )
    db["issues"].insert_all(
        [{"id": 111, "title": "Not enough dog stuff", "user": 1, "repo": 1}],
        pk="id",
        foreign_keys=("user", "repo"),
    )
    return db_path


@pytest.fixture(scope="session")
def ds(db_path):
    return Datasette([db_path])
