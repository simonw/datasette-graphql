from datasette_graphql import utils


def test_namer():
    n = utils.Namer()
    for input, expected in (
        ("foo", "foo"),
        ("foo", "foo_2"),
        ("foo", "foo_3"),
        ("bar", "bar"),
        ("bar", "bar_2"),
        ("74_thang", "_74_thang"),
        ("74_thang", "_74_thang_2"),
        ("this has spaces", "this_has_spaces"),
        ("this$and&that", "this_and_that"),
    ):
        assert n.name(input) == expected
