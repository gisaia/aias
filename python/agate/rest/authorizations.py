import requests
from agate.logger import Logger
from agate.settings import Configuration, Rule
import jwt
from urllib import parse
import re

LOGGER = Logger.get_logger()


class Authorizations:

    keys: dict = {}

    @staticmethod
    def load_keys_from_jwks_uri(jwks_uri: str, verify_ssl: bool = True):
        """ Retrieve the JWKS from the uri and return a dictionary of keys indexed by their kid.

        Args:
            jwks_uri (str): The JWKS uri (e.g. https://www.googleapis.com/oauth2/v3/certs)

        Raises:
            Exception: If the JWKS can not be retrieved.

        Returns:
            dict: A dictionary of keys indexed by their kid.
        """
        r = requests.get(jwks_uri, verify=verify_ssl)
        if r.status_code == 200:
            jwks = r.json()
            LOGGER.debug(f"Loading JWKS from {jwks_uri}")
            from jwt.algorithms import RSAAlgorithm
            for e in jwks.get("keys", []):
                Authorizations.keys[e['kid']] = RSAAlgorithm.from_jwk(e)
        else:
            raise Exception(f"Unable to retrieve JWKS from {jwks_uri}, status code {r.status_code}")

    @staticmethod
    def get_user_roles(authorization: str) -> list[str]:
        """Extract user roles from a JWT authorization token.

        This method decodes a JWT token from the authorization header and extracts
        the roles assigned to the user from the token's resource_access section.

        Args:
            authorization (str): The authorization header value (e.g., "Bearer <token>").

        Returns:
            list[str]: A list of roles assigned to the user. Returns an empty list if no roles are found.

        Example:
            >>> get_user_roles("Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
            ['admin', 'user']

        Note:
            - If JWT verification is disabled (Configuration.settings.verify_jwt=False),
              the token is decoded without signature verification (warning issued).
            - If JWT verification is enabled, the method uses the appropriate key from
              the loaded JWKS based on the token's key ID (kid) to verify the signature.
        """
        encoded_token = authorization.removeprefix("Bearer ").removeprefix("bearer ")
        if not Configuration.settings.urbac.verify_jwt:
            token = jwt.decode(encoded_token, options={"verify_signature": False})
            LOGGER.warning("JWT verification is disabled, this should never be the case in production.")
        else:
            jwt_headers = jwt.get_unverified_header(encoded_token)
            LOGGER.debug("Key ring contains keys: {}".format(", ".join(Authorizations.keys.keys())))
            key = Authorizations.keys.get(jwt_headers['kid'])
            if key:
                LOGGER.debug("check token with audience {} and algorithm {}".format(Configuration.settings.urbac.jwt_audience, jwt_headers['alg']))
                token = jwt.decode(encoded_token, key, audience=Configuration.settings.urbac.jwt_audience.split(","), algorithms=[jwt_headers['alg']])
            else:
                msg = "Key {} not found".format(jwt_headers['kid'])
                raise Exception(msg)
        return token.get("resource_access", {}).get("arlas-backend", {}).get("roles", [])

    @staticmethod
    def extract_url_part(rule: Rule, requested_path: str) -> str | None:
        if rule.part is None or rule.part == "path":
            return requested_path
        if rule.part.startswith("query."):
            param_name = rule.part.split(".")[1]
            LOGGER.debug("Using query parameter {} as target".format(param_name))
            query = parse.urlparse(requested_path).query
            param = parse.parse_qs(query).get(param_name)
            if param is None or len(param) < 1:
                msg = "Parameter {} not found in query {}".format(param_name, query)
                LOGGER.error(msg)
                return None
            else:
                param = param[0]
            LOGGER.debug("{}={}".format(param_name, param))
            if rule.part.endswith(".path") or rule.part.endswith(".query"):
                url: parse.ParseResult = parse.urlparse(param)
                if rule.part.endswith(".url.path"):
                    LOGGER.debug("Using path of url {} as target".format(param))
                    return url.path
                elif rule.part.endswith(".url.query"):
                    LOGGER.debug("Using query of url {} as target".format(param))
                    return url.query
            else:
                LOGGER.debug("Using query parameter {} as target".format(param_name))
                return parse.urlparse(requested_path).query
        else:
            msg = "Invalid configuration '{}' for pattern_target".format(rule.part)
            LOGGER.error(msg)
            return None
        LOGGER.warning("Should not happen: no part extracted")
        return None

    @staticmethod
    def at_least_one_rule_match_on_path(rules: list[Rule], path: str, arlas_control: bool = True, headers: dict[str, str] = {}) -> bool:
        """Check if at least one rule in the provided list matches the given path.

        This method iterates through the provided rules and checks if any of them
        match the specified path using regular expression patterns. It uses the
        extract_url_part method to determine which part of the path to match against.
        If arlas_control activated, then the collection and item id are used for
        searching the hit on ARLAS with the user token. The rule matches if at least
        one hit is returned.

        Args:
            rules (list[Rule]): A list of Rule objects containing patterns to match against.
            path (str): The path to check against the rules.

        Returns:
            bool: True if at least one rule matches the path, False otherwise.

        Note:
            - The method returns False immediately if no part can be extracted from the path
              according to the rule configuration.
            - Matching is performed using re.finditer with pattern matching and searchs on ARLAS
              if arlas_control is True.
        """
        for rule in rules:
            part = Authorizations.extract_url_part(rule, path)
            if part:
                LOGGER.debug("Using {} as target for pattern matching on {}".format(part, rule.pattern))
            else:
                msg = "Unable to identify the URL part for pattern matching with rule '{}'".format(rule)
                LOGGER.warning(msg)
                continue
            matches = re.finditer(pattern=rule.pattern, string=part)
            for match in matches:
                if match.start() == 0:
                    LOGGER.debug("{} matches pattern {}".format(part, rule.pattern))
                    if not arlas_control:
                        return True
                    else:
                        try:
                            r = requests.get(Configuration.settings.arlas_url_search.format(collection=match.group("collection"), item=match.group("item")), headers=headers)
                            if r.ok:
                                response = r.json()
                                if response["hits"] is not None and len(response["hits"]) > 0:
                                    LOGGER.debug("ARLAS returned {} result(s) for {}".format(len(response["hits"]), part))
                                    return True
                                else:
                                    LOGGER.debug("ARLAS returned zero results for {}".format(part))
                            else:
                                LOGGER.error("ARLAS failed to answer {}: {}".format(str(r.status_code), str(r.content)))
                                LOGGER.error("  with headers {}".format(headers))
                        except Exception as e:
                            LOGGER.exception(e)
                else:
                    LOGGER.debug("{} does not match pattern {} at position 0".format(part, rule.pattern))
            LOGGER.debug("{} does not match {}".format(rule.pattern, part))
        return False
