import os
import shutil
import pytest
from aias_common.access.configuration import AccessManagerSettings, HttpsStorageConfiguration
import aias_common.access.storages.s3 as s3
import aias_common.access.manager as manager
import aias_common.access.storages.file as fs
import aias_common.access.storages.gs as gs
from pathlib import Path
import os.path as p

MINIO_HOST = "minio"


###########################
# FILES AND DIR VARIABLES
###########################

S3_RO_DIR_SLASH = "https://storage.googleapis.com/gisaia-public/test-aias/spot6/"
S3_RO_DIR_NO_SLASH = "https://storage.googleapis.com/gisaia-public/test-aias/ast"
S3_RO_FILE = "https://storage.googleapis.com/gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw"
S3_RO_FILE2 = "https://storage.googleapis.com/gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tif"
S3_RO_SMALL_DIR = "https://storage.googleapis.com/gisaia-public/test-aias/spot6/PROD_SPOT6_001/LIBRARY"
S3_RO_DIR = "http://" + MINIO_HOST + ":9000/downloads/readonly/"
S3_RW_DIR = "http://" + MINIO_HOST + ":9000/downloads/readwrite/"
S3_RW_FILE = "http://" + MINIO_HOST + ":9000/downloads/readwrite/a_file"

GS_RO_DIR_NO_SLASH = "gs://gisaia-public/test-aias/ast"
GS_RO_DIR_SLASH = "gs://gisaia-public/test-aias/spot6/"
GS_RO_FILE = "gs://gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw"
GS_RO_SMALL_DIR = "gs://gisaia-public/test-aias/spot6/PROD_SPOT6_001/LIBRARY/"

HTTPS_RO_FILE = "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md"

FS_RO_DIR_NO_SLASH = "/tmp/readonly"
FS_RW_DIR_SLASH = "/tmp/readwrite/"

FS_RO_FILE = "/tmp/readonly/file"
FS_RW_FILE = "/tmp/readwrite/file"

GDAL_FILES = [
    "https://storage.googleapis.com/gisaia-public/test-aias/images/jpeg2000.jpg2", "gs://gisaia-public/test-aias/images/jpeg2000.jpg2"
]


###########################
# PARAMETER MATRICES
###########################

CAN_READ = [
    GS_RO_FILE,
    GS_RO_DIR_SLASH,
    GS_RO_DIR_NO_SLASH,

    HTTPS_RO_FILE,

    S3_RO_DIR_SLASH,
    S3_RO_DIR_NO_SLASH,
    S3_RO_FILE,
    S3_RO_DIR,
    S3_RW_DIR,

    FS_RO_DIR_NO_SLASH,
    FS_RW_DIR_SLASH,
    FS_RO_FILE,
    FS_RW_FILE,
]

GET_SIZE = CAN_READ

FILES = [
    GS_RO_FILE,
    S3_RO_FILE,
    HTTPS_RO_FILE,
    FS_RO_FILE,
    FS_RW_FILE,
]


DIRS = [
    GS_RO_DIR_SLASH,
    GS_RO_DIR_NO_SLASH,

    S3_RO_DIR_SLASH,
    S3_RO_DIR_NO_SLASH,
    S3_RO_DIR,
    S3_RW_DIR,

    FS_RO_DIR_NO_SLASH,
    FS_RW_DIR_SLASH,
]

MKDIRS = [
    FS_RW_DIR_SLASH + "dir_for_mkdir_test",
]

CAN_NOT_READ = [
    GS_RO_DIR_NO_SLASH + "something",
    GS_RO_DIR_NO_SLASH + "andsomethingelse/",
    p.dirname(GS_RO_DIR_NO_SLASH),
    p.dirname(p.dirname(GS_RO_DIR_NO_SLASH)),

    HTTPS_RO_FILE.replace("ARLAS-Exploration-stack", "ARLAS-Exploration-stack-something"),

    S3_RO_DIR_SLASH.replace("spot6", "spot6-something"),
    S3_RO_DIR_NO_SLASH + "something",
    p.dirname(S3_RO_DIR_NO_SLASH),
    p.dirname(p.dirname(S3_RO_DIR_NO_SLASH)),

    p.dirname(FS_RO_DIR_NO_SLASH),
    FS_RO_DIR_NO_SLASH + "something",
    FS_RO_DIR_NO_SLASH + "andsomethingelse/",
    "/",
    "",
]

CAN_WRITE = [
    FS_RW_DIR_SLASH,
    S3_RW_DIR,
]

