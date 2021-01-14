# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import output_values
from apps.common.convert_keys import convert_extend_propertys
from apps.api.configer.provider import ProviderApi
from apps.api.configer.resource import ResourceObject
from apps.api.configer.value_config import ValueConfigObject
from apps.background.lib.commander.terraform import TerraformDriver
from apps.background.lib.drivers.terraform_operate import TerraformResource
from apps.background.resource.network.vpc import VpcObject
from apps.background.resource.network.subnet import SubnetObject


class SubnetApi(TerraformResource):
    def __init__(self):
        super(SubnetApi, self).__init__()
        self.resource_name = "subnet"
        self.resource_workspace = "subnet"
        self.resource_object = SubnetObject()
        self.resource_keys_config = None

    def resource_info(self, provider):
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

    def save_data(self, rid, name,
                  provider, provider_id, region, zone,
                  cidr, extend_info, define_json, vpc,
                  status, result_json):

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "cidr": cidr,
                                                 "vpc": vpc, "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

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

    def create(self, rid, name, cidr, provider_id,
               vpc_id, region, zone, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param cidr:
        :param provider_id:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        extend_info = extend_info or {}
        vpc_resource_id = VpcObject().vpc_resource_id(vpc_id, where_data={"region": region})

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)

        create_data = {"cidr": cidr, "name": name,
                       "vpc_id": vpc_resource_id,
                       "zone": zone}

        define_json = self._generate_data(provider_object["name"], rid,
                                          data=create_data, extend_info=extend_info)
        define_json.update(provider_info)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       cidr=cidr, vpc=vpc_id,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        resource_id = self._fetch_id(result)
        _update_data = {"status": "ok",
                        "resource_id": resource_id,
                        "result_json": format_json_dumps(result)}
        _update_data.update(self._read_other_result(result))
        self.update_data(rid, data=_update_data)

        return rid

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
