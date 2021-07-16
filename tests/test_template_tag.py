from datasette.app import Datasette
import pytest
from .fixtures import db_path

TEMPLATE = r'''
{% set users = graphql("""
{
    users {
        nodes {
            name
            points
            score
        }
    }
}
""")["users"] %}
{% for user in users.nodes %}
    <p>{{ user.name }} - points: {{ user.points }}, score = {{ user.score }}</p>
{% endfor %}
'''

TEMPLATE_WITH_VARS = r'''
{% set user = graphql("""
query ($id: Int) {
    users_row(id: $id) {
        id
        name
    }
}
""", variables={"id": 2})["users_row"] %}
<p>{{ user.id }}: {{ user.name }}</p>
'''


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "template,expected",
    [
        (
            TEMPLATE,
            "<p>cleopaws - points: 5, score = 51.5</p>\n\n"
            "    <p>simonw - points: 3, score = 35.2</p>",
        ),
        (TEMPLATE_WITH_VARS, "<p>2: simonw</p>"),
    ],
)
async def test_schema_caching(tmp_path_factory, db_path, template, expected):
    template_dir = tmp_path_factory.mktemp("templates")
    pages_dir = template_dir / "pages"
    pages_dir.mkdir()
    (pages_dir / "about.html").write_text(template)

    ds = Datasette([str(db_path)], template_dir=template_dir)
    response = await ds.client.get("/about")
    assert response.status_code == 200
    assert response.text.strip() == expected
