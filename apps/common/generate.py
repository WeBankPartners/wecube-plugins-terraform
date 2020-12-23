# -*- coding: utf-8 -*-

import json


def generate_data(value, model):
    if not model:
        return value
    type = model.get("type", "string").lower()
    value = model.get("value", value)
    if type == "string":
        return str(value)
    elif type == "int":
        return int(value)
    elif type == "float":
        return float(value)
    elif type == "list":
        return [value]
    elif type == "bool":
        if isinstance(value, bool):
            return value
        elif value == 0 or value.lower() == "false":
            return False
        elif value == 1 or value.lower() == "true":
            return True
        else:
            raise ValueError("不合法的bool类型值 %s" % value)
    elif type == "json":
        if isinstance(value, dict):
            return value
        else:
            return json.loads(value)

    raise ValueError("不支持的类型 %s" % type)
