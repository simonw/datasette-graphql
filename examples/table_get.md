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
