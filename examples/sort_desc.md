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
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20%20%20users%28sort_desc%3A%20points%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20points%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A)

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
