# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.api.configer.provider import ProviderApi
from apps.api.configer.resource import ResourceObject
from apps.api.configer.value_config import ValueConfigObject
from apps.background.lib.commander.terraform import TerraformDriver
from apps.background.lib.drivers.terraform_operate import TerraformResource
from apps.background.resource.network.eip import EipObject


class EipApi(TerraformResource):
    def __init__(self):
        super(EipApi, self).__init__()
        self.resource_name = "eip"
        self.resource_workspace = "eip"
        self.resource_object = EipObject()

    def resource_info(self, provider):
        resource_config = ResourceObject().query_one(where_data={"provider": provider,
                                                                 "property": self.resource_name})
        if not resource_config:
            raise local_exceptions.ResourceConfigError("%s 资源未初始化完成配置" % self.resource_name)

        return resource_config

    def values_config(self, provider):
        return ValueConfigObject().resource_value_configs(provider, self.resource_name)

    def _generate_data(self, provider, name, data):
        resource_keys_config = self.resource_info(provider)
        resource_values_config = self.values_config(provider)

        resource_name = resource_keys_config["resource_name"]
        resource_property = resource_keys_config["resource_property"]

        resource_columns = {}
        for key, value in data.items():
            if resource_values_config.get(key):
                value = convert_value(value, resource_values_config.get(key))

            resource_columns[key] = value

        resource_columns = convert_keys(resource_columns, defines=resource_property)

        _info = {
            "resource": {
                resource_name: {
                    name: resource_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def formate_result(self, result):
        return result

    def save_data(self, rid, name,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name,
                                                 "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def update_data(self, rid, data):
        return self.resource_object.update(rid, data)

    def _fetch_id(self, result):
        try:
            _data = result.get("resources")[0]
            _instances = _data.get("instances")[0]
            _attributes = _instances.get("attributes")
            return _attributes["id"]
        except:
            logger.info(traceback.format_exc())
            raise ValueError("result can not fetch id")

    def _read_other_result(self, result, models):
        return {}

    def create(self, rid, name, provider_id,
               zone, region, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param cider:
        :param provider_id:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        create_data = {"name": name}

        create_data.update(extend_info)
        create_data.update(kwargs)

        define_json = self._generate_data(provider_object["name"], name, data=create_data)
        define_json.update(provider_info)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))
        resource_id = self._fetch_id(result)

        #  ---------------
        # todo 提取ipaddress

        _update_data = {"status": "ok",
                        "resource_id": resource_id,
                        "result_json": format_json_dumps(result)}
        _update_data.update(self._read_other_result(result, {}))
        self.update_data(rid, data=_update_data)

        return rid

    def destory(self, rid):
        resource_info = self.resource_object.show(rid)
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        status = TerraformDriver().destroy(dir_path=_path)
        if not status:
            self.write_define(rid, _path, define_json=resource_info["define_json"])
            TerraformDriver().destroy(dir_path=_path)

        return self.resource_object.delete(rid)
