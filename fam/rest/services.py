import datetime
import os

from fastapi import APIRouter, HTTPException, status

from fam.core.model import File
from fam.core.settings import Configuration

ROUTER = APIRouter()


@ROUTER.post("/files", response_model=list[File])
async def files(file_path: str = ""):
    if file_path and file_path.find("..") > -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File path can not contain '..' ({})".format(file_path))
    if not file_path:
        file_path = ""
    full_path = os.path.join(Configuration.settings.inputs_directory, file_path)
    print(full_path)
    if os.path.exists(full_path):
        if os.path.isdir(full_path):
            files: list[str] = os.listdir(full_path)
            return list(map(lambda f: File(name=f, path=os.path.join(file_path, f), is_dir=os.path.isdir(os.path.join(full_path, f)), last_modification_date=datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(full_path, f))), creation_date=datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(full_path, f)))), files))
        else:
            f = os.path.basename(full_path)
            return [File(name=f, path=full_path, is_dir=False, last_modification_date=datetime.datetime.fromtimestamp(os.path.getmtime(full_path)), creation_date=datetime.datetime.fromtimestamp(os.path.getctime(full_path)))]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File {} not found".format(file_path))


@ROUTER.post("/archives", response_model=list[File])
async def archives(file_path: str = ""):
    if file_path and file_path.find("..") > -1:
        raise Exception("File path can not contain '..' ({})".format(file_path))
    if not file_path:
        file_path = ""
    full_path = os.path.join(Configuration.settings.inputs_directory, file_path)
