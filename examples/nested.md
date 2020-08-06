# Nested query

```graphql
{
    issues {
        nodes {
            title
            user {
                id
                name
            }
            repo {
                name
                license {
                    key
                    name
                }
                owner {
                    id
                    name
                }
            }
        }
    }
}
```

Expected output:

```json
{
    "issues": {
        "nodes": [
            {
                "title": "Not enough dog stuff",
                "user": {
                    "id": 1,
                    "name": "cleopaws"
                },
                "repo": {
                    "name": "datasette",
                    "license": {
                        "key": "apache2",
                        "name": "Apache 2"
                    },
                    "owner": {
                        "id": 2,
                        "name": "simonw"
                    }
                }
            }
        ]
    }
}
```
