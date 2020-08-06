# Table search

```graphql
{
    users(sort_desc: points) {
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
                "name": "cleopaws",
                "points": 5
            },
            {
                "name": "simonw",
                "points": 3
            }
        ]
    }
}
```
