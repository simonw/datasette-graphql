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
