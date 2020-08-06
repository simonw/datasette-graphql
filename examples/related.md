# Fetch related rows

```graphql
{
    users {
        nodes {
            name
            repos_list(first: 1) {
                totalCount
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    name
                    license {
                        key
                        name
                    }
                }
            }
        }
    }
}
```

Expected output:

```json
{
    "users": {
        "nodes": [
            {
                "name": "cleopaws",
                "repos_list": {
                    "totalCount": 1,
                    "pageInfo": {
                        "endCursor": null,
                        "hasNextPage": false
                    },
                    "nodes": [
                        {
                            "name": "dogspotter",
                            "license": {
                                "key": "mit",
                                "name": "MIT"
                            }
                        }
                    ]
                }
            },
            {
                "name": "simonw",
                "repos_list": {
                    "totalCount": 2,
                    "pageInfo": {
                        "endCursor": "1",
                        "hasNextPage": true
                    },
                    "nodes": [
                        {
                            "name": "datasette",
                            "license": {
                                "key": "apache2",
                                "name": "Apache 2"
                            }
                        }
                    ]
                }
            }
        ]
    }
}
```
