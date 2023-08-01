from boto3 import Session

from aeoprs.core.settings import Configuration

__session=None

def get_session()->Session:
    global __session
    if __session is None:
        __session = Session(
            aws_access_key_id=Configuration.settings.s3.access_key_id,
            aws_secret_access_key=Configuration.settings.s3.secret_access_key,
            region_name=Configuration.settings.s3.region
        )
    return __session

def get_client():
    if Configuration.settings.s3.endpoint_url is not None:
        return get_session().client("s3", endpoint_url=Configuration.settings.s3.endpoint_url)
    else:
        return get_session().client("s3")
