import shutil

import requests


def requests_get(href: str, dst: str, headers: dict):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(href, headers=headers, stream=True, verify=False)

    with open(dst, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)


def requests_exists(href: str, headers: dict):
    r = requests.head(href, headers=headers, verify=False)
    return r.status_code >= 200 and r.status_code < 300
