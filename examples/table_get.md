# table_get to retrieve individual rows

```graphql
{
  paginate_by_rowid_get(rowid: 1) {
    name
  }
  paginate_by_pk_get(pk: 1) {
    pk
    name
  }
  paginate_by_compound_pk_get(pk1:1, pk2:3) {
    name
    pk1
    pk2
  }
}
```

```json
{
    "paginate_by_rowid_get": {
        "name": "Row 1"
    },
    "paginate_by_pk_get": {
        "pk": 1,
        "name": "Row 1"
    },
    "paginate_by_compound_pk_get": {
        "name": "Row 1 3",
        "pk1": 1,
        "pk2": 3
    }
}
```
