# table_get to retrieve individual rows

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
