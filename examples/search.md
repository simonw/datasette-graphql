# Table search

```graphql
{
    repos(search:"cleopaws") {
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
        "nodes": [
            {
                "full_name": "cleopaws/dogspotter"
            }
        ]
    }
}
```
