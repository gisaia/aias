import contextlib
import shutil
import warnings

import requests
from urllib3.exceptions import InsecureRequestWarning

old_merge_environment_settings = requests.Session.merge_environment_settings


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
    return r.status_code >= 200 and r.status_code < 300


# Taken from https://stackoverflow.com/questions/15445981/how-do-i-disable-the-security-certificate-check-in-python-requests
@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except Exception:
                pass
