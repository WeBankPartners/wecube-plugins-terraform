# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import traceback
from core import local_exceptions
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.convert_keys import convert_extend_propertys
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import output_line
from apps.common.convert_keys import ConvertMetadata
from apps.common.reverse_convert_keys import ReverseProperty
from apps.background.resource.configr.resource import ResourceObject


class ResourceConfiger(object):
    def __init__(self):
        self.resource_keys_config = None

    def resource_info(self, provider, resource_name):
        '''

        :param provider:
        :param resource_name:
        :return:
        '''

        if self.resource_keys_config:
            return self.resource_keys_config

        resource_keys_config = ResourceObject().query_one(where_data={"provider": provider,
                                                                      "resource_type": resource_name})
        if not resource_keys_config:
            raise local_exceptions.ResourceConfigError("%s 资源未初始化完成配置" % resource_name)

        self.resource_keys_config = resource_keys_config
        return resource_keys_config

    def conductor_apply_property(self, provider, resource_name, resource_data):
        '''

        :param provider:
        :param resource_name:
        :param resource_data:
        :return:
        '''

        self.resource_info(provider, resource_name)

        resource_property = self.resource_keys_config["resource_property"]
        resource_columns = convert_keys(resource_data, defines=resource_property)

        resource_columns = self.reduce_key(resource_columns)
        return resource_columns, self.resource_keys_config

    def conductor_import_property(self, provider, resource_name):
        '''

        :param provider:
        :param resource_name:
        :param resource_data:
        :return:
        '''

        self.resource_info(provider, resource_name)

        return {}, self.resource_keys_config

    def pre_check_source_property(self, provider, resource_name, resource_data):
        '''

        :param provider:
        :param resource_name:
        :param resource_data:
        :return:
        '''

        self.resource_info(provider, resource_name)

        data_source = self.resource_keys_config["data_source"]
        if not data_source:
            raise ValueError("source资源未定义")

        for key, value in resource_data.items():
            if key == "zone":
                continue
            else:
                if key not in data_source.keys():
                    raise ValueError("provider: %s 不支持过滤参数： %s" % (provider, key))

    def conductor_source_property(self, provider, resource_name, resource_data):
        '''

        :param provider:
        :param resource_name:
        :param resource_data:
        :return:
        '''

        self.resource_info(provider, resource_name)

        data_source = self.resource_keys_config["data_source"]
        if not data_source:
            raise ValueError("source资源未定义")

        resource_columns = convert_keys(resource_data, defines=data_source)

        resource_columns = self.reduce_key(resource_columns)
        return resource_columns, self.resource_keys_config

    def conductor_reset_property(self, provider, resource_name):
        '''

        :param provider:
        :param resource_name:
        :param resource_data:
        :return:
        '''

        self.resource_info(provider, resource_name)

        origin_columns = {}
        # resource_property = self.resource_keys_config["resource_property"]
        # extend_info = self.resource_keys_config["extend_info"]
        # resource_output = self.resource_keys_config["resource_output"]
        # data_source_output = self.resource_keys_config["data_source_output"]

        resource_property = self.resource_keys_config["data_source_output"]

        extend_info = resource_property.pop("extend_info", {}) or {}

        propertys = ReverseProperty.reverse_keys(resource_property)
        extend = ReverseProperty.reverse_extend_keys(extend_info)

        # resource_output.pop("resource_id", None)
        # output = ReverseProperty.reverse_output_lines(resource_output)
        origin_columns.update(propertys)
        origin_columns.update(extend)
        # origin_columns.update(output)

        # columns = {}
        # for key, value in origin_columns.items():
        #     if value in data_source_output.keys():
        #         # todo dirct reverse ?
        #         continue
        #     columns[key] = value

        # data_source_output = ReverseProperty.reverse_keys(data_source_output)
        # columns.update(data_source_output)

        columns = origin_columns
        return columns, self.resource_keys_config


    def conductor_reset_equivalence(self, provider, resource_name):
        '''

        :param provider:
        :param resource_name:
        :param resource_data:
        :return:
        '''

        self.resource_info(provider, resource_name)

        origin_columns = {}
        resource_property = self.resource_keys_config["data_source_output"]

        extend_info = resource_property.pop("extend_info", {}) or {}

        propertys = ReverseProperty.reverse_equivalence(resource_property)
        extend = ReverseProperty.reverse_extend_key_equivalence(extend_info)

        origin_columns.update(propertys)
        origin_columns.update(extend)

        columns = origin_columns
        return columns, self.resource_keys_config

    def conductor_upgrade_property(self, provider, resource_name, resource_data):
        '''

        :param provider:
        :param resource_name:
        :param resource_data:
        :return:
        '''

        self.resource_info(provider, resource_name)

        resource_property = self.resource_keys_config["resource_property"]
        resource_columns = ConvertMetadata.upgrade_keys(resource_data, defines=resource_property)

        resource_columns = self.reduce_key(resource_columns)

        # origin_data.update(resource_columns)
        # return origin_data, self.resource_keys_config
        return resource_columns, self.resource_keys_config

    def conductor_apply_extend(self, provider, resource_name, extend_info):
        '''

        :param provider:
        :param resource_name:
        :param extend_info:
        :return:
        '''

        self.resource_info(provider, resource_name)

        resource_columns = {}
        resource_property = self.resource_keys_config["resource_property"]
        resource_extend_info = self.resource_keys_config["extend_info"]

        resource_property_extend = resource_property.pop("extend_info", {}) or {}

        _extend_columns = convert_keys(datas=extend_info, defines=resource_property, is_extend=True)
        logger.info("property extend info: %s" % (format_json_dumps(_extend_columns)))
        resource_columns.update(_extend_columns)

        _extend_columns = convert_keys(datas=extend_info, defines=resource_property_extend, is_extend=True)
        logger.info("resource_property extend info: %s" % (format_json_dumps(_extend_columns)))
        resource_columns.update(_extend_columns)

        _extend_columns = convert_extend_propertys(datas=extend_info, extend_info=resource_extend_info)
        logger.info("extend info: %s" % (format_json_dumps(_extend_columns)))
        resource_columns.update(_extend_columns)

        resource_columns = self.reduce_key(resource_columns)
        return resource_columns, self.resource_keys_config

    def reduce_key(self, data):
        result = {}
        for key, value in data.items():
            if value:
                result[key] = value
            elif isinstance(value, (int, bool)):
                result[key] = value
            else:
                logger.info("key %s value: %s is null, remove it" % (key, str(value)))

        return result

    def _generate_output(self, provider, resource_name, label_name):
        '''
        转换output 输出参数，生成配置
        :param label_name:
        :return:
        '''

        self.resource_info(provider, resource_name)

        output_configs = self.resource_keys_config["resource_output"]
        resource_name = self.resource_keys_config["resource_name"]

        _ext_output = {}
        for key, define in output_configs.items():
            _ext_output.update(output_line(key, define))

        ext_output_config = {}
        for column, ora_column in _ext_output.items():
            ext_output_config[column] = {"value": "${%s.%s.%s}" % (resource_name, label_name, ora_column)}

        result = {"output": ext_output_config} if ext_output_config else {}
        return result, self.resource_keys_config

    def _generate_source_output(self, provider, resource_name, label_name):
        '''
        转换output 输出参数，生成配置
        :param label_name:
        :return:
        '''

        self.resource_info(provider, resource_name)

        output_configs = self.resource_keys_config["resource_output"]
        resource_name = self.resource_keys_config["resource_type"]

        _ext_output = {}
        for key, define in output_configs.items():
            _ext_output.update(output_line(key, define))

        ext_output_config = {}
        for column, ora_column in _ext_output.items():
            if column != "resource_id":
                ext_output_config[column] = {"value": "${data.%s.%s.%s}" % (resource_name, label_name, ora_column)}

        result = {"output": ext_output_config} if ext_output_config else {}
        return result, self.resource_keys_config

    def conductor_apply_output(self, provider, resource_name, label_name):
        '''

        :param provider:
        :param resource_name:
        :param label_name:
        :return:
        '''

        return self._generate_output(provider, resource_name, label_name)

    def conductor_data_output(self, provider, resource_name, label_name):
        '''

        :param provider:
        :param resource_name:
        :param label_name:
        :return:
        '''

        return self._generate_source_output(provider, resource_name, label_name)

    def conductor_upgrade_extend(self, provider, resource_name, extend_info):
        '''

        :param provider:
        :param resource_name:
        :param extend_info:
        :return:
        '''

        self.resource_info(provider, resource_name)

        resource_columns = {}
        resource_property = self.resource_keys_config["resource_property"]
        resource_extend_info = self.resource_keys_config["extend_info"]

        _extend_columns = ConvertMetadata.upgrade_extend_keys(datas=extend_info, defines=resource_property)
        logger.info("property extend info: %s" % (format_json_dumps(_extend_columns)))
        resource_columns.update(_extend_columns)

        _extend_columns = ConvertMetadata.upgrade_extend_info(datas=extend_info, extend_info=resource_extend_info)
        logger.info("extend info: %s" % (format_json_dumps(_extend_columns)))
        resource_columns.update(_extend_columns)

        resource_columns = self.reduce_key(resource_columns)

        # origin_data.update(resource_columns)
        #
        # result = self.reduce_key(origin_data)
        # return result, self.resource_keys_config
        return resource_columns, self.resource_keys_config


# if __name__ == '__main__':
#     x = ResourceConfiger().conductor_reset_property('tencentcloud', 'vpc')
#     print(x)
