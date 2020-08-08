from datasette.app import Datasette
import pytest
import sqlite_utils

GIF_1x1 = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01D\x00;"


def build_database(db):
    db["users"].insert_all(
        [
            {
                "id": 1,
                "name": "cleopaws",
                "points": 5,
                "score": 51.5,
                "joined": "2018-11-04 00:05:23",
                "dog_award": "3rd best mutt",
            },
            {
                "id": 2,
                "name": "simonw",
                "points": 3,
                "score": 35.2,
                "joined": "2019-04-03 12:35:11",
                "dog_award": None,
            },
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
                "tags": ["databases", "apis"],
            },
            {
                "id": 2,
                "full_name": "cleopaws/dogspotter",
                "name": "dogspotter",
                "owner": 1,
                "license": "mit",
                "tags": ["dogs"],
            },
            {
                "id": 3,
                "full_name": "simonw/private",
                "name": "private",
                "owner": 2,
                "license": None,
                "tags": [],
            },
        ],
        pk="id",
        foreign_keys=(("owner", "users"), ("license", "licenses")),
    ).enable_fts(["full_name"], fts_version="FTS4")
    db["issues"].insert_all(
        [{"id": 111, "title": "Not enough dog stuff", "user": 1, "repo": 1}],
        pk="id",
        foreign_keys=("user", "repo"),
    )
    db["images"].insert({"path": "1x1.gif", "content": GIF_1x1}, pk="path")
    # To test pagination with both rowid, single-pk and compound-pk tables:
    db["table_with_rowid"].insert_all(
        [{"name": "Row {}".format(i)} for i in range(1, 22)]
    )
    db["table_with_pk"].insert_all(
        [{"pk": i, "name": "Row {}".format(i)} for i in range(1, 22)], pk="pk"
    )
    db["table_with_compound_pk"].insert_all(
        [
            {"pk1": i, "pk2": j, "name": "Row {} {}".format(i, j)}
            for i in range(1, 4)
            for j in range(1, 8)
        ],
        pk=("pk1", "pk2"),
    )
    db.create_view("view_on_table_with_pk", "select * from table_with_pk")


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    build_database(db)
    return db_path


@pytest.fixture(scope="session")
def db_path2(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test2.db"
    db = sqlite_utils.Database(db_path)
    db["test"].insert({"body": "This is test two"})
    return db_path


@pytest.fixture(scope="session")
def ds(db_path):
    return Datasette([db_path])


if __name__ == "__main__":
    import sys

    if not sys.argv[-1].endswith(".db"):
        print("Usage: python fixtures.py fixtures.db")
        sys.exit(1)

    db = sqlite_utils.Database(sys.argv[-1])
    build_database(db)
    print("Data written to {}".format(sys.argv[-1]))
