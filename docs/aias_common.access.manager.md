<!-- markdownlint-disable -->

<a href="../python/aias_common/access/manager.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `aias_common.access.manager`






---

<a href="../python/aias_common/access/manager.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AccessManager`







---

<a href="../python/aias_common/access/manager.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `check_local_path_writable`

```python
check_local_path_writable(href: str)
```

Checks that the path is a writable path for at least one of the file storages 

---

<a href="../python/aias_common/access/manager.py#L192"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clean`

```python
clean(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L259"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `dirname`

```python
dirname(href: str)
```

Wraps os.path.dirname to allow for absolute path to be determined if needed 

---

<a href="../python/aias_common/access/manager.py#L112"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `exists`

```python
exists(href: str) → bool
```

Whether the file exists 

---

<a href="../python/aias_common/access/manager.py#L246"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_creation_time`

```python
get_creation_time(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L241"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_last_modification_time`

```python
get_last_modification_time(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L106"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_rasterio_session`

```python
get_rasterio_session(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L219"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_size`

```python
get_size(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_storage_parameters`

```python
get_storage_parameters(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `init`

```python
init(ams: AccessManagerSettings)
```





---

<a href="../python/aias_common/access/manager.py#L213"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_dir`

```python
is_dir(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_download_required`

```python
is_download_required(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L207"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_file`

```python
is_file(href: str)
```





---

<a href="../python/aias_common/access/manager.py#L232"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `listdir`

```python
listdir(href: str) → list[File]
```





---

<a href="../aias_common/access/manager/make_local#L127"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `make_local`

```python
make_local(href: str, dst: str | None = None)
```

Prepare the file to be processed locally. Once the file has been used, if it has been pulled, deletes it. 



**Args:**
 
 - <b>`href`</b> (str):  Href (local or not) of the file 



**Returns:**
 
 - <b>`str`</b>:  The local path at which the file can be found 

---

<a href="../aias_common/access/manager/make_local_list#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `make_local_list`

```python
make_local_list(href_list: list[str], dst_list: list[str | None] | None = None)
```

Prepare a list of files to make them available locally for further processing. Once used, the file is deleted if it has been pulled 

---

<a href="../python/aias_common/access/manager.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `makedir`

```python
makedir(href: str, strict=False)
```

Create if needed (and possible) the specified dir 

---

<a href="../python/aias_common/access/manager.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pull`

```python
pull(href: str, dst: str)
```

Pulls a file from a storage to write it in the local storage. If the input storage is local, then it is a copy. Otherwise it is a download. 

---

<a href="../python/aias_common/access/manager.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `resolve_storage`

```python
resolve_storage(
    href: str
) → Annotated[Union[FileStorage, GoogleStorage, HttpStorage, HttpsStorage, S3Storage], FieldInfo(annotation=NoneType, required=True, discriminator='type')]
```

Based on the defined storages, returns the one matching the input href 

---

<a href="../aias_common/access/manager/stream#L95"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `stream`

```python
stream(href: str)
```

Reads the content of a file in a storage without downloading it. 

---

<a href="../python/aias_common/access/manager.py#L200"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `zip`

```python
zip(href: str, zip_path: str)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
