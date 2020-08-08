# datasette-graphql

[![PyPI](https://img.shields.io/pypi/v/datasette-graphql.svg)](https://pypi.org/project/datasette-graphql/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-graphql?include_prereleases&label=changelog)](https://github.com/simonw/datasette-graphql/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-graphql/blob/master/LICENSE)

A GraphQL endpoint for Datasette

Read more about this project: [GraphQL in Datasette with the new datasette-graphql plugin](https://simonwillison.net/2020/Aug/7/datasette-graphql/)

Try out a live demo at [datasette-graphql-demo.datasette.io/graphql](https://datasette-graphql-demo.datasette.io/graphql?query=%7B%0A%20%20repos(first%3A10%2C%20search%3A%20%22sql%22%2C%20sort_desc%3A%20created_at)%20%7B%0A%20%20%20%20totalCount%0A%20%20%20%20pageInfo%20%7B%0A%20%20%20%20%20%20endCursor%0A%20%20%20%20%20%20hasNextPage%0A%20%20%20%20%7D%0A%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20full_name%0A%20%20%20%20%20%20description%0A%20%20%20%20%09stargazers_count%0A%20%20%20%20%20%20created_at%0A%20%20%20%20%20%20owner%20%7B%0A%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20html_url%0A%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D%0A)

![GraphiQL animated demo](https://static.simonwillison.net/static/2020/graphiql.gif)

## Installation

Install this plugin in the same environment as Datasette.

    $ pip install datasette-graphql

## Usage

This plugin sets up `/graphql` as a GraphQL endpoint for the first attached database.

If you have multiple attached databases each will get its own endpoint at `/graphql/name_of_database`.

### Querying for tables and columns

Individual tables (and SQL views) can be queried like this:

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

In this example query the underlying database table is called `repos` and its columns include `id`, `full_name` and `description`.

### Fetching a single record

If you only want to fetch a single record - for example if you want to fetch a row by its primary key - you can use the `tablename_get` field:

```graphql
{
  repos_get(id: 107914493) {
    id
    full_name
    description
  }
}
```

The `tablename_get` field accepts the primary key column (or columns) as arguments. It also supports the same `filter:`, `search:`, `sort:` and `sort_desc:` arguments as the `tablename` field, described below.

### Accessing nested objects

If a column is a foreign key to another table, you can request columns from the table pointed to by that foreign key using a nested query like this:

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

### Accessing related objects

If another table has a foreign key back to the table you are accessing, you can fetch rows from that related table.

Consider a `users` table which is related to `repos` - a repo has a foreign key back to the user that owns the repository. The `users` object type will have a `repos_list` field which can be used to access those related repos:

```graphql
{
  users(first: 1, search:"simonw") {
    nodes {
      name
      repos_list(first: 5) {
        totalCount
        nodes {
          full_name
        }
      }
    }
  }
}
```

### Filtering tables

You can filter the rows returned for a specific table using the `filter:` argument. This accepts a filter object mapping columns to operations. For example, to return just repositories with the Apache 2 license and more than 10 stars:

```graphql
{
  repos(filter: {license: {eq: "apache-2.0"}, stargazers_count: {gt: 10}}) {
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

See [table filters examples](https://github.com/simonw/datasette-graphql/blob/main/examples/filters.md) for more operations, and [column filter arguments](https://datasette.readthedocs.io/en/stable/json_api.html#column-filter-arguments) in the Datasette documentation for details of how those operations work.

These same filters can be used on nested relationships, like so:

```graphql
{
  users_get(id: 9599) {
    name
    repos_list(filter: {name: {startswith: "datasette-"}}) {
      totalCount
      nodes {
        full_name
      }
    }
  }
}
```

The `where:` argument can be used as an alternative to `filter:` when the thing you are expressing is too complex to be modeled using a filter expression. It accepts a string fragment of SQL that will be included in the `WHERE` clause of the SQL query.

```graphql
{
  repos(where: "name='sqlite-utils' or name like 'datasette-%'") {
    totalCount
    nodes {
      full_name
    }
  }
}
```

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

### CORS

This plugin obeys the `--cors` option passed to the `datasette` command-line tool. If you pass `--cors` it adds the following CORS HTTP headers to allow JavaScript running on other domains to access the GraphQL API:

    access-control-allow-headers: content-type
    access-control-allow-method: POST
    access-control-allow-origin: *

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
