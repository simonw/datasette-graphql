# datasette-graphql

[![PyPI](https://img.shields.io/pypi/v/datasette-graphql.svg)](https://pypi.org/project/datasette-graphql/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-graphql?include_prereleases&label=changelog)](https://github.com/simonw/datasette-graphql/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-graphql/blob/master/LICENSE)

A GraphQL endpoint for Datasette

**Work in progress alpha** - this has many missing features.

Try out a live demo at [datasette-graphql-demo.datasette.io/graphql](https://datasette-graphql-demo.datasette.io/graphql?query=%7B%0A%20%20repos%20%7B%0A%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20full_name%0A%20%20%20%20%20%20description%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D%0A).

## Installation

Install this plugin in the same environment as Datasette.

    $ pip install datasette-graphql

## Usage

This plugin sets up `/graphql` as a GraphQL endpoint for the first attached database.

### Querying for tables and columns

Individual tables can be queried like this:

```graphql
{
  repos {
    nodes {
      id
      full_name
      description
    }
  }
}
```

### Accessing nested objects

If a column is a foreign key to another table, you can request columns of that table using a nested query like this:
```graphql
{
  repos {
    nodes {
      id
      full_name
      owner {
        id
        login
      }
    }
  }
}
```

### Filtering tables

You can filter the rows returned for a specific table using the `filters:` argument. This accepts a list of filters, where a filter is a string of the form `column=value` or `column__op=value`. For example, to return just repositories with the Apache 2 license and more than 10 stars:

```graphql
{
  repos(filters: ["license=apache-2.0", "stargazers_count__gt=10"]) {
    nodes {
      full_name
      stargazers_count
      license {
        key
      }
    }
  }
}
```

This is the same format used for querystring arguments to the Datasette table view, see [column filter arguments](https://datasette.readthedocs.io/en/stable/json_api.html#column-filter-arguments) in the Datasette documentation.

### Sorting

You can set a sort order for results from a table using the `sort:` or `sort_desc:` arguments. The value for this argument should be the name of the column you wish to sort (or sort-descending) by.

```graphql
{
  repos(sort_desc: stargazers_count) {
    nodes {
      full_name
      stargazers_count
    }
  }
}
```

### Pagination

By default the first 10 rows will be returned. You can control this using the `first:` argument.

```graphql
{
  repos(first: 20) {
    totalCount
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      full_name
      stargazers_count
      license {
        key
      }
    }
  }
}
```

The `totalCount` field returns the total number of records that match the query.

Requesting the `pageInfo.endCursor` field provides you with the value you need to request the next page. You can pass this to the `after:` argument to request the next page.

```graphql
{
  repos(first: 20, after: "134874019") {
    totalCount
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      full_name
      stargazers_count
      license {
        key
      }
    }
  }
}
```

The `hasNextPage` field tells you if there are any more records.

### Search

If a table has been configured to use SQLite full-text search you can execute searches against it using the `search:` argument:

```graphql
{
  repos(search: "datasette") {
    totalCount
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      full_name
      description
    }
  }
}
```

The [sqlite-utils](https://sqlite-utils.readthedocs.io/) Python library and CLI tool can be used to add full-text search to an existing database table.

### Auto camelCase

The names of your columns and tables default to being matched by their representations in GraphQL.

If you have tables with `names_like_this` you may want to work with them in GraphQL using `namesLikeThis`, for consistency with GraphQL and JavaScript conventions.

You can turn on automatic camelCase using the `"auto_camelcase"` plugin configuration setting in `metadata.json`, like this:

```json
{
    "plugins": {
        "datasette-graphql": {
            "auto_camelcase": true
        }
    }
}
```

## Still to come

See [issues](https://github.com/simonw/datasette-graphql/issues) for a full list. Planned improvements include:

- Canned query support
- Ability to allowlist specific tables, views and canned queries

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
