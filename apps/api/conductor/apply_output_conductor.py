# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.api.conductor.model_format import ModelFormat
from apps.api.conductor.value_conductor import ValueConfigerConductor


class OutputReader(object):
    @staticmethod
    def read_output(provider, key, define, result, resource_value_config):
        '''

        :param key:
        :param define:
        example: cidr replace cidr_block
        define:  cidr_block
                or: {"value": "cidr_block", "type": "string"}
        :param result:
        :return:
        '''

        add_infos = {}
        if (define is None):
            logger.info("output %s define is null" % key)
            return {}
        if isinstance(define, basestring):
            value = result
        elif isinstance(define, dict):
            client = ModelFormat
            value = client.format_type(result, type=define.get("type", "string"))
            value, add_infos = client.hint_outer_infos(provider, value, define)
        else:
            raise ValueError("转换配置错误， 类型错误")

        if value:
            value = ValueConfigerConductor.outer_value(value, resource_value_config)

        add_infos[key] = value
        return add_infos


def read_output_result(provider, result, models, resource_values_config):
    '''
    对于设置了output的属性， 则提取output输出值
    :param result:
    :return:
    '''

    if models:
        result_output = result.get("outputs")

        ext_result = {}
        for column, res in result_output.items():
            _out_dict = OutputReader.read_output(provider=provider,
                                                 key=column, define=models.get(column),
                                                 result=res.get("value"),
                                                 resource_value_config=resource_values_config.get(column))
            ext_result.update(_out_dict)

        if "resource_id" in ext_result.keys():
            if len(ext_result["resource_id"]) > 512:
                ext_result["resource_id"] = ext_result["resource_id"][:512]
                logger.info("resource id length more than 512, will truncated for resource_id")

        logger.info(format_json_dumps(ext_result))
        return ext_result

    return {}
