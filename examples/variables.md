# GraphQL variables

[GraphQL variables](https://graphql.org/learn/queries/#variables) can be incorporated into queries.

```graphql
query specific_repo($name: String) {
    repos(filter: {name: {eq: $name}}) {
        nodes {
            name
            license {
                key
            }
        }
    }
}
```
Variables:
```json+variables
{
    "name": "datasette"
}
```
Expected output:
```json
{
    "repos": {
        "nodes": [
            {
                "name": "datasette",
                "license": {
                    "key": "apache2"
                }
            }
        ]
    }
}
```
