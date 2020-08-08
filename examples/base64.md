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
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20%20%20images%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20path%0A%20%20%20%20%20%20%20%20%20%20%20%20content%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A)

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