CAN_NOT_WRITE = [
    GS_RO_DIR_SLASH,
    GS_RO_DIR_NO_SLASH,
    GS_RO_DIR_NO_SLASH + "something",
    GS_RO_DIR_NO_SLASH + "andsomethingelse/",
    p.dirname(GS_RO_DIR_NO_SLASH),
    p.dirname(p.dirname(GS_RO_DIR_NO_SLASH)),

    S3_RO_DIR_SLASH,
    S3_RO_DIR_NO_SLASH,
    S3_RO_DIR,
    p.dirname(S3_RO_DIR_NO_SLASH),
    p.dirname(p.dirname(S3_RO_DIR_NO_SLASH)),

    FS_RO_DIR_NO_SLASH,
    p.dirname(FS_RO_DIR_NO_SLASH),
    FS_RO_DIR_NO_SLASH + "something",
    FS_RO_DIR_NO_SLASH + "andsomethingelse/",
]


CAN_CLEAN = [
    S3_RW_FILE,
    FS_RW_FILE
]

CAN_NOT_CLEAN = [
    GS_RO_DIR_NO_SLASH + "something",
    GS_RO_DIR_NO_SLASH + "andsomethingelse/",
    S3_RO_DIR_NO_SLASH,

    FS_RO_DIR_NO_SLASH,
    FS_RO_DIR_NO_SLASH + "something",
    FS_RO_DIR_NO_SLASH + "andsomethingelse/",
]

NOT_EXISTS = [
    GS_RO_FILE + "something",
    GS_RO_DIR_SLASH + "something",

    HTTPS_RO_FILE + "something",

    S3_RO_DIR_SLASH + "something",
    S3_RO_FILE + "something",
    S3_RO_DIR + "something",
    S3_RW_DIR + "something",

    FS_RO_DIR_NO_SLASH + "/something",
    FS_RW_DIR_SLASH + "something",
    FS_RO_FILE + "something",
    FS_RW_FILE + "something",
]

CAN_PULL = [
    GS_RO_FILE,
    S3_RO_FILE2,
    HTTPS_RO_FILE,
    #    GS_RO_SMALL_DIR, // todo fix pull of directories for gs. See issue #366
    S3_RO_SMALL_DIR
]

CAN_NOT_PULL = [
    "https://storage.googleapis.com/gisaia-public/test-aias/cog.tiff",
    "gs://gisaia-public/test-aias/cog.tiff",
    "https://raw.githubusercontent.com/gisaia/something/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md"
]


CAN_PUSH_ON = [
    S3_RW_DIR + "pushed"
]


CAN_NOT_PUSH_ON = [
    S3_RO_DIR + "pushed",
    S3_RO_DIR_SLASH + "pushed",
    S3_RO_DIR_NO_SLASH + "/pushed",
    "https://raw.githubusercontent.com/gisaia/ARLAS-Exploration-stack/adbfe2df1699df1fecc161fdb4464fcd07ad6235/docs/docs/version.md",
    GS_RO_DIR_SLASH + "pushed",
    GS_RO_DIR_NO_SLASH + "/pushed",
]


###########################
# FIXTURES
###########################

@pytest.fixture(scope="class")
def fixture_am():
    shutil.rmtree(FS_RO_DIR_NO_SLASH, ignore_errors=True, onerror=None)
    shutil.rmtree(FS_RW_DIR_SLASH, ignore_errors=True, onerror=None)
    os.makedirs(FS_RO_DIR_NO_SLASH, exist_ok=True)
    os.makedirs(FS_RW_DIR_SLASH, exist_ok=True)
    Path(FS_RO_FILE).touch()
    Path(FS_RW_FILE).touch()

    minios3conf = s3.S3StorageConfiguration(bucket="downloads", endpoint="http://" + MINIO_HOST + ":9000", readable_paths=["readwrite", "readonly"], writable_paths=["readwrite", "readonly"])
    minios3 = s3.S3Storage(minios3conf)
    minios3.push(FS_RO_FILE, S3_RO_DIR + "a_file")
    minios3.push(FS_RO_FILE, S3_RW_FILE)

    manager.AccessManager.init(AccessManagerSettings(
        storages=[
            s3.S3StorageConfiguration(bucket="downloads", endpoint="http://" + MINIO_HOST + ":9000", readable_paths=["readwrite", "readonly"], writable_paths=["readwrite"]),
            s3.S3StorageConfiguration(bucket="gisaia-public", endpoint="https://storage.googleapis.com", readable_paths=["/test-aias/ast", "test-aias/spot6"]),
            fs.FileStorageConfiguration(readable_paths=["/tmp/readonly"], writable_paths=["/tmp/readwrite"]),
            HttpsStorageConfiguration(domain="raw.githubusercontent.com", readable_paths=["/gisaia/ARLAS-Exploration-stack"], writable_paths=[]),
            gs.GoogleStorageConfiguration(bucket="gisaia-public", readable_paths=["/test-aias/ast", "test-aias/spot6"])
        ],
        tmp_dir="/tmp/readwrite"
    ))


@pytest.fixture(scope="class")
def fixture_objectstore() -> s3.S3Storage:
    return s3.S3Storage(s3.S3StorageConfiguration(bucket="downloads", endpoint="http://" + MINIO_HOST + ":9000", readable_paths=["readwrite", "readonly"], writable_paths=["readwrite"]))


