# Fetch related rows

```graphql
{
    users {
        nodes {
            name
            repos_list(first: 1) {
                totalCount
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    name
                    license {
                        key
                        name
                    }
                }
            }
        }
    }
    users_with_dogspotter: users {
        nodes {
            name
            repos_list(filter: {name: {eq: "dogspotter"}}, sort: id) {
                totalCount
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    name
                }
            }
        }
    }
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20%20%20users%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20repos_list%28first%3A%201%29%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20totalCount%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20pageInfo%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20endCursor%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20hasNextPage%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20license%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20key%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_with_dogspotter%3A%20users%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20repos_list%28filter%3A%20%7Bname%3A%20%7Beq%3A%20%22dogspotter%22%7D%7D%2C%20sort%3A%20id%29%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20totalCount%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20pageInfo%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20endCursor%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20hasNextPage%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A)

Expected output:

```json
{
    "users": {
        "nodes": [
            {
                "name": "cleopaws",
                "repos_list": {
                    "totalCount": 1,
                    "pageInfo": {
                        "endCursor": null,
                        "hasNextPage": false
                    },
                    "nodes": [
                        {
                            "name": "dogspotter",
                            "license": {
                                "key": "mit",
                                "name": "MIT"
                            }
                        }
                    ]
                }
            },
            {
                "name": "simonw",
                "repos_list": {
                    "totalCount": 2,
                    "pageInfo": {
                        "endCursor": "1",
                        "hasNextPage": true
                    },
                    "nodes": [
                        {
                            "name": "datasette",
                            "license": {
                                "key": "apache2",
                                "name": "Apache 2"
                            }
                        }
                    ]
                }
            }
        ]
    },
    "users_with_dogspotter": {
        "nodes": [
            {
                "name": "cleopaws",
                "repos_list": {
                    "totalCount": 1,
                    "pageInfo": {
                        "endCursor": null,
                        "hasNextPage": false
                    },
                    "nodes": [
                        {
                            "name": "dogspotter"
                        }
                    ]
                }
            },
            {
                "name": "simonw",
                "repos_list": {
                    "totalCount": 0,
                    "pageInfo": {
                        "endCursor": null,
                        "hasNextPage": false
                    },
                    "nodes": []
                }
            }
        ]
    }
}
```
