# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import re
import json
import traceback
from lib.logs import logger
from apps.api.conductor.type_format import TypeFormat
from apps.api.conductor.model_format import ModelFormat
from apps.api.conductor.value_conductor import ValueConfigerConductor


class SourceOuterReader(object):
    @staticmethod
    def format_argument(key, data):
        if not data:
            return ""
        if isinstance(data, dict):
            return data
        elif isinstance(data, basestring):
            data = data.strip()
            if data.startswith("{"):
                data = TypeFormat.f_dict(data)

            return data
        else:
            raise ValueError("key: %s 应为json或string" % key)

    @staticmethod
    def is_null_dict(data):
        count = 0
        for _, x_value in data.items():
            if not x_value:
                count += 1
        if count == len(data):
            logger.info("out data columns is null, skip ...")
            return True

        return False

    @staticmethod
    def skip_empty_dict(datas):
        result = []
        for out_data in datas:
            if out_data:
                if isinstance(out_data, dict) and (not SourceOuterReader.is_null_dict(out_data)):
                    result.append(out_data)
                elif isinstance(out_data, (basestring, bool, int, float)):
                    result.append(out_data)

        return result

    @staticmethod
    def eval_line(line, column):
        def line_pointer(data):
            try:
                data = data[len("$line"):]
                nums = re.findall('\d+', data)
                if nums:
                    num = nums[0]
                    split_point = data.replace(num)
                    return split_point, int(num)
                else:
                    return None, None
            except:
                raise ValueError("$line define error, use: split + [num], example: $line / $line#2")

        if column == "$line":
            return line
        elif column.startswith("$line"):
            s_split, point = line_pointer(column)
            if s_split:
                try:
                    return line.split(s_split)[point]
                except:
                    raise ValueError("$line: %s 不能获取数据， 请检查定义" % column)
            else:
                return line
        else:
            logger.info("unknown define %s ,skip ..." % line)
            return ""

    @staticmethod
    def fetch_property(provider, key, data, define_column, resource_value_config, resource_name):
        '''

        提取 output 数据字段值
        :param provider:
        :param data:
        :param define_columns:
        string: {"desc": "$line"}
        dict: {"name": "name", "dns": {"type": "list", "convert": "dns_info"}}
        :param resource_value_config:
        :return:
        '''

        def _f_string_property_(data, key, column, resource_value_config):
            '''
            #处理data为string时字段提取
            {"desc": "$line", "port": "$line#2"}
            :param data:
            :param key:
            :param columns:
            :param resource_values_config:
            :return:
            '''

            x_value = ""
            if column.startswith("$"):
                x_value = SourceOuterReader.eval_line(line=data, column=column)
                if x_value:
                    x_value = resource_value_config.get(x_value) or x_value
            elif column == "-" or not column:
                return {}

            return {key: x_value}

        def _f_fetch_property(data, define):
            if "." in define:
                _keys = define.split(".")
                tmp = data
                for x_key in _keys:
                    try:
                        tmp = tmp[int(x_key)]
                    except:
                        tmp = tmp.get(x_key)

                x_data = tmp
            else:
                x_data = data.get(define) or ""

            return x_data

        def _f_dict_property_(provider, data, key, define, resource_value_config, resource_name):
            '''
            for dict
            :param data:
            :param define_columns:
            {"name": "name", "dns": {"type": "list", "convert": "dns_info"}}
            :param resource_value_config:
            :return:
            '''

            if not define:
                logger.info("key: %s define is empty, skip it .." % key)
                return {}

            if isinstance(define, basestring):
                if define == '-' or not define.strip():
                    logger.info("key: %s define ignore, skip it .." % key)
                    return {}

                value = _f_fetch_property(data, define)
                value = ValueConfigerConductor.outer_value(value, resource_value_config)
                return {key: value}
            else:
                to_column = define.get("convert") or key
                value = _f_fetch_property(data, to_column)
                value = ModelFormat.format_type(value, type=define.get("type", "string"))
                value = ValueConfigerConductor.outer_value(value, resource_value_config)

                # for hint 转换为资产id等信息
                value, add_info = ModelFormat.hint_outer_infos(provider, value, define, resource_name)
                add_info[key] = value
                return add_info

        if isinstance(data, basestring):
            return _f_string_property_(data=data, key=key,
                                       column=define_column,
                                       resource_value_config=resource_value_config)

        return _f_dict_property_(provider=provider, data=data,
                                 key=key, define=define_column,
                                 resource_value_config=resource_value_config,
                                 resource_name=resource_name)


