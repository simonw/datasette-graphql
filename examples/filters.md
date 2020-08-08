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
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20%20%20users_eq%3A%20users%28filter%3A%20%7Bname%3A%20%7Beq%3A%20%22cleopaws%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_not%3A%20users%28filter%3A%20%7Bname%3A%20%7Bnot%3A%20%22cleopaws%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_contains%3A%20users%28filter%3A%20%7Bname%3A%20%7Bcontains%3A%20%22leo%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_endswith%3A%20users%28filter%3A%20%7Bname%3A%20%7Bendswith%3A%20%22paws%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_startswith%3A%20users%28filter%3A%20%7Bname%3A%20%7Bstartswith%3A%20%22si%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_gt%3A%20users%28filter%3A%20%7Bscore%3A%20%7Bgt%3A%2050%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20score%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_gte%3A%20users%28filter%3A%20%7Bscore%3A%20%7Bgte%3A%2050%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20score%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_lt%3A%20users%28filter%3A%20%7Bscore%3A%20%7Blt%3A%2050%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20score%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_lte%3A%20users%28filter%3A%20%7Bscore%3A%20%7Blte%3A%2050%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20score%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_like%3A%20users%28filter%3A%20%7Bname%3A%20%7Blike%3A%20%22cl%25%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_notlike%3A%20users%28filter%3A%20%7Bname%3A%20%7Bnotlike%3A%20%22cl%25%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_glob%3A%20users%28filter%3A%20%7Bname%3A%20%7Bglob%3A%20%22cl%2A%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_in%3A%20users%28filter%3A%20%7Bname%3A%20%7Bin%3A%20%5B%22cleopaws%22%5D%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_notin%3A%20users%28filter%3A%20%7Bname%3A%20%7Bnotin%3A%20%5B%22cleopaws%22%5D%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20repos_arraycontains%3A%20repos%28filter%3A%20%7Btags%3A%20%7Barraycontains%3A%20%22dogs%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20full_name%0A%20%20%20%20%20%20%20%20%20%20%20%20tags%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_date%3A%20users%28filter%3A%20%7Bjoined%3A%20%7Bdate%3A%20%222018-11-04%22%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_isnull%3A%20users%28filter%3A%20%7Bdog_award%3A%20%7Bisnull%3A%20true%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_notnull%3A%20users%28filter%3A%20%7Bdog_award%3A%20%7Bnotnull%3A%20true%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_isblank%3A%20users%28filter%3A%20%7Bdog_award%3A%20%7Bisblank%3A%20true%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_notblank%3A%20users%28filter%3A%20%7Bdog_award%3A%20%7Bnotblank%3A%20true%7D%7D%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A)

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
