# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.logs import logger


def validate_convert_key(defines):
    for key, define in defines.items():
        if (not isinstance(define, (basestring, dict))) or isinstance(define, list):
            raise ValueError("错误的定义 合法值为 string "
                             "或json:{'type': <type>, 'allow_null': <0/1>,"
                             "'convert': <value>, 'default':<value>}")

        if isinstance(define, dict):
            if define.get("type", "string") not in ["string", "json", "int", "float", "list"]:
                raise ValueError("未知的类型约束 %s" % define.get("type"))
            if define.get("allow_null", 1) not in [0, 1]:
                raise ValueError("allow_null 合法值为 0/1")


def validate_convert_value(defines):
    for key, define in defines.items():
        if not isinstance(define, (basestring, (basestring, bool, int, dict))):
            raise ValueError("错误的定义 合法值为 string/bool/int "
                             "或json:{'type': <type>, 'value':<value>}")

        if isinstance(define, dict):
            if define.get("type", "string") not in ["string", "json", "int", "float", "list"]:
                raise ValueError("未知的类型约束 %s" % define.get("type"))


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
            if isinstance(value, basestring):
                if value.startswith("["):
                    value = json.loads(value)
                elif "," in value:
                    value = value.split(",")
                elif ";" in value:
                    value = value.split(";")
                else:
                    _v = " ".join(value.split())
                    value = _v.split()
            else:
                raise ValueError()
        except:
            raise ValueError("%s 不是list类型" % value)
    else:
        pass

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

    if isinstance(define, basestring):
        if define == '-':
            return {}
        key = define or key
    else:
        if (value is None) and (not define.get("allow_null", 1)):
            raise ValueError("key %s 不允许为空" % key)
        if not value:
            value = define.get("default") or value
        else:
            value = _validate_type(value, type=define.get("type", "string"))

        if define.get("convert"):
            key = define.get("convert") or key

    if value:
        return {key: value}


def convert_keys(datas, defines, is_update=False):
    '''

    :param datas:
    :param defines:
    :return:
    '''

    result = {}
    if is_update:
        for key, value in datas.items():
            # 依据data数据进行字段， 如果字段未定义则异常
            if defines.get(key) is not None:
                result.update(convert_key(key, value, define=defines[key]))
            else:
                raise ValueError("未定义的关键词 %s, 若需移除关键词，则定义为 'key': '-'" % key)

        return result

    for key, define in defines.items():
        # 依据定义字段转换，只转换defines中的字段，检查必要字段的传入，未定义字段移除
        _t = convert_key(key, datas.get(key), define=define)
        if _t:
            result.update(_t)

    return result


def convert_value(value, define):
    '''

    :param value:
    :param define:  string or json
    example: cidr replace cidr_block
    define:  cidr_block
            or: {"value": "cidr_block", "type": "string"}
    :return:
    '''

    if (value is None) or (define is None):
        return value
    if isinstance(define, (basestring, bool, int)):
        value = define or value
    elif isinstance(define, dict):
        value = define.get("value", value) or value
        value = _validate_type(value, define.get("type", "string"))
    else:
        raise ValueError("转换配置错误， 类型错误")

    return value


def convert_values(data, define):
    '''

    :param data: example: {"cidr"： "cidr_8"}
    :param define: {"cidr_8": {"type": "string", "vlue": "192.168.8.0/20"}}
    :return:
    '''

    res = {}
    for key, value in data.items():
        res[key] = convert_value(value, define.get(value))

    return res


def convert_extend_propertys(datas, extend_info):
    '''

    :param datas:
    :param extend_info:
    :return:
    '''

    def allowed_key(keys, data):
        for key in keys:
            if key not in data:
                raise ValueError("不合法的参数%s" % key)

    if not extend_info:
        logger.info("extend info define is null, so extend keys will be removed")
        return {}

    ora_ext_info = {}
    allowed_key(datas.keys(), extend_info.keys())
    for key, define in extend_info.items():
        if isinstance(define, (int, basestring, int, float, bool)):
            ora_ext_info[key] = define
        elif isinstance(define, dict):
            if define.get("value") is not None:
                ora_ext_info[key] = define.get("value")
            if define.get("type") is not None and (key in datas.keys()):
                _validate_type(datas.get(key), type=define.get("type", "string"))

    ora_ext_info.update(datas)
    return ora_ext_info


def _format_type(value, type):
    if type == "string":
        value = str(value)
    elif type == "json":
        if not isinstance(value, list):
            try:
                value = json.loads(value)
            except Exception, e:
                raise ValueError("value is not json")
    elif type == "list":
        if not isinstance(value, list):
            value = [value]
    elif type == "int":
        try:
            value = int(value)
        except Exception, e:
            raise ValueError("value is not int")

    elif type == "float":
        try:
            value = float(value)
        except Exception, e:
            raise ValueError("value is not float")
    else:
        raise ValueError("不支持的output类型")

    return value


def output_value(key, define, result):
    '''

    :param value:
    :param define:  string or json
    example: cidr replace cidr_block
    define:  cidr_block
            or: {"value": "cidr_block", "type": "string"}
    :return:
    '''

    if (define is None):
        logger.info("output %s define is null" % key)
        return {}
    if isinstance(define, basestring):
        value = result.get(define)
    elif isinstance(define, dict):
        value = result.get(define.get("value"))
        value = _format_type(value, type=define.get("type", "string"))
    else:
        raise ValueError("转换配置错误， 类型错误")

    return {key: value}


def output_values(defines, result):
    res = {}
    for key, define in defines.items():
        res.update(output_value(key, define, result))

    return res


def define_relations_key(key, value, define):
    '''

    :param key:
    :param value:
    :param define:
    :return:
    '''

    if isinstance(define, basestring):
        if define == '-':
            return True
    else:
        if (not value) and (not define.get("allow_null", 1)):
            raise ValueError("key %s 不允许为空" % key)

    return False
