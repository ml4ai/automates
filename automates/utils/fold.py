"""Helper function for pretty-printing Gromet Json output.
Example:
{
    "function_networks": [
        {
            "B": [{"name":"module","type":"Module"}],
            "BF": [{"contents":1,"name":"","type":"Expression"}],
            "POF": [{"box":0,"name":"x"}]
        },
        {
            "B": [{"name":"","type":"Expression"}],
            "BF": [{"name":"","type":"LiteralValue","value":{"value":2,"value_type":"Integer"}}],
            "OPO": [{"box":0,"name":"x"}],
            "POF": [{"box":0,"name":""}],
            "WFOPO": [{"src":0,"tgt":0}]
        }
    ]
}
"""

import sys
import json


def dictionary_to_gromet_json(o, fold_level=3, indent=4, level=0):
    if level < fold_level:
        newline = "\n"
        space = " "
    else:
        newline = ""
        space = ""
    ret = ""
    if isinstance(o, str):
        ret += '"' + o + '"'
    elif isinstance(o, bool):
        ret += "true" if o else "false"
    elif isinstance(o, float):
        ret += '%.7g' % o
    elif isinstance(o, int):
        ret += str(o)
    elif isinstance(o, list):
        ret += "[" + newline
        comma = ""
        for e in o:
            ret += comma
            comma = "," + newline
            ret += space * indent * (level+1)
            ret += dictionary_to_gromet_json(e, fold_level, indent, level+1)
        ret += newline + space * indent * level + "]"
    elif isinstance(o, dict):
        ret += "{" + newline
        comma = ""
        for k, v in sorted(o.items()):
            ret += comma
            comma = "," + newline
            ret += space * indent * (level+1)
            ret += '"' + str(k) + '":' + space
            ret += dictionary_to_gromet_json(v, fold_level, indent, level+1)
        ret += newline + space * indent * level + "}"
    elif o is None:
        ret += "null"
    else:
        ret += str(o)
    return ret