# SQL view

```graphql
{
    view_on_table_with_pk(first: 3) {
        nodes {
            pk
            name
        }
    }
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20%20%20view_on_table_with_pk%28first%3A%203%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20pk%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A)

Expected output:

```json
{
    "view_on_table_with_pk": {
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
