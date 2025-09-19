import os
import pytest
from aias_common.access.configuration import AccessManagerSettings, AccessType, HttpsStorageConfiguration
import aias_common.access.storages.s3 as s3
import aias_common.access.manager as manager
import aias_common.access.storages.file as fs
import aias_common.access.storages.http as http
import aias_common.access.storages.gs as gs
from pathlib import Path


CAN_READ = [
    "https://storage.googleapis.com/gisaia-public/test-aias/ast",
    "https://storage.googleapis.com/gisaia-public/test-aias/DIMAP/",
    "https://storage.googleapis.com/gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw",
    "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md",
    "gs://gisaia-public/test-aias/ast",
    "gs://gisaia-public/test-aias/DIMAP/",
    "gs://gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw",
    "/tmp",
    "/tmp/",
]

GET_SIZE = [
    "https://storage.googleapis.com/gisaia-public/test-aias/ast",
    "https://storage.googleapis.com/gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw",
    "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md",
    "gs://gisaia-public/test-aias/ast",
    "gs://gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw"
]


FILES = [
    "https://storage.googleapis.com/gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw",
    "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md",
    "gs://gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw",
    "/tmp/tobepushed"
]

DIRS = [
    "https://storage.googleapis.com/gisaia-public/test-aias/ast",
    "https://storage.googleapis.com/gisaia-public/test-aias/DIMAP/",
    "gs://gisaia-public/test-aias/ast",
    "gs://gisaia-public/test-aias/DIMAP/",
    "/tmp",
    "/tmp/",
]

MKDIRS = [
    "/tmp/dir_for_tests",
]

CAN_NOT_READ = [
    "https://storage.googleapis.com/gisaia-public/test-aias/astsomething",
    "https://storage.googleapis.com/gisaia-public/test-aias/DIMAPsomething/",
    "https://raw.githubusercontent.com/something",
    "gs://gisaia-public/test-aias/astsomething",
    "gs://gisaia-public/test-aias/DIMAPsomething/",
    "/tmpsomething",
    "/tmpsomething/",
    "https://storage.googleapis.com/gisaia-public/test-aias/",
    "https://storage.googleapis.com/gisaia-public/",
    "https://storage.googleapis.com/",
    "gs://gisaia-public/test-aias/astsomething",
    "gs://gisaia-public/test-aias/DIMAPsomething/",
    "gs://gisaia-public/test-aias/",
    "gs://gisaia-public/",
    "/tmpsomething",
    "/tmpsomething/",
    "/",
    "",
]

CAN_WRITE = [
    "/tmp",
    "/tmp/"
]

CAN_NOT_WRITE = [
    "https://storage.googleapis.com/gisaia-public/test-aias/ast",
    "https://storage.googleapis.com/gisaia-public/test-aias/DIMAP/",
    "https://storage.googleapis.com/gisaia-public/test-aias/ast/something",
    "https://storage.googleapis.com/gisaia-public/test-aias/DIMAP/something",
    "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/",
    "gs://gisaia-public/test-aias/ast",
    "gs://gisaia-public/test-aias/DIMAP/",
    "gs://gisaia-public/test-aias/ast/something",
    "gs://gisaia-public/test-aias/DIMAP/something",
]

NOT_EXISTS = [
    "https://storage.googleapis.com/gisaia-public/test-aias/ast/something",
    "https://storage.googleapis.com/gisaia-public/test-aias/DIMAP/something/",
    "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/something/docs/docs/version.md",
    "gs://gisaia-public/test-aias/ast/something",
    "gs://gisaia-public/test-aias/DIMAP/something/",
    "/tmp/something",
    "/tmp/something/"
]

CAN_PULL = [
    "https://storage.googleapis.com/gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw",
    "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md",
    "gs://gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw"
]

CAN_NOT_PULL = [
    "https://storage.googleapis.com/gisaia-public/test-aias/cog.tiff",
    "gs://gisaia-public/test-aias/cog.tiff",
    "https://raw.githubusercontent.com/gisaia/something/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md"
]


CAN_PUSH_ON = [
    "http://localhost:9000/downloads/readwrite/pushed"
]


CAN_NOT_PUSH_ON = [
    "http://localhost:9000/downloads/read/pushed",
    "http://localhost:9000/downloads/pushed",
    "https://storage.googleapis.com/gisaia-public/test-aias/ast",
    "https://storage.googleapis.com/gisaia-public/test-aias/DIMAP/",
    "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md",
    "gs://gisaia-public/test-aias/ast",
    "gs://gisaia-public/test-aias/DIMAP/"
]


@pytest.fixture(scope="class")
def fixture_am():
    manager.AccessManager.init(AccessManagerSettings(
        storages=[
            s3.S3StorageConfiguration(bucket="downloads", endpoint="http://localhost:9000", readable_paths=["readwrite", "readonly"], writable_paths=["readwrite"]),
            s3.S3StorageConfiguration(bucket="gisaia-public", endpoint="https://storage.googleapis.com", readable_paths=["/test-aias/ast", "test-aias/DIMAP"]),
            fs.FileStorageConfiguration(readable_paths=["/tmp/"], writable_paths=["/tmp/"]),
            HttpsStorageConfiguration(domain="raw.githubusercontent.com", readable_paths=["/gisaia/ARLAS-Exploration-stack"], writable_paths=[]),
            gs.GoogleStorageConfiguration(bucket="gisaia-public", readable_paths=["/test-aias/ast", "test-aias/DIMAP"])
        ],
        tmp_dir="/tmp/"
    ))


