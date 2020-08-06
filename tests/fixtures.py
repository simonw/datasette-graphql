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
            {
                "id": 3,
                "full_name": "simonw/private",
                "name": "private",
                "owner": 2,
                "license": None,
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
    # To test pagination with both rowid, single-pk and compound-pk tables:
    db["paginate_by_rowid"].insert_all(
        [{"name": "Row {}".format(i)} for i in range(1, 22)]
    )
    db["paginate_by_pk"].insert_all(
        [{"pk": i, "name": "Row {}".format(i)} for i in range(1, 22)], pk="pk"
    )
    db["paginate_by_compound_pk"].insert_all(
        [
            {"pk1": i, "pk2": j, "name": "Row {} {}".format(i, j)}
            for i in range(1, 4)
            for j in range(1, 8)
        ],
        pk=("pk1", "pk2"),
    )
    return db_path


@pytest.fixture(scope="session")
def ds(db_path):
    return Datasette([db_path])
