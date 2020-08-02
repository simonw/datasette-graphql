from datasette.app import Datasette
import pytest
import sqlite_utils


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    db["dogs"].insert_all(
        [
            {"id": 1, "name": "Cleo", "age": 5, "weight": 51.5},
            {"id": 2, "name": "Pancakes", "age": 4, "weight": 35.2},
        ],
        pk="id",
    )
    return db_path


@pytest.fixture(scope="session")
def ds(db_path):
    return Datasette([db_path])