###########################
# CAN READ
###########################

@pytest.mark.parametrize("href", CAN_READ)
def test_can_read(fixture_am, href: str):
    manager.AccessManager.check_path_readable(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_can_not_read(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.check_path_readable(href)


###########################
# CAN WRITE
###########################

@pytest.mark.parametrize("href", CAN_WRITE)
def test_can_write(fixture_am, href: str):
    manager.AccessManager.check_path_writable(href)


@pytest.mark.parametrize("href", CAN_NOT_WRITE)
def test_can_not_write(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.check_path_writable(href)


###########################
# EXISTS
###########################

@pytest.mark.parametrize("href", CAN_READ)
def test_exists(fixture_am, href: str):
    assert manager.AccessManager.exists(href)


@pytest.mark.parametrize("href", NOT_EXISTS)
def test_not_exists(fixture_am, href: str):
    assert not manager.AccessManager.exists(href)


###########################
# PULL
###########################

@pytest.mark.parametrize("href", CAN_PULL)
def test_pull(fixture_am, href: str):
    manager.AccessManager.pull(href, os.path.join(manager.AccessManager.tmp_dir, "pulled"))


@pytest.mark.parametrize("href", CAN_NOT_PULL)
def test_not_pull(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.pull(href, os.path.join(manager.AccessManager.tmp_dir, "pulled"))


###########################
# PUSH
###########################

@pytest.mark.parametrize("href", CAN_PUSH_ON)
def test_push(fixture_am, href: str):
    manager.AccessManager.push(FS_RO_FILE, href)


@pytest.mark.parametrize("href", CAN_NOT_WRITE)
def test_not_push(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.push(FS_RO_FILE, href)


@pytest.mark.parametrize("href", CAN_PUSH_ON)
async def test_push_fo(fixture_am, fixture_objectstore: s3.S3Storage, href: str):
    with open(FS_RO_FILE, 'rb') as fo:
        await fixture_objectstore.async_push_file_obj(fo, href)


@pytest.mark.parametrize("href", CAN_NOT_WRITE)
def test_not_push_fo(fixture_am, fixture_objectstore: s3.S3Storage, href: str):
    with pytest.raises(PermissionError):
        with open(FS_RO_FILE, 'rb') as fo:
            fixture_objectstore.async_push_file_obj(fo, href)


###########################
# IS FILE / DIR
###########################

@pytest.mark.parametrize("href", FILES)
def test_is_file(fixture_am, href: str):
    assert manager.AccessManager.is_file(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_is_file_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.is_file(href)


@pytest.mark.parametrize("href", DIRS)
def test_is_dir(fixture_am, href: str):
    assert manager.AccessManager.is_dir(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_is_dir_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.is_dir(href)


###########################
# GET SIZE
###########################

@pytest.mark.parametrize("href", GET_SIZE)
def test_get_size(fixture_am, href: str):
    manager.AccessManager.get_size(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_get_size_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.get_size(href)


###########################
# LIST DIR
###########################

@pytest.mark.parametrize("href", DIRS)
def test_listdir(fixture_am, href: str):
    manager.AccessManager.listdir(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_listdir_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.listdir(href)


###########################
# GET DATES
###########################

@pytest.mark.parametrize("href", FILES)
def test_get_last_modification_time(fixture_am, href: str):
    print(manager.AccessManager.get_last_modification_time(href))


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_get_last_modification_time_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.get_last_modification_time(href)


@pytest.mark.parametrize("href", FILES)
def test_get_creation_time(fixture_am, href: str):
    print(manager.AccessManager.get_creation_time(href))


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_get_creation_time_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.get_creation_time(href)


###########################
# MKDIR
###########################

@pytest.mark.parametrize("href", MKDIRS)
def test_makedir(fixture_am, href: str):
    manager.AccessManager.makedir(href)


@pytest.mark.parametrize("href", CAN_NOT_WRITE)
def test_makedir_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.makedir(href)


###########################
# DIRNAME
###########################

@pytest.mark.parametrize("href", DIRS)
def test_dirname(fixture_am, href: str):
    manager.AccessManager.dirname(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_dirname_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.dirname(href)


###########################
# CLEAN
###########################

@pytest.mark.parametrize("href", CAN_CLEAN)
def test_clean(fixture_am, href: str):
    print(href)
    manager.AccessManager.clean(href)


@pytest.mark.parametrize("href", CAN_NOT_CLEAN)
def test_clean_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.clean(href)


###########################
# ZIP
###########################

@pytest.mark.parametrize("href", FILES)
def test_zip(fixture_am, href: str):
    manager.AccessManager.zip(href, FS_RW_DIR_SLASH + "file.zip")


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_zip_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.zip(href, FS_RW_DIR_SLASH + "file.zip")
