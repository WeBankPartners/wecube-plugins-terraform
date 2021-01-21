# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import read_output
from apps.common.convert_keys import output_values
from apps.common.convert_keys import output_line
from apps.common.convert_keys import define_relations_key
from apps.common.convert_keys import convert_extend_propertys
from apps.api.configer.resource import ResourceObject
from apps.api.configer.value_config import ValueConfigObject
from apps.background.lib.drivers.terraform_operate import TerraformResource


class ApiBase(TerraformResource):
    def __init__(self):
        super(ApiBase, self).__init__()
        self.resource_name = ""
        self.resource_workspace = ""
        self.resource_object = None
        self.resource_keys_config = None

    def resource_info(self, provider):
        '''

        :param provider:
        :return:
        '''

        if self.resource_keys_config:
            return

        self.resource_keys_config = ResourceObject().query_one(where_data={"provider": provider,
                                                                           "resource_name": self.resource_name})
        if not self.resource_keys_config:
            raise local_exceptions.ResourceConfigError("%s 资源未初始化完成配置" % self.resource_name)

    def values_config(self, provider):
        '''

        :param provider:
        :return:
        '''

        return ValueConfigObject().resource_value_configs(provider, self.resource_name)

    def before_keys_checks(self, **kwargs):
        '''
        校验依赖的id的合法性
        :param kwargs:
        :return:
        '''

        # self.resource_info(provider)
        return {}

    def _generate_output(self, label_name):
        '''
        转换output 输出参数，生成配置
        :param label_name:
        :return:
        '''

        output_configs = self.resource_keys_config["output_property"]
        resource_name = self.resource_keys_config["property"]

        _ext_output = {}
        for key, define in output_configs.items():
            _ext_output.update(output_line(key, define))

        ext_output_config = {}
        for column, ora_column in _ext_output.items():
            ext_output_config[column] = {"value": "${%s.%s.%s}" % (resource_name, label_name, ora_column)}

        return {"output": ext_output_config} if ext_output_config else {}

    def _generate_resource(self, provider, label_name, data, extend_info):
        '''
        转换resource 资源属性， 生成配置
        :param provider:
        :param label_name: 资源的标签名称
        :param data:
        :param extend_info:
        :return:
        '''

        self.resource_info(provider)
        resource_values_config = self.values_config(provider)

        resource_name = self.resource_keys_config["property"]
        resource_property = self.resource_keys_config["resource_property"]
        resource_extend_info = self.resource_keys_config["extend_info"]

        resource_columns = {}
        for key, value in data.items():
            if resource_values_config.get(key):
                _values_configs = resource_values_config.get(key)
                value = convert_value(value, _values_configs.get(value))

            resource_columns[key] = value

        resource_columns = convert_keys(resource_columns, defines=resource_property)
        _extend_columns = convert_extend_propertys(datas=extend_info, extend_info=resource_extend_info)
        resource_columns.update(_extend_columns)

        _info = {
            "resource": {
                resource_name: {
                    label_name: resource_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def formate_result(self, result):
        '''
        对 result 做处理
        :param result:
        :return:
        '''

        return result

    def save_data(self, **kwargs):
        '''
        save data to db
        :param kwargs:
        :return:
        '''
        raise NotImplementedError()

    def update_data(self, rid, data):
        '''

        :param rid:
        :param data:
        :return:
        '''

        return self.resource_object.update(rid, data)

    def _fetch_id(self, result):
        '''

        :param result:
        :return:
        '''

        try:
            _data = result.get("resources")[0]
            _instances = _data.get("instances")[0]
            _attributes = _instances.get("attributes")
            return _attributes.get("id") or "0000000"
        except:
            logger.info(traceback.format_exc())
            raise ValueError("result can not fetch id")

    def _read_output_result(self, result):
        '''
        对于设置了output的属性， 则提取output输出值
        :param result:
        :return:
        '''

        models = self.resource_keys_config["output_property"]
        if models:
            result_output = result.get("outputs")

            ext_result = {}
            for column, res in result_output.items():
                _out_dict = read_output(key=column, define=models.get(column),
                                        result=res.get("value"))
                ext_result.update(_out_dict)

            logger.info(format_json_dumps(ext_result))
            return ext_result

        return {}

    def create(self, **kwargs):
        '''
        main    create resource and save info into db
        :param kwargs:
        :return:
        '''
        raise NotImplementedError()

    def destory(self, rid):
        '''

        :param rid:
        :return:
        '''

        resource_info = self.resource_object.show(rid)
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        if not self.destory_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)
