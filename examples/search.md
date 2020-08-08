# Table search

```graphql
{
    repos(search: "cleopaws") {
        nodes {
            full_name
        }
    }
    users_get(id: 1) {
        name
            repos_list(search:"dogspotter") {
                nodes {
                    full_name
            }
        }
    }
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20%20%20repos%28search%3A%20%22cleopaws%22%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20full_name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_get%28id%3A%201%29%20%7B%0A%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20repos_list%28search%3A%22dogspotter%22%29%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20full_name%0A%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A)

Expected output:

```json
{
    "repos": {
        "nodes": [
            {
                "full_name": "cleopaws/dogspotter"
            }
        ]
    },
    "users_get": {
        "name": "cleopaws",
        "repos_list": {
            "nodes": [
                {
                    "full_name": "cleopaws/dogspotter"
                }
            ]
        }
    }
}
```