def source_object_outer(datas, columns):
    if len(columns) == 0:
        c_data = []
        for data in datas:
            if isinstance(data, list):
                c_data += data
            else:
                c_data.append(data)

        return SourceOuterReader.skip_empty_dict(c_data)

    column = columns.pop(0)
    if isinstance(datas, list):
        x_data = []
        for data in datas:
            try:
                x_data.append(data.get(column)) if data.get(column) else None
            except:
                raise ValueError("can not fetch property： %s" % column)

        return source_object_outer(x_data, columns)
    elif isinstance(datas, dict):
        return source_object_outer(datas.get(column), columns)
    else:
        logger.info("data is not dict/list, no columns %s filter, skip.." % column)
        return datas


def _data_attr_(result):
    _data = result.get("resources")[0]
    _instances = _data.get("instances")[0]
    return _instances.get("attributes")


def _adder_property(result, key, define):
    x_tmp = []
    for t_data in result:
        if isinstance(t_data, dict):
            t_data[define.get("property")] = key
        elif isinstance(t_data, basestring):
            # 对于获取的数据是字符串类型时， 需要添加property字段， 
            # 则先将数据放入x_Origin_line， 由后续的字段提取进行特殊处理
            t_data = {define.get("property"): key, "x_Origin_line": t_data}
        else:
            logger.info("_adder_property %s is not string or dict, skip add property" % key)

        x_tmp.append(t_data)

    return x_tmp


def read_source_output(result, data_source_argument):
    try:
        result_columns = []
        _attributes = _data_attr_(result)

        if not data_source_argument:
            return source_object_outer(datas=_attributes, columns=[])

        if isinstance(data_source_argument, basestring):
            result_columns = source_object_outer(datas=_attributes, columns=data_source_argument.split("."))
        elif isinstance(data_source_argument, dict):
            # 多个字段提取定义 {"engree": {"property": "type", "attributes": "engress"}}
            for key, define in data_source_argument.items():
                if isinstance(define, basestring):
                    result_columns = source_object_outer(datas=_attributes, columns=define.split("."))
                elif isinstance(define, dict):
                    col_defines = source_object_outer(datas=_attributes,
                                                      columns=define.get("attributes", "").split("."))

                    if define.get("property"):
                        col_defines = _adder_property(result=col_defines, key=key, define=define)
                    result_columns += col_defines
                else:
                    raise ValueError("data source argument 配置异常应为 string或json：key-value "
                                     "或 key - {'property': 'xxx', 'attributes': ''}")

        return result_columns
    except:
        logger.info(traceback.format_exc())
        raise ValueError("query remote source failed, result read faild")


def read_outer_property(provider, result, defines, resource_values_config, resouce_name):
    logger.debug("data source output outer .... ")

    # 处理x_Origin_line
    x_Origin_line = result.pop("x_Origin_line", None) if isinstance(result, dict) else None
    if x_Origin_line:
        for key, define in defines.items():
            _t = SourceOuterReader.fetch_property(provider, key, result, define,
                                                  resource_values_config.get(key),
                                                  resouce_name)
            result.update(_t)

        return result

    res = {}
    for key, define in defines.items():
        if isinstance(define, dict) and define.get("define"):
            if result.get(key):
                value = TypeFormat.f_dict(result.get(key))
            else:
                value = read_outer_property(provider=provider, result=result,
                                            defines=define.get("define"),
                                            resource_values_config=resource_values_config,
                                            resouce_name=resouce_name)
            if value:
                res[key] = value

        else:
            _t = SourceOuterReader.fetch_property(provider, key, result, define,
                                                  resource_values_config.get(key),
                                                  resouce_name)
            if _t:
                res.update(_t)

    return res
