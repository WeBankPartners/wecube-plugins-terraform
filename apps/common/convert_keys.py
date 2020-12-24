# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json


def _validate_type(value, type):
    '''

    :param value:
    :param type:
    :return:
    '''

    if (type == "string") and (not isinstance(value, basestring)):
        raise ValueError("%s 不是string" % value)
    elif (type == "int") and not isinstance(value, int):
        try:
            value = int(value)
        except:
            raise ValueError("%s 不是int" % value)
    elif (type == "float") and (not isinstance(value, float)):
        try:
            value = float(value)
        except:
            raise ValueError("%s 不是浮点类型" % value)
    elif (type == "json") and (not isinstance(value, dict)):
        try:
            value = json.loads(value)
        except:
            raise ValueError("%s 不是json" % value)
    elif (type == "list") and (not isinstance(value, list)):
        try:
            value = json.loads(value)
        except:
            raise ValueError("%s 不是list类型" % value)
    else:
        raise ValueError("未知的类型约束 %s" % type)

    return value


def convert_key(key, value, define):
    '''

    :param key:
    :param value:
    :param define:  {
    "type": "string",
    "convert": "access_key",
    "allow_null": 1,
    "default": ""
    }
    :return:
    '''

    if (value is None) and (not define.get("allow_null", 1)):
        raise ValueError("key %s 不允许为空" % key)
    if not value:
        value = define.get("default") or value
    else:
        value = _validate_type(value, type=define.get("type", "string"))

    if define.get("convert"):
        key = define.get("convert") or key

    return {key: value}


def convert_datas(datas, defines):
    '''

    :param datas:
    :param defines:
    :return:
    '''

    result = {}
    for key, value in datas.items():
        if defines.get(key):
            result.update(convert_key(key, value, define=defines[key]))
        else:
            result.update({key, value})

    return result


def convert_value(value, define):
    '''

    :param value:
    :param define:  string or json
    example: cider replace cider_block
    define:  cider_block
            or: {"value": "cider_block", "type": "string"}
    :return:
    '''

    if (value is None) or (define is None):
        return value
    if isinstance(define, basestring):
        value = define or define
    elif isinstance(define, dict):
        value = define.get("value", value) or value
        value = _validate_type(value, define.get("type", "string"))
    else:
        raise ValueError("转换配置错误， 类型错误")

    return value


def convert_values(data, define):
    '''

    :param data: example: {"cider"： "cider_8"}
    :param define: {"cider_8": {"type": "string", "vlue": "192.168.8.0/20"}}
    :return:
    '''

    res = {}
    for key, value in data.items():
        res[key] = convert_value(value, define.get(value))

    return res

