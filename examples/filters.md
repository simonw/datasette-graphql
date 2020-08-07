# Table filters

```graphql
{
    users_eq: users(filters:[{name: {eq: "cleopaws"}}]) {
        nodes {
            name
        }
    }
    users_not: users(filters:[{name: {not: "cleopaws"}}]) {
        nodes {
            name
        }
    }
    users_contains: users(filters:[{name: {contains: "leo"}}]) {
        nodes {
            name
        }
    }
    users_endswith: users(filters:[{name: {endswith: "paws"}}]) {
        nodes {
            name
        }
    }
    users_startswith: users(filters:[{name: {startswith: "si"}}]) {
        nodes {
            name
        }
    }
    users_gt: users(filters:[{score: {gt: 50}}]) {
        nodes {
            name
            score
        }
    }
    users_gte: users(filters:[{score: {gte: 50}}]) {
        nodes {
            name
            score
        }
    }
    users_lt: users(filters:[{score: {lt: 50}}]) {
        nodes {
            name
            score
        }
    }
    users_lte: users(filters:[{score: {lte: 50}}]) {
        nodes {
            name
            score
        }
    }
    users_like: users(filters:[{name: {like: "cl%"}}]) {
        nodes {
            name
        }
    }
    users_notlike: users(filters:[{name: {notlike: "cl%"}}]) {
        nodes {
            name
        }
    }
    users_glob: users(filters:[{name: {glob: "cl*"}}]) {
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
    }
}
```
