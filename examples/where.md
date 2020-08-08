# The where: argument

The `where:` argument can be used as an alternative to `filter:` when the thing you are expressing is too complex to be modeled using a filter expression. It accepts a string fragment of SQL that will be included in the `WHERE` clause of the SQL query.

```graphql
{
    repos(where: "name='dogspotter' or license is null") {
        totalCount
        nodes {
            full_name
        }
    }
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20%20%20repos%28where%3A%20%22name%3D%27dogspotter%27%20or%20license%20is%20null%22%29%20%7B%0A%20%20%20%20%20%20%20%20totalCount%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20full_name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A)

Expected output:

```json
{
    "repos": {
        "totalCount": 2,
        "nodes": [
            {
                "full_name": "cleopaws/dogspotter"
            },
            {
                "full_name": "simonw/private"
            }
        ]
    }
}
```
