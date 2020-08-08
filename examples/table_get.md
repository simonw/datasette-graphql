# table_get to retrieve individual rows

Every table in the database automatically gets a field that is the name of the table plus `_get`. This field can be used to directly retrieve individual rows. The primary key columns of the table become field arguments. `rowid` and compound primary key tables are also supported.

```graphql
{
  table_with_rowid_get(rowid: 1) {
    name
  }
  table_with_pk_get(pk: 1) {
    pk
    name
  }
  table_with_compound_pk_get(pk1:1, pk2:3) {
    name
    pk1
    pk2
  }
  users_get(id: 12345) {
    name
  }
}
```
[Try this query](https://datasette-graphql-demo.datasette.io/graphql/fixtures?query=%0A%7B%0A%20%20table_with_rowid_get%28rowid%3A%201%29%20%7B%0A%20%20%20%20name%0A%20%20%7D%0A%20%20table_with_pk_get%28pk%3A%201%29%20%7B%0A%20%20%20%20pk%0A%20%20%20%20name%0A%20%20%7D%0A%20%20table_with_compound_pk_get%28pk1%3A1%2C%20pk2%3A3%29%20%7B%0A%20%20%20%20name%0A%20%20%20%20pk1%0A%20%20%20%20pk2%0A%20%20%7D%0A%20%20users_get%28id%3A%2012345%29%20%7B%0A%20%20%20%20name%0A%20%20%7D%0A%7D%0A)

```json
{
    "table_with_rowid_get": {
        "name": "Row 1"
    },
    "table_with_pk_get": {
        "pk": 1,
        "name": "Row 1"
    },
    "table_with_compound_pk_get": {
        "name": "Row 1 3",
        "pk1": 1,
        "pk2": 3
    },
    "users_get": null
}
```
That last `users_get` result is `null` because the provided ID refers to a record that does not exist.
