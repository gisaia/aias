from jsonref import replace_refs
from pydantic import BaseModel

from aproc.core.models.ogc import (Bbox, BinaryInputValue, Execute,
                                   InputDescription, OutputDescription)


def base_model2description(model: type[BaseModel]) \
        -> dict[str, OutputDescription] | dict[str, InputDescription]:
    description: dict = replace_refs(model.model_json_schema())["properties"]

    for k, v in description.items():
        result = {}
        copy_v = {**v}

        # Keep all the attributes of inputDescription and outputDescription
        if "title" in copy_v.keys():
            result["title"] = copy_v["title"]
            del copy_v["title"]
        if "description" in copy_v.keys():
            result["description"] = copy_v["description"]
            del copy_v["description"]
        if "keywords" in copy_v.keys():
            result["keywords"] = copy_v["keywords"]
            del copy_v["keywords"]
        if "metadata" in copy_v.keys():
            result["metadata"] = copy_v["metadata"]
            del copy_v["metadata"]
        if "additionalParameters" in copy_v.keys():
            result["additionalParameters"] = copy_v["additionalParameters"]
            del copy_v["additionalParameters"]
        # Keep all the attributes of inputDescription
        if "minOccurs" in copy_v.keys():
            result["minOccurs"] = copy_v["minOccurs"]
            del copy_v["minOccurs"]
        if "maxOccurs" in copy_v.keys():
            result["maxOccurs"] = copy_v["maxOccurs"]
            del copy_v["maxOccurs"]

        result["schema"] = copy_v
        description[k] = {**result}

    return description


def execute2inputs(execute: Execute):
    result = {}
    for key, input in execute.inputs.items():
        if isinstance(input.root.root, BinaryInputValue | Bbox):
            result[key] = input.root.root.root
        else:
            result[key] = input.root.root
    return result
