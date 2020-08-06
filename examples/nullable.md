# Nested query with foreign keys

```graphql
{
    repos {
        nodes {
            name
            license {
                key
                name
            }
        }
    }
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
                    "key": "apache2",
                    "name": "Apache 2"
                }
            },
            {
                "name": "dogspotter",
                "license": {
                    "key": "mit",
                    "name": "MIT"
                }
            },
            {
                "name": "private",
                "license": null
            }
        ]
    }
}
```
