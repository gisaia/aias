# Untitled object in Item Schema

```txt
airs_model#/$defs/Properties/properties/cube__dimensions/anyOf/0
```



| Abstract            | Extensible | Status         | Identifiable            | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                |
| :------------------ | :--------- | :------------- | :---------------------- | :---------------- | :-------------------- | :------------------ | :------------------------------------------------------------------------ |
| Can be instantiated | No         | Unknown status | Unknown identifiability | Forbidden         | Allowed               | none                | [model.schema.json\*](../../out/model.schema.json "open original schema") |

## 0 Type

`object` ([Details](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube-anyof-0.md))

# 0 Properties

| Property              | Type     | Required | Nullable       | Defined by                                                                                                                  |
| :-------------------- | :------- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| Additional Properties | `string` | Optional | cannot be null | [Item](model-defs-dimensiontype.md "airs_model#/$defs/Properties/properties/cube__dimensions/anyOf/0/additionalProperties") |

## Additional Properties

Additional properties are allowed, as long as they follow this schema:



*   is optional

*   Type: `string` ([DimensionType](model-defs-dimensiontype.md))

*   cannot be null

*   defined in: [Item](model-defs-dimensiontype.md "airs_model#/$defs/Properties/properties/cube__dimensions/anyOf/0/additionalProperties")

### additionalProperties Type

`string` ([DimensionType](model-defs-dimensiontype.md))

### additionalProperties Constraints

**enum**: the value of this property must be equal to one of the following values:

| Value        | Explanation |
| :----------- | :---------- |
| `"spatial"`  |             |
| `"temporal"` |             |
| `"geometry"` |             |
