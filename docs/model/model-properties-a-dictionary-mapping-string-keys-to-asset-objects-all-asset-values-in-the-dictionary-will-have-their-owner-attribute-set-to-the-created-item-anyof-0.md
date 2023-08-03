# Untitled object in Item Schema

```txt
aeopres_model#/properties/assets/anyOf/0
```



| Abstract            | Extensible | Status         | Identifiable            | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                |
| :------------------ | :--------- | :------------- | :---------------------- | :---------------- | :-------------------- | :------------------ | :------------------------------------------------------------------------ |
| Can be instantiated | No         | Unknown status | Unknown identifiability | Forbidden         | Allowed               | none                | [model.schema.json\*](../../out/model.schema.json "open original schema") |

## 0 Type

`object` ([Details](model-properties-a-dictionary-mapping-string-keys-to-asset-objects-all-asset-values-in-the-dictionary-will-have-their-owner-attribute-set-to-the-created-item-anyof-0.md))

# 0 Properties

| Property              | Type     | Required | Nullable       | Defined by                                                                                  |
| :-------------------- | :------- | :------- | :------------- | :------------------------------------------------------------------------------------------ |
| Additional Properties | `object` | Optional | cannot be null | [Item](model-defs-asset.md "aeopres_model#/properties/assets/anyOf/0/additionalProperties") |

## Additional Properties

Additional properties are allowed, as long as they follow this schema:



*   is optional

*   Type: `object` ([Asset](model-defs-asset.md))

*   cannot be null

*   defined in: [Item](model-defs-asset.md "aeopres_model#/properties/assets/anyOf/0/additionalProperties")

### additionalProperties Type

`object` ([Asset](model-defs-asset.md))
