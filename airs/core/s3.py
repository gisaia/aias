from boto3 import Session

from airs.core.settings import Configuration

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

def get_matching_s3_objects(bucket, prefix="", suffix="")->str:
    """
    Generate objects in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional) or any of these prefixes if a list/tuple is provided.
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional) or any of these suffixes if a list/tuple is provided.
    Yields:
        _type_: yealds keys (str)

    """

    s3 = get_client()
    paginator = s3.get_paginator("list_objects_v2")

    kwargs = {'Bucket': bucket}

    # We can pass the prefix directly to the S3 API.  If the user has passed
    # a tuple or list of prefixes, we go through them one by one.
    if isinstance(prefix, str):
        prefixes = (prefix, )
    else:
        prefixes = prefix

    for key_prefix in prefixes:
        kwargs["Prefix"] = key_prefix

        for page in paginator.paginate(**kwargs):
            try:
                contents = page["Contents"]
            except KeyError:
                break

            for obj in contents:
                key = obj["Key"]
                if key.endswith(suffix):
                    yield key


def get_matching_s3_keys(bucket, prefix="", suffix=""):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        yield obj["Key"]