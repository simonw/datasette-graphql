# Binary content in base64

```graphql
{
    images {
        nodes {
            path
            content
        }
    }
}
```

Expected output:

```json
{
    "images": {
        "nodes": [
            {
                "path": "1x1.gif",
                "content": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
            }
        ]
    }
}
```
