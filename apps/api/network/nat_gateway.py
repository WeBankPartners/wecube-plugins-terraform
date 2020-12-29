# coding: utf-8

import os
import json
import traceback
from core import local_exceptions
from lib.json_helper import format_json_dumps
from lib.logs import logger
from lib.uuid_util import get_uuid
from wecube_plugins_terraform.settings import TERRAFORM_BASE_PATH
from apps.common.generate import generate_data
from apps.api.configer.provider import ProviderApi
from apps.api.configer.resource import ResourceObject
from apps.api.configer.value_config import ValueConfigObject
from apps.background.lib.commander.terraform import TerraformDriver
from apps.background.resource.network.nat_gateway import NatGatewayObject


class NatGatewayApi(object):
    terraformDriver = TerraformDriver()

    def create_workpath(self, rid, provider, region, zone):
        zone = zone or ""
        _az = "%s_%s" % (region, zone) if zone else region
        _path = os.path.join(TERRAFORM_BASE_PATH, provider, _az, "vpc", rid)
        if not os.path.exists(_path):
            os.makedirs(_path)

        self.terraformDriver.init_resource_dir(dir_path=_path, provider=provider)
        return _path

    def write_define(self, rid, path, define_json):
        with open(os.path.join(path, "%s.tf.json" % rid), 'wb+') as f:
            json.dump(define_json, f, ensure_ascii=False, indent=4)

    def run(self, path):
        self.terraformDriver.apply(path, auto_approve="")
        return self.terraformDriver.resource_result(path)

    def resource_info(self, provider):
        _vpc_resource = ResourceObject().query_one(where_data={"provider": provider,
                                                               "property": "vpc"})
        if not _vpc_resource:
            raise local_exceptions.ResourceConfigError("vpc 资源未初始化完成配置")

        return _vpc_resource

    def resource_config(self, provider):
        return ValueConfigObject().query_one(where_data={"provider": provider,
                                                         "resource": "vpc"})

    def revert(self, data, resource_property, data_modes):
        result = {}
        for k, v in data.items():
            key = resource_property.get(k, k)
            result[key] = generate_data(v, model=data_modes.get(v, {}))

        return result

    def _generate_vpc(self, provider, name, data):
        _vpc_resource = self.resource_info(provider)
        _vpc_config = self.resource_config(provider)

        resource_name = _vpc_resource["resource_name"]
        resource_property = _vpc_resource["resource_property"]

        _columns = self.revert(data, resource_property=json.loads(resource_property),
                               data_modes=json.loads(_vpc_config.get("value_config", "{}")))
        _info = {
            "resource": {
                resource_name: {
                    name: _columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def formate_result(self, result):
        # todo 获取vpc创建信息
        return result

    def save_data(self, rid, name, provider, region, zone,
                  cider, extend_info, define_json,
                  status, result_json):
        NatGatewayObject().create(create_data={"id": rid, "provider": provider,
                                        "region": region, "zone": zone,
                                        "name": name, "cider": cider,
                                        "status": status,
                                        "extend_info": json.dumps(extend_info),
                                        "define_json": json.dumps(define_json),
                                        "result_json": result_json})

    def update_data(self, rid, data):
        NatGatewayObject().update(rid, data)

    def _fetch_id(self, result):
        try:
            _data = result.get("resources")[0]
            _instances = _data.get("instances")[0]
            _attributes = _instances.get("attributes")
            return _attributes["id"]
        except:
            logger.info(traceback.format_exc())
            raise ValueError("result can not fetch id")

    def create(self, data):
        name = data["name"]
        cider = data["cider"]
        provider = data["provider"]
        region = data["region"]
        zone = data.get("zone")
        extend_info = data.get("extend_info", {})
        rid = data.get("id") or get_uuid()

        create_data = {"cider": cider, "name": name}
        create_data.update(extend_info)

        _path = self.create_workpath(rid, provider, region, zone)

        provider_info = ProviderApi().provider_info(provider, region=data.get("region"))
        vpc_info = self._generate_vpc(provider, name, data=create_data)
        vpc_info.update(provider_info)

        self.save_data(rid, name=name, provider=provider, region=region,
                       zone=zone, cider=cider, extend_info=extend_info,
                       define_json=vpc_info, status="applying", result_json='{}')

        self.write_define(rid, _path, define_json=vpc_info)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))
        resource_id = self._fetch_id(result)
        self.update_data(rid, data={"status": "ok",
                                    "resource_id": resource_id,
                                    "result_json": format_json_dumps(result)})

        return rid

