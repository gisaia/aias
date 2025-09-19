import shutil

import requests


def requests_get(href: str, dst: str, headers: dict):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(href, headers=headers, stream=True, verify=False)  # NOSONAR

    with open(dst, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)


def requests_head(href: str, headers: dict) -> requests.Response:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    r = requests.head(href, headers=headers, verify=False)  # NOSONAR
    return r


def requests_exists(href: str, headers: dict) -> bool:
    r = requests_head(href, headers)
    print("request on  {}".format(href))
    return r.status_code >= 200 and r.status_code < 300


def remote_path_starts_with(path: str, prefix: str) -> bool:
    """
    Check whether a remote path (e.g., a cloud storage URI) is under a given prefix.

    This function normalizes both `path` and `prefix` by stripping trailing slashes,
    then checks whether `path` is exactly equal to `prefix` or is a subpath of it.

    Parameters:
        path (str): The full remote path to check, e.g., "gs://bucket/folder/file.txt".
        prefix (str): The expected prefix path, e.g., "gs://bucket/folder".

    Returns:
        bool: True if `path` is equal to or is a subpath of `prefix`, False otherwise.
    """
    path = path.rstrip("/")
    prefix = prefix.rstrip("/")
    return path == prefix or path.startswith(prefix + "/")
