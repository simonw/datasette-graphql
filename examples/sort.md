# Table search

```graphql
{
    users(sort: points) {
        nodes {
            name
            points
        }
    }
    users_sort_by_dog_award: users(sort: dog_award) {
        nodes {
            name
            dog_award
        }
    }
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20%20%20users%28sort%3A%20points%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20points%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20users_sort_by_dog_award%3A%20users%28sort%3A%20dog_award%29%20%7B%0A%20%20%20%20%20%20%20%20nodes%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20name%0A%20%20%20%20%20%20%20%20%20%20%20%20dog_award%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%7D%0A)

Expected output:

```json
{
    "users": {
        "nodes": [
            {
                "name": "simonw",
                "points": 3
            },
            {
                "name": "cleopaws",
                "points": 5
            }
        ]
    },
    "users_sort_by_dog_award": {
        "nodes": [
            {
                "name": "simonw",
                "dog_award": null
            },
            {
                "name": "cleopaws",
                "dog_award": "3rd best mutt"
            }
        ]
    }
}
```
