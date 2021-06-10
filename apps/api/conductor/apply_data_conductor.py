# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from apps.api.conductor.type_format import TypeFormat
from apps.api.conductor.model_format import ModelFormat

client = ModelFormat


def _validate_apply_data(provider, key, value, define, resource_value_config, resource_name):
    '''
    转换传入的数据的key 以及 value映射值

    :param key:
    :param value:
    :param define:  string or json
        {
        "type":"string",
        "convert":"access_key",
        "allow_null":1,
        "default":"",
        "define":{
            }
        }
    :return:
    '''

    if not define:
        return {}

    if isinstance(define, basestring):
        if define == '-' or not define.strip():
            return {}

        if value is not None:
            value = client.convert_apply_value(value, resource_value_config)
        key = define or key
    else:
        value = client.format_apply_value(key, value, define)
        if value:
            value = client.convert_apply_value(value, resource_value_config)
            value = client.format_type(value, type=define.get("type", "string"))
            if isinstance(value, list):
                # for list after format, may need revert value
                value = client.convert_apply_value(value, resource_value_config)
            value = client.hint_apply_infos(provider, value, define, resource_name)

        if define.get("convert"):
            key = define.get("convert") or key

    if value:
        return {key: value}
    elif isinstance(value, (int, bool)):
        return {key: value}
    else:
        return {}


def apply_data_builder(provider, datas, defines, resource_values_config, resource_name):
    '''
    依据resource定义， 转换字段， 转换value值， 生成apply resource 数据
    {
    "type":"string",
    "convert":"access_key",
    "allow_null":1,
    "default":"",
    "hint":"$resource.vpc/$resource",
    "define":{
         }
    }
    :param provider:
    :param datas:
    :param defines:
    :param resource_values_config:
    :return:
    '''
    result = {}
    logger.info("apply_builder ... ")
    for key, define in defines.items():
        # 依据定义字段转换，只转换defines中的字段，检查必要字段的传入，未定义字段移除
        if isinstance(define, dict) and define.get("define"):
            if datas.get(key):
                value = TypeFormat.f_dict(datas.get(key))
            else:
                value = apply_data_builder(provider=provider,
                                           datas=datas, defines=define.get("define"),
                                           resource_values_config=resource_values_config,
                                           resource_name=resource_name)
            if value:
                result[key] = value
        else:
            _t = _validate_apply_data(provider=provider, key=key,
                                      value=datas.get(key), define=define,
                                      resource_value_config=resource_values_config.get(key, {}),
                                      resource_name=resource_name)
            if _t:
                for xkey, xvalue in _t.items():
                    if xkey in result.keys():
                        if isinstance(xvalue, list) and isinstance(result.get(xkey), list):
                            xtmp = xvalue + result.get(xkey)
                            result[xkey] = list(set(xtmp))
                        elif isinstance(xvalue, list) or isinstance(result.get(xkey), list):
                            raise ValueError("key -> %s 存在映射同一字段，类型不统一， 请检查" % xkey)
                        else:
                            result[xkey] = xvalue
                    else:
                        result[xkey] = xvalue

    return result


def apply_output_builder(datas, defines):
    pass
