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
        keys = copy_v.keys()
        if "title" in keys:
            result["title"] = copy_v["title"]
            del copy_v["title"]
        if "description" in keys:
            result["description"] = copy_v["description"]
            del copy_v["description"]
        if "keywords" in keys:
            result["keywords"] = copy_v["keywords"]
            del copy_v["keywords"]
        if "metadata" in keys:
            result["metadata"] = copy_v["metadata"]
            del copy_v["metadata"]
        if "additionalParameters" in keys:
            result["additionalParameters"] = copy_v["additionalParameters"]
            del copy_v["additionalParameters"]

        # If there is a default value, then the value is NOT required
        if "default" in keys:
            result["minOccurs"] = 0
        else:
            result["minOccurs"] = 1
        # Only one of each paramater. Otherwise it would be a list
        result["maxOccurs"] = 1

        # Parameters associated with a list input
        if "min_length" in copy_v.keys():
            result["minItems"] = copy_v["min_length"]
        if "max_length" in keys:
            result["maxItems"] = copy_v["max_length"]

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


def add_msg_to_text(message: str, messages: str) -> str:
    if messages:
        messages = messages + "; " + message
    else:
        messages = message
    return messages
