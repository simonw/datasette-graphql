def pytest_addoption(parser):
    parser.addoption(
        "--rewrite-examples",
        action="store_true",
        default=False,
        help="Rewrite examples/ 'Try this query' links on error",
    )
