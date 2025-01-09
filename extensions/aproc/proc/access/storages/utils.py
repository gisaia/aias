import os
import shutil

import requests


def requests_get(href: str, dst: str, headers: dict):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(href, headers=headers, stream=True, verify=False)

    if os.path.isdir(dst):
        # If it is a directory, then add filename at the end of the path to match shutil.copy behaviour
        dst = os.path.join(dst, os.path.basename(dst))

    with open(dst, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)


def requests_exists(href: str, headers: dict):
    r = requests.head(href, headers=headers, verify=False)
    return r.status_code >= 200 and r.status_code < 300
