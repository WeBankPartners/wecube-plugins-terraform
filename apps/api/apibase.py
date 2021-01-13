# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import output_values
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
        if self.resource_keys_config:
            return

        self.resource_keys_config = ResourceObject().query_one(where_data={"provider": provider,
                                                                           "resource_name": self.resource_name})
        if not self.resource_keys_config:
            raise local_exceptions.ResourceConfigError("%s 资源未初始化完成配置" % self.resource_name)

    def values_config(self, provider):
        return ValueConfigObject().resource_value_configs(provider, self.resource_name)

    def _generate_data(self, provider, rid, data, extend_info):
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

        _name = self.resource_name + "_" + rid
        _info = {
            "resource": {
                resource_name: {
                    _name: resource_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def formate_result(self, result):
        return result

    def save_data(self, **kwargs):
        raise NotImplementedError()

    def update_data(self, rid, data):
        self.resource_object.update(rid, data)

    def _fetch_id(self, result):
        try:
            _data = result.get("resources")[0]
            _instances = _data.get("instances")[0]
            _attributes = _instances.get("attributes")
            return _attributes["id"]
        except:
            logger.info(traceback.format_exc())
            raise ValueError("result can not fetch id")

    def _read_other_result(self, result):
        models = self.resource_keys_config["output_property"]
        if models:
            _data = result.get("resources")[0]
            result = _data.get("instances")[0]
            logger.info(result)
            return output_values(models, result)
        return {}

    def create(self, **kwargs):
        raise NotImplementedError()

    def destory(self, rid):
        resource_info = self.resource_object.show(rid)
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        status = self.run_destory(_path)
        if status == 2021:
            self.write_define(rid, _path, define_json=resource_info["define_json"])
            status = self.run_destory(_path)
            if not status:
                raise local_exceptions.ResourceOperateException(self.resource_name,
                                                                msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)
