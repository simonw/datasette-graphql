# Table search

```graphql
{
    users(sort: points) {
        nodes {
            name
            points
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
                "name": "simonw",
                "points": 3
            },
            {
                "name": "cleopaws",
                "points": 5
            }
        ]
    }
}
```
