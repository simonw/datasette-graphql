# GraphQL variables

[GraphQL variables](https://graphql.org/learn/queries/#variables) can be incorporated into queries.

```graphql
query ($name: String) {
    repos(filter: {name: {eq: $name}}) {
        nodes {
            name
            license {
                _key
            }
        }
    }
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0Aquery%20%28%24name%3A%20String%29%20%7B%0A%20%20%20%20repos%28filter%3A%20%7Bname%3A%20%7Beq%3A%20%24name%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20license%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20_key%0A%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A&variables=%7B%0A%20%20%20%20%22name%22%3A%20%22datasette%22%0A%7D%0A)

Variables:
```json+variables
{
    "name": "datasette"
}
```
Expected output:
```json
{
    "repos": {
        "nodes": [
            {
                "name": "datasette",
                "license": {
                    "_key": "apache2"
                }
            }
        ]
    }
}
```
