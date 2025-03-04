import io
import re
import zipfile
from typing import Pattern

from extensions.aproc.proc.dc3build.model.dc3build_input import InputDC3BuildProcess


# TODO: find a better place for the method?
def find_raster_files(fb: str | io.TextIOWrapper, regex: Pattern[str], alias=None) -> dict[str, str]:
    """
    From a zip archive, extract a dictionary of band -> path matching the input regex.
    The regex must have exactly one capturing group
    """
    bands: dict[str, str] = {}
    with zipfile.ZipFile(fb) as zip:
        file_names = zip.namelist()
        for f_name in file_names:
            match = re.match(regex, f_name)
            if match:
                key = match.group(1)
                if alias is not None:
                    key = alias + '.' + key
                bands[key] = f_name

    return bands


def get_eval_formula(band_expression: str,
                     aliases: set[str]) -> str:
    """
    Transform the requested expression of the band in a xarray operation
    """
    def repl(match: re.Match[str]) -> str:
        for m in match.groups():
            return f"datacube.get('{m}')"

    result = band_expression
    for alias in aliases:
        result = re.sub(rf"({alias}\.[a-zA-Z0-9]*)", repl, result)

    return result


def get_all_aliases(request: InputDC3BuildProcess) -> set[str]:
    """
    Get all unique aliases nested in the request's composition
    """
    aliases: set[str] = set()
    for g in request.composition:
        for r in g.dc3__references:
            aliases.add(r.dc3__alias)
    return aliases
