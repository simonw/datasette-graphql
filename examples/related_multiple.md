# Related rows for tables with multiple foreign keys

If another table has multiple foreign keys back to the same table, related row fields are created to avoid name clashes:

```graphql
{
  users {
    nodes {
      id
      name
      issues_by_user_list {
        nodes {
          id
          title
          updated_by {
            name
          }
          user {
            name
          }
        }
      }
      issues_by_updated_by_list {
        nodes {
          id
          title
          updated_by {
            name
          }
          user {
            name
          }
        }
      }
    }
  }
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20users%20%7B%0A%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20id%0A%20%20%20%20%20%20name%0A%20%20%20%20%20%20issues_by_user_list%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20id%0A%20%20%20%20%20%20%20%20%20%20title%0A%20%20%20%20%20%20%20%20%20%20updated_by%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20user%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20issues_by_updated_by_list%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20id%0A%20%20%20%20%20%20%20%20%20%20title%0A%20%20%20%20%20%20%20%20%20%20updated_by%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20user%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D%0A)

Expected output:

```json
{
    "users": {
        "nodes": [
            {
                "id": 1,
                "name": "cleopaws",
                "issues_by_user_list": {
                    "nodes": [
                        {
                            "id": 111,
                            "title": "Not enough dog stuff",
                            "updated_by": {
                                "name": "simonw"
                            },
                            "user": {
                                "name": "cleopaws"
                            }
                        }
                    ]
                },
                "issues_by_updated_by_list": {
                    "nodes": []
                }
            },
            {
                "id": 2,
                "name": "simonw",
                "issues_by_user_list": {
                    "nodes": []
                },
                "issues_by_updated_by_list": {
                    "nodes": [
                        {
                            "id": 111,
                            "title": "Not enough dog stuff",
                            "updated_by": {
                                "name": "simonw"
                            },
                            "user": {
                                "name": "cleopaws"
                            }
                        }
                    ]
                }
            }
        ]
    }
}
```
