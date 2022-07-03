import pathlib
import pytest
import re
import urllib
from .test_graphql import graphql_re, variables_re

link_re = re.compile(r"\[Try this query]\((.*?)\)")


@pytest.mark.parametrize(
    "path",
    list((pathlib.Path(__file__).parent.parent / "examples").glob("*.md"))
    + [pathlib.Path(__file__).parent.parent / "README.md"],
)
def test_examples_link_to_live_demo(request, path):
    should_rewrite = request.config.getoption("--rewrite-examples")
    is_readme = path.name == "README.md"
    content = path.read_text()
    ideal_content = content
    variables = None
    if not is_readme:
        try:
            variables = variables_re.search(content)[1]
        except TypeError:
            pass

    for match in graphql_re.finditer(content):
        query = match.group(1)
        if "packages {" in query:
            # Skip the example illustrating the packages plugin
            continue
        start = match.start()
        end = match.end()
        args = {"query": query}
        if variables:
            args["variables"] = variables
        expected_url = (
            "https://datasette-graphql-demo.datasette.io/graphql{}?{}".format(
                "" if is_readme else "/fixtures",
                urllib.parse.urlencode(args, quote_via=urllib.parse.quote),
            )
        )
        fixed_fragment = "```graphql\n{}\n```\n[Try this query]({})\n".format(
            query.strip(), expected_url
        )
        # Check for the `[Try this query ...]` that follows this one character later
        try_this_match = link_re.search(content, start)
        if try_this_match is None or try_this_match.start() - end != 1:
            if should_rewrite:
                query_fix_re = re.compile(
                    r"```graphql\n{}\n```\n".format(re.escape(query.strip()))
                )
                ideal_content = query_fix_re.sub(fixed_fragment, ideal_content)
            else:
                assert (
                    False
                ), "{}: [Try this query] link should follow {}\n\nFix with pytest --rewrite-examples'".format(
                    path, query
                )
        else:
            # The link is there! But does it have the correct URL?
            if expected_url != try_this_match.group(1):
                if should_rewrite:
                    query_link_fix_re = re.compile(
                        r"```graphql\n{}\n```\n\[Try this query]\((.*?)\)".format(
                            re.escape(query.strip())
                        )
                    )
                    ideal_content = query_link_fix_re.sub(fixed_fragment, ideal_content)
                else:
                    assert (
                        False
                    ), "{}: Expected URL {} for {}\n\nFix with pytest --rewrite-examples'".format(
                        path, expected_url, query
                    )

    if should_rewrite and ideal_content != content:
        path.write_text(ideal_content)