@pytest.fixture(scope="class")
def fixture_objectstore() -> s3.S3Storage:
    return s3.S3Storage(s3.S3StorageConfiguration(bucket="downloads", endpoint="http://localhost:9000", readable_paths=["readwrite", "readonly"], writable_paths=["readwrite"]))


@pytest.fixture(scope="class")
def fixture_tobepushed():
    fl = os.path.join(manager.AccessManager.tmp_dir, "tobepushed")
    Path(fl).touch()
    return fl


@pytest.mark.parametrize("href", CAN_READ)
def test_can_read(fixture_am, href: str):
    manager.AccessManager.check_path_readable(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_can_not_read(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.check_path_readable(href)


@pytest.mark.parametrize("href", CAN_WRITE)
def test_can_write(fixture_am, href: str):
    manager.AccessManager.check_path_writable(href)


@pytest.mark.parametrize("href", CAN_NOT_WRITE)
def test_can_not_write(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.check_path_writable(href)


@pytest.mark.parametrize("href", CAN_READ)
def test_exists(fixture_am, href: str):
    assert manager.AccessManager.exists(href)


@pytest.mark.parametrize("href", NOT_EXISTS)
def test_not_exists(fixture_am, href: str):
    assert not manager.AccessManager.exists(href)


@pytest.mark.parametrize("href", CAN_PULL)
def test_pull(fixture_am, href: str):
    manager.AccessManager.pull(href, os.path.join(manager.AccessManager.tmp_dir, "pulled"))


@pytest.mark.parametrize("href", CAN_NOT_PULL)
def test_not_pull(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.pull(href, os.path.join(manager.AccessManager.tmp_dir, "pulled"))


@pytest.mark.parametrize("href", CAN_PUSH_ON)
def test_push(fixture_am, fixture_tobepushed, href: str):
    manager.AccessManager.push(fixture_tobepushed, href)


@pytest.mark.parametrize("href", CAN_NOT_WRITE)
def test_not_push(fixture_am, fixture_tobepushed, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.push(fixture_tobepushed, href)


@pytest.mark.parametrize("href", CAN_PUSH_ON)
def test_push_fo(fixture_am, fixture_tobepushed, fixture_objectstore: s3.S3Storage, href: str):
    with open(fixture_tobepushed, 'rb') as fo:
        fixture_objectstore.push_file_obj(fo, href)


@pytest.mark.parametrize("href", CAN_NOT_WRITE)
def test_not_push_fo(fixture_am, fixture_tobepushed, fixture_objectstore: s3.S3Storage, href: str):
    with pytest.raises(PermissionError):
        with open(fixture_tobepushed, 'rb') as fo:
            fixture_objectstore.push_file_obj(fo, href)


@pytest.mark.parametrize("href", FILES)
def test_is_file(fixture_am, fixture_tobepushed, href: str):
    assert manager.AccessManager.is_file(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_is_file_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.is_file(href)


@pytest.mark.parametrize("href", DIRS)
def test_is_dir(fixture_am, fixture_tobepushed, href: str):
    assert manager.AccessManager.is_dir(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_is_dir_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.is_dir(href)


@pytest.mark.parametrize("href", GET_SIZE)
def test_get_size(fixture_am, fixture_tobepushed, href: str):
    assert manager.AccessManager.get_size(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_get_size_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.get_size(href)


@pytest.mark.parametrize("href", FILES)
def test_get_rasterio_session(fixture_am, fixture_tobepushed, href: str):
    manager.AccessManager.get_rasterio_session(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_get_rasterio_session_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.get_rasterio_session(href)


@pytest.mark.parametrize("href", DIRS)
def test_listdir(fixture_am, fixture_tobepushed, href: str):
    manager.AccessManager.listdir(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_listdir_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.listdir(href)


@pytest.mark.parametrize("href", FILES)
def test_get_last_modification_time(fixture_am, fixture_tobepushed, href: str):
    print(manager.AccessManager.get_last_modification_time(href))


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_get_last_modification_time_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.get_last_modification_time(href)


@pytest.mark.parametrize("href", FILES)
def test_get_creation_time(fixture_am, fixture_tobepushed, href: str):
    print(manager.AccessManager.get_creation_time(href))


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_get_creation_time_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.get_creation_time(href)


@pytest.mark.parametrize("href", MKDIRS)
def test_makedir(fixture_am, fixture_tobepushed, href: str):
    manager.AccessManager.makedir(href)


@pytest.mark.parametrize("href", CAN_NOT_WRITE)
def test_makedir_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.makedir(href)


@pytest.mark.parametrize("href", DIRS)
def test_dirname(fixture_am, fixture_tobepushed, href: str):
    manager.AccessManager.dirname(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_dirname_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.dirname(href)


@pytest.mark.parametrize("href", DIRS)
def test_clean(fixture_am, fixture_tobepushed, href: str):
    manager.AccessManager.dirname(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_dirname_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.dirname(href)
