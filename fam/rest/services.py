import datetime
import os

from fastapi import APIRouter, HTTPException, status

from fam.core.fam import Fam
from fam.core.model import Archive, File, PathRequest
from fam.core.settings import Configuration

ROUTER = APIRouter()
MAX_SIZE = 1000


@ROUTER.get("/root", response_model=File)
async def root():
    return File(
        name=Configuration.settings.inputs_directory,
        path=Configuration.settings.inputs_directory,
        is_dir=os.path.isdir(Configuration.settings.inputs_directory),
        last_modification_date=datetime.datetime.fromtimestamp(os.path.getmtime(Configuration.settings.inputs_directory)),
        creation_date=datetime.datetime.fromtimestamp(os.path.getctime(Configuration.settings.inputs_directory)))


@ROUTER.post("/files", response_model=list[File])
async def files(path_request: PathRequest):
    file_path = path_request.path
    __check_file_path__(file_path)
    if os.path.isdir(file_path):
        files: list[str] = os.listdir(file_path)
        return list(map(lambda f: File(name=f, path=os.path.join(file_path, f), is_dir=os.path.isdir(os.path.join(file_path, f)), last_modification_date=datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(file_path, f))), creation_date=datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(file_path, f)))), filter(lambda f: not os.path.basename(f).startswith("."), files)))
    else:
        f = os.path.basename(file_path)
        return [File(name=f, path=file_path, is_dir=False, last_modification_date=datetime.datetime.fromtimestamp(os.path.getmtime(file_path)), creation_date=datetime.datetime.fromtimestamp(os.path.getctime(file_path)))]


@ROUTER.post("/archives", response_model=list[Archive])
async def archives(path_request: PathRequest):
    path_request.size = min(path_request.size, MAX_SIZE)
    file_path = path_request.path
    __check_file_path__(file_path)
    return Fam.list_archives(file_path, max_size=path_request.size)


def __check_file_path__(file_path: str):
    if file_path and file_path.find("..") > -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File path can not contain '..' ({})".format(file_path))
    if not file_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File path must be provided. Root is at {}".format(Configuration.settings.inputs_directory))
    if not file_path.startswith(Configuration.settings.inputs_directory):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File path ({}) must be start with the root prefix ({}).".format(file_path, Configuration.settings.inputs_directory))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File {} not found".format(file_path))
