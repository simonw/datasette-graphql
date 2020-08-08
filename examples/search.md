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
