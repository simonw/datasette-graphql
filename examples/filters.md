# Table filters

```graphql
{
    users_eq: users(filter: {name: {eq: "cleopaws"}}) {
        nodes {
            name
        }
    }
    users_not: users(filter: {name: {not: "cleopaws"}}) {
        nodes {
            name
        }
    }
    users_contains: users(filter: {name: {contains: "leo"}}) {
        nodes {
            name
        }
    }
    users_endswith: users(filter: {name: {endswith: "paws"}}) {
        nodes {
            name
        }
    }
    users_startswith: users(filter: {name: {startswith: "si"}}) {
        nodes {
            name
        }
    }
    users_gt: users(filter: {score: {gt: 50}}) {
        nodes {
            name
            score
        }
    }
    users_gte: users(filter: {score: {gte: 50}}) {
        nodes {
            name
            score
        }
    }
    users_lt: users(filter: {score: {lt: 50}}) {
        nodes {
            name
            score
        }
    }
    users_lte: users(filter: {score: {lte: 50}}) {
        nodes {
            name
            score
        }
    }
    users_like: users(filter: {name: {like: "cl%"}}) {
        nodes {
            name
        }
    }
    users_notlike: users(filter: {name: {notlike: "cl%"}}) {
        nodes {
            name
        }
    }
    users_glob: users(filter: {name: {glob: "cl*"}}) {
        nodes {
            name
        }
    }
    users_in: users(filter: {name: {in: ["cleopaws"]}}) {
        nodes {
            name
        }
    }
    users_notin: users(filter: {name: {notin: ["cleopaws"]}}) {
        nodes {
            name
        }
    }
    repos_arraycontains: repos(filter: {tags: {arraycontains: "dogs"}}) {
        nodes {
            full_name
            tags
        }
    }
    users_date: users(filter: {joined: {date: "2018-11-04"}}) {
        nodes {
            name
        }
    }
    users_isnull: users(filter: {dog_award: {isnull: true}}) {
        nodes {
            name
        }
    }
    users_notnull: users(filter: {dog_award: {notnull: true}}) {
        nodes {
            name
        }
    }
    users_isblank: users(filter: {dog_award: {isblank: true}}) {
        nodes {
            name
        }
    }
    users_notblank: users(filter: {dog_award: {notblank: true}}) {
        nodes {
            name
        }
    }
}
```

Expected output:

```json
{
    "users_eq": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    },
    "users_not": {
        "nodes": [
            {
                "name": "simonw"
            }
        ]
    },
    "users_contains": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    },
    "users_endswith": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    },
    "users_startswith": {
        "nodes": [
            {
                "name": "simonw"
            }
        ]
    },
    "users_gt": {
        "nodes": [
            {
                "name": "cleopaws",
                "score": 51.5
            }
        ]
    },
    "users_gte": {
        "nodes": [
            {
                "name": "cleopaws",
                "score": 51.5
            }
        ]
    },
    "users_lt": {
        "nodes": [
            {
                "name": "simonw",
                "score": 35.2
            }
        ]
    },
    "users_lte": {
        "nodes": [
            {
                "name": "simonw",
                "score": 35.2
            }
        ]
    },
    "users_like": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    },
    "users_notlike": {
        "nodes": [
            {
                "name": "simonw"
            }
        ]
    },
    "users_glob": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    },
    "users_in": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    },
    "users_notin": {
        "nodes": [
            {
                "name": "simonw"
            }
        ]
    },
    "repos_arraycontains": {
        "nodes": [
            {
                "full_name": "cleopaws/dogspotter",
                "tags": "[\"dogs\"]"
            }
        ]
    },
    "users_date": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    },
    "users_isnull": {
        "nodes": [
            {
                "name": "simonw"
            }
        ]
    },
    "users_notnull": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    },
    "users_isblank": {
        "nodes": [
            {
                "name": "simonw"
            }
        ]
    },
    "users_notblank": {
        "nodes": [
            {
                "name": "cleopaws"
            }
        ]
    }
}
```
