# DimensionType Schema

```txt
aeopres_model#/$defs/Properties/properties/cube:dimensions/anyOf/0/additionalProperties
```



| Abstract            | Extensible | Status         | Identifiable            | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                |
| :------------------ | :--------- | :------------- | :---------------------- | :---------------- | :-------------------- | :------------------ | :------------------------------------------------------------------------ |
| Can be instantiated | No         | Unknown status | Unknown identifiability | Forbidden         | Allowed               | none                | [model.schema.json\*](../../out/model.schema.json "open original schema") |

## additionalProperties Type

`string` ([DimensionType](model-defs-dimensiontype.md))

## additionalProperties Constraints

**enum**: the value of this property must be equal to one of the following values:

| Value        | Explanation |
| :----------- | :---------- |
| `"spatial"`  |             |
| `"temporal"` |             |
| `"geometry"` |             |
