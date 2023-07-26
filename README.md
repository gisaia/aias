# aeoprs
ARLAS EO Product Registration Services

## Data model

The AEOPRS Model is based in the STAC specifications. It supports the folling extensions:
- view
- storage
- eo
- processing
- dc3 (ARLAS Datacube Builder)
- cube
- sar
- proj

Also, metadata are enriched and placed in the `generated`` namespace.

Namespaces are prefixes in the key names of the JSON. The `:` is used for seperating the namespace and the field name. Since ARLAS does not support the `:` in field names, the character is replaced by `__` for storage and indexation.


## Tests
To run the tests:

```shell
./test/tests.sh 
```
