
# Item Schema

```
airs_model
```


| Abstract | Extensible | Status | Identifiable | Custom Properties | Additional Properties | Defined In |
|----------|------------|--------|--------------|-------------------|-----------------------|------------|
| Can be instantiated | No | Experimental | No | Forbidden | Permitted | [model.schema.json](model.schema.json) |

# Item Properties

| Property | Type | Required | Default | Defined by |
|----------|------|----------|---------|------------|
| [assets](#assets) | complex | Optional | `null` | Item (this schema) |
| [bbox](#bbox) | complex | Optional | `null` | Item (this schema) |
| [catalog](#catalog) | complex | Optional | `null` | Item (this schema) |
| [centroid](#centroid) | complex | Optional | `null` | Item (this schema) |
| [collection](#collection) | complex | Optional | `null` | Item (this schema) |
| [geometry](#geometry) | complex | Optional | `null` | Item (this schema) |
| [id](#id) | complex | Optional | `null` | Item (this schema) |
| [properties](#properties) | complex | Optional | `null` | Item (this schema) |
| `*` | any | Additional | this schema *allows* additional properties |

## assets
### A dictionary mapping string keys to Asset objects. All Asset values in the dictionary will have their owner attribute set to the created Item.

`assets`
* is optional
* type: complex
* default: `null`
* defined in this schema

### assets Type


**Any** following *options* needs to be fulfilled.


#### Option 1



#### Option 2







## bbox
### Bounding Box of the asset represented by this item using either 2D or 3D geometries. The length of the array must be 2*n where n is the number of dimensions. Could also be None in the case of a null geometry.

`bbox`
* is optional
* type: complex
* default: `null`
* defined in this schema

### bbox Type


**Any** following *options* needs to be fulfilled.


#### Option 1


Array type: 

All items must be of the type:
`number`






#### Option 2







## catalog
### Name of the catalog the item belongs to.

`catalog`
* is optional
* type: complex
* default: `null`
* defined in this schema

### catalog Type


**Any** following *options* needs to be fulfilled.


#### Option 1


`string`

* maximum length: 300 characters


#### Option 2







## centroid
### Coordinates (lon/lat) of the geometry&#39;s centroid.

`centroid`
* is optional
* type: complex
* default: `null`
* defined in this schema

### centroid Type


**Any** following *options* needs to be fulfilled.


#### Option 1


Array type: 

All items must be of the type:
`number`






#### Option 2







## collection
### Name of the collection the item belongs to.

`collection`
* is optional
* type: complex
* default: `null`
* defined in this schema

### collection Type


**Any** following *options* needs to be fulfilled.


#### Option 1


`string`

* maximum length: 300 characters


#### Option 2







## geometry
### Defines the full footprint of the asset represented by this item, formatted according to `RFC 7946, section 3.1 (GeoJSON) &lt;https://tools.ietf.org/html/rfc7946&gt;`_

`geometry`
* is optional
* type: complex
* default: `null`
* defined in this schema

### geometry Type


**Any** following *options* needs to be fulfilled.


#### Option 1



#### Option 2







## id
### Unique item identifier. Must be unique within the collection.

`id`
* is optional
* type: complex
* default: `null`
* defined in this schema

### id Type


**Any** following *options* needs to be fulfilled.


#### Option 1


`string`

* maximum length: 300 characters


#### Option 2







## properties
### Item properties

`properties`
* is optional
* type: complex
* default: `null`
* defined in this schema

### properties Type


**Any** following *options* needs to be fulfilled.


#### Option 1


* []() – `#/$defs/Properties`


#### Option 2






