import pathlib
import pytest
import re
import urllib
from .test_graphql import graphql_re, variables_re

link_re = re.compile(r"\[Try this query]\((.*?)\)")


@pytest.mark.parametrize(
    "path", (pathlib.Path(__file__).parent.parent / "examples").glob("*.md")
)
def test_examples_link_to_live_demo(request, path):
    should_rewrite = request.config.getoption("--rewrite-examples")
    content = path.read_text()
    query = graphql_re.search(content)[1]
    try:
        variables = variables_re.search(content)[1]
    except TypeError:
        variables = None
    args = {"query": query}
    if variables:
        args["variables"] = variables
    expected_url = (
        "https://datasette-graphql-demo.datasette.io/graphql/fixtures?"
        + urllib.parse.urlencode(args, quote_via=urllib.parse.quote)
    )
    # Is the link there at all? If not we will need to add it
    link_match = link_re.search(content)
    if link_match is None:
        if should_rewrite:
            ideal_content = graphql_re.sub(
                "```graphql\n{}\n```\n[Try this query]({})\n".format(
                    query.strip(), expected_url
                ),
                content,
            )
            path.write_text(ideal_content)
            return
        else:
            assert (
                link_match is not None
            ), "'Try this query' link is missing from {}, run 'pytest --rewrite-examples' to fix it".format(
                path
            )
    # Does the link contain the correct URL?
    link_url = link_match[1]
    if link_url != expected_url:
        if should_rewrite:
            ideal_content = link_re.sub(
                "[Try this query]({})".format(expected_url), content
            )
            path.write_text(ideal_content)
            return
        else:
            assert (
                link_url == expected_url
            ), "'Try this query' link is incorrect in {}, run 'pytest --rewrite-examples' to fix it".format(
                path
            )
