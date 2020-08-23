# Fragments

```graphql
{
  cleopaws: users_row(id: 1) {
    ...userFields
  }
  simonw: users_row(id: 2) {
    ...userFields
  }
}

fragment userFields on users {
  id
  name
  dog_award
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20cleopaws%3A%20users_row%28id%3A%201%29%20%7B%0A%20%20%20%20...userFields%0A%20%20%7D%0A%20%20simonw%3A%20users_row%28id%3A%202%29%20%7B%0A%20%20%20%20...userFields%0A%20%20%7D%0A%7D%0A%0Afragment%20userFields%20on%20users%20%7B%0A%20%20id%0A%20%20name%0A%20%20dog_award%0A%7D%0A)

Expected output:

```json
{
    "cleopaws": {
        "id": 1,
        "name": "cleopaws",
        "dog_award": "3rd best mutt"
    },
    "simonw": {
        "id": 2,
        "name": "simonw",
        "dog_award": null
    }
}
```
