# Basic table query

```graphql
{
    users {
        nodes {
            name
            points
            score
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
                "points": 5,
                "score": 51.5
            },
            {
                "name": "simonw",
                "points": 3,
                "score": 35.2
            }
        ]
    }
}
```
