# SQL view

```graphql
{
    view_on_paginate_by_pk(first: 3) {
        nodes {
            pk
            name
        }
    }
}
```

Expected output:

```json
{
    "view_on_paginate_by_pk": {
        "nodes": [
            {
                "pk": 1,
                "name": "Row 1"
            },
            {
                "pk": 2,
                "name": "Row 2"
            },
            {
                "pk": 3,
                "name": "Row 3"
            }
        ]
    }
}
```
