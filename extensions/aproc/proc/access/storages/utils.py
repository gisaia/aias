import os
import shutil

import requests


def requests_get(href: str, dst: str, is_dst_dir: bool, headers: dict):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(href, headers=headers, stream=True, verify=False)

    if is_dst_dir:
        # If it is a directory, then add filename at the end of the path to match shutil.copy behaviour
        dst = os.path.join(dst, os.path.basename(href))

    with open(dst, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)


def requests_exists(href: str, headers: dict):
    r = requests.head(href, headers=headers, verify=False)
    return r.status_code >= 200 and r.status_code < 300
