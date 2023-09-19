from aproc.core.models.ogc import Execute, BinaryInputValue, Bbox


def execute2inputs(execute: Execute):
    result = {}
    for key, input in execute.inputs.items():
        if isinstance(input.__root__.__root__, BinaryInputValue | Bbox):
            result[key] = input.__root__.__root__.__root__
        else:
            result[key] = input.__root__.__root__
    return result
