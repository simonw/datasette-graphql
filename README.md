# datasette-graphql

[![PyPI](https://img.shields.io/pypi/v/datasette-graphql.svg)](https://pypi.org/project/datasette-graphql/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-graphql?include_prereleases&label=changelog)](https://github.com/simonw/datasette-graphql/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-graphql/blob/master/LICENSE)

A GraphQL endpoint for Datasette

**Work in progress alpha** - this probably isn't worth using yet.

## Installation

Install this plugin in the same environment as Datasette.

    $ pip install datasette-graphql

## Usage

This sets up `/graphql` as a GraphQL endpoint for the first attached database. Individual tables can be queried like this:
```grophql
{
  name_of_table {
    first_column
    second_column
  }
}
```

Still to come:

- Pagination
- Filtering (e.g. rows where age > X)
- Foreign key expansion
- Much, much more

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-graphql
    python3 -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
