import json
import textwrap
from aeoprs.core.models.model import Item

def __short_titles(o):
    if type(o) is dict:
        d={}
        for key in o:
            if key == "title" and isinstance(o[key], str):
                d[key]=textwrap.shorten(o[key],220)
            else:
                d[key]=__short_titles(o[key])                   
        return d
    if type(o) is list:
        return list(map(lambda elt:__short_titles(elt), o))
    else:
        return o

if __name__ == '__main__':
    model=__short_titles(Item.model_json_schema())
    model["$id"]="aeopres_model"
    print(json.dumps(model))
