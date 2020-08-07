# Table filters

```graphql
{
    users(filters:[{score: {gt: 50}}]) {
        nodes {
            name
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
                "score": 51.5
            }
        ]
    }
}
```
