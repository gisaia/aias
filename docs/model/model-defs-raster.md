# Raster Schema

```txt
aeopres_model#/$defs/Raster
```



| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                |
| :------------------ | :--------- | :------------- | :----------- | :---------------- | :-------------------- | :------------------ | :------------------------------------------------------------------------ |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [model.schema.json\*](../../out/model.schema.json "open original schema") |

## Raster Type

`object` ([Raster](model-defs-raster.md))

# Raster Properties

| Property      | Type     | Required | Nullable       | Defined by                                                                                 |
| :------------ | :------- | :------- | :------------- | :----------------------------------------------------------------------------------------- |
| [type](#type) | `object` | Required | cannot be null | [Item](model-defs-rastertype.md "aeopres_model#/$defs/Raster/properties/type")             |
| [path](#path) | `string` | Required | cannot be null | [Item](model-defs-raster-properties-path.md "aeopres_model#/$defs/Raster/properties/path") |
| [id](#id)     | `string` | Required | cannot be null | [Item](model-defs-raster-properties-id.md "aeopres_model#/$defs/Raster/properties/id")     |

## type



`type`

*   is required

*   Type: `object` ([RasterType](model-defs-rastertype.md))

*   cannot be null

*   defined in: [Item](model-defs-rastertype.md "aeopres_model#/$defs/Raster/properties/type")

### type Type

`object` ([RasterType](model-defs-rastertype.md))

## path



`path`

*   is required

*   Type: `string` ([Path](model-defs-raster-properties-path.md))

*   cannot be null

*   defined in: [Item](model-defs-raster-properties-path.md "aeopres_model#/$defs/Raster/properties/path")

### path Type

`string` ([Path](model-defs-raster-properties-path.md))

## id



`id`

*   is required

*   Type: `string` ([Id](model-defs-raster-properties-id.md))

*   cannot be null

*   defined in: [Item](model-defs-raster-properties-id.md "aeopres_model#/$defs/Raster/properties/id")

### id Type

`string` ([Id](model-defs-raster-properties-id.md))
