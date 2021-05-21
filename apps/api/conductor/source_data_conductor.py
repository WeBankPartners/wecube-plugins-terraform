# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from apps.api.conductor.type_format import TypeFormat
from apps.api.conductor.model_format import ModelFormat

client = ModelFormat


def _validate_query_data(provider, key, value, define, resource_value_config):
    '''


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
        if define.strip() == '-' or not define.strip():
            return {}

        key = define or key
    else:
        value = client.format_query_value(key, value, define)
        if value:
            value = client.convert_apply_value(value, resource_value_config)
            value = client.format_type(value, type=define.get("type", "string"))
            if isinstance(value, list):
                # for list after format, may need revert value
                value = client.convert_apply_value(value, resource_value_config)
            value = client.hint_apply_infos(provider, value, define)

        if define.get("convert"):
            key = define.get("convert") or key

    if value:
        return {key: value}
    elif isinstance(value, (int, bool)):
        return {key: value}
    else:
        return {}


def query_data_builder(provider, datas, defines, resource_values_config):
    '''

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
    logger.info("query_builder ... ")

    for key, define in defines.items():
        # 依据定义字段转换，只转换defines中的字段，检查必要字段的传入，未定义字段移除
        if isinstance(define, dict) and define.get("define"):
            if datas.get(key):
                value = TypeFormat.f_dict(datas.get(key))
            else:
                value = query_data_builder(provider=provider,
                                           datas=datas, defines=define.get("define"),
                                           resource_values_config=resource_values_config)
            if value:
                result[key] = value
        else:
            _t = _validate_query_data(provider=provider, key=key,
                                      value=datas.get(key), define=define,
                                      resource_value_config=resource_values_config.get(key))
            if _t:
                result.update(_t)

    return result


def query_return_builder(data, defines, results):
    add_columns = {}
    for key, define in defines:
        if isinstance(define, dict):
            if define.get("return") in [True, 1, '1', 'true', 'True']:
                add_columns[key] = data.get(key)

    if isinstance(results, list):
        res = []
        for result in results:
            if isinstance(result, dict):
                result.update(add_columns)
            res.append(result)
        return res
    elif isinstance(results, dict):
        results.update(add_columns)
        return results
    else:
        return results
