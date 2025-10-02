import requests
from agate.logger import Logger

LOGGER = Logger.logger


class KeyRing:

    keys: dict = {}

    @staticmethod
    def load_from_openid_configuration(uri: str, verify_ssl: bool = True):
        """ Retrieve the JWKS from the OpenID configuration located at uri and return a dictionary of keys indexed by their kid.

        Args:
            uri (str): The OpenID configuration uri (e.g. https://accounts.google.com/.well-known/openid-configuration)

        Raises:
            Exception: If the OpenID configuration or the JWKS can not be retrieved.

        Returns:
            dict: A dictionary of keys indexed by their kid.
        """
        LOGGER.debug(f"Retrieving OpenID configuration from {uri}")
        r = requests.get(uri, verify=verify_ssl)
        if r.status_code == 200:
            jwks_uri = r.json().get("jwks_uri")
            if jwks_uri:
                r = requests.get(jwks_uri, verify=verify_ssl)
                if r.status_code == 200:
                    jwks = r.json()
                    LOGGER.debug(f"Loading JWKS from {jwks_uri}")
                    from jwt.algorithms import RSAAlgorithm
                    for e in jwks.get("keys", []):
                        KeyRing.keys[e['kid']] = RSAAlgorithm.from_jwk(e)
                else:
                    raise Exception(f"Unable to retrieve JWKS from {jwks_uri}, status code {r.status_code}")
            else:
                raise Exception(f"No jwks_uri found in the OpenID configuration from {uri}")
        else:
            raise Exception(f"Unable to retrieve JWKS from {uri}, status code {r.status_code}")
