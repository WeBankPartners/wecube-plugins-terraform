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
from apps.background.resource.network.subnet import SubnetObject
from apps.background.resource.vm.instance_type import InstanceTypeObject
from apps.background.resource.vm.instance import InstanceObject


class InstanceApi(TerraformResource):
    def __init__(self):
        super(InstanceApi, self).__init__()
        self.resource_name = "instance"
        self.resource_workspace = "instance"
        self.resource_object = InstanceObject()
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

        resource_name = self.resource_keys_config["resource_name"]
        resource_property = self.resource_keys_config["resource_property"]
        resource_extend_info = self.resource_keys_config["extend_info"]

        resource_columns = {}
        for key, value in data.items():
            if resource_values_config.get(key):
                value = convert_value(value, resource_values_config.get(key))

            resource_columns[key] = value

        resource_columns = convert_keys(resource_columns, defines=resource_property)

        _extend_columns = convert_extend_propertys(datas=extend_info, extend_info=resource_extend_info)
        resource_columns.update(_extend_columns)

        _info = {
            "resource": {
                resource_name: {
                    rid: resource_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def _generate_update_data(self, rid, provider, define_json, update_data):
        resource_keys_config = self.resource_info(provider)
        resource_values_config = self.values_config(provider)

        resource_name = resource_keys_config["resource_name"]
        resource_property = resource_keys_config["resource_property"]

        resource_columns = {}
        for key, value in update_data.items():
            if resource_values_config.get(key):
                value = convert_value(value, resource_values_config.get(key))

            resource_columns[key] = value

        resource_columns = convert_keys(resource_columns,
                                        defines=resource_property,
                                        is_update=True)

        _t = define_json["resource"][resource_name]
        origin_columns = _t[rid]

        origin_columns.update(resource_columns)

        _info = {
            "resource": {
                resource_name: {
                    rid: origin_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def formate_result(self, result):
        return result

    def save_data(self, rid, name, hostname,
                  instance_type, disk_type,
                  disk_size, image, cpu, memory,
                  provider, provider_id, region,
                  subnet_id, zone,
                  extend_info, define_json,
                  status, result_json):

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "hostname": hostname,
                                                 "instance_type": instance_type,
                                                 "disk_type": disk_type,
                                                 "disk_size": disk_size,
                                                 "subnet_id": subnet_id,
                                                 "power_state": "start",
                                                 "image": image, "cpu": cpu,
                                                 "memory": memory, "status": status,
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

    def _read_other_result(self, result):
        models = self.resource_keys_config["output_property"]
        if models:
            _data = result.get("resources")[0]
            result = _data.get("instances")[0]
            logger.info(result)
            return output_values(models, result)
        return {}

    def create(self, rid, name, provider_id, hostname,
               instance_type, image, disk_type,
               subnet_id, disk_size,
               zone, region, extend_info, **kwargs):
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

        origin_type, instance_type_data = InstanceTypeObject().type_resource_id(provider_id, instance_type)
        cpu = instance_type_data.get("cpu")
        memory = instance_type_data.get("memory")

        origin_subnet_id = SubnetObject().subnet_resource_id(subnet_id)

        # todo  安全组转换
        if extend_info.get("security_group_id"):
            pass

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        create_data = {"name": name, "hostname": hostname,
                       "instance_type": origin_type,
                       "disk_type": disk_type,
                       "disk_size": disk_size,
                       "subnet_id": origin_subnet_id,
                       "zone": zone, "image": image}

        define_json = self._generate_data(provider_object["name"], rid,
                                          data=create_data, extend_info=extend_info)
        define_json.update(provider_info)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       hostname=hostname, instance_type=instance_type,
                       disk_type=disk_type, disk_size=disk_size,
                       image=image, cpu=cpu, memory=memory,
                       subnet_id=subnet_id,
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

    def destory(self, rid, force_delete=False):
        '''

        :param rid:
        :param force_delete:
        :return:
        '''

        resource_info = self.resource_object.show(rid)
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])
        if force_delete:
            update_data = {"force_delete": "true"}
            define_json = self._generate_update_data(rid, resource_info["provider"],
                                                     define_json=resource_info["define_json"],
                                                     update_data=update_data)

            self.write_define(rid, _path, define_json=define_json)

        status = TerraformDriver().destroy(dir_path=_path)
        if not status:
            self.write_define(rid, _path, define_json=resource_info["define_json"])
            TerraformDriver().destroy(dir_path=_path)

        return self.resource_object.delete(rid, update_data={"status": "deleted",
                                                             "power_state": "stop"})

    def update(self, rid, name, instance_type, image, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        # todo 更新安全组

        _obj = self.resource_object.show(rid)
        if not _obj:
            raise local_exceptions.ResourceNotFoundError("instance %s 不存在" % rid)

        update_data = {}
        if name:
            update_data["name"] = name
        if instance_type:
            update_data["instance_type"] = instance_type
        if image:
            update_data["image"] = image

        update_data.update(extend_info)
        _path = self.create_workpath(rid,
                                     provider=_obj["provider"],
                                     region=_obj["region"])

        define_json = self._generate_update_data(rid, _obj["provider"],
                                                 define_json=_obj["define_json"],
                                                 update_data=update_data)

        update_data["status"] = "updating"
        self.update_data(rid, data=update_data)
        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data = {"status": "ok",
                        "result_json": format_json_dumps(result)}
        _update_data.update(self._read_other_result(result, {}))
        return self.update_data(rid, data=_update_data)

    def start(self, rid):
        '''
        power_action " start
        :param rid:
        :return:
        '''

        _obj = self.resource_object.show(rid)
        if not _obj:
            raise local_exceptions.ResourceNotFoundError("instance %s 不存在" % rid)

        update_data = {"power_action": "start"}

        _path = self.create_workpath(rid,
                                     provider=_obj["provider"],
                                     region=_obj["region"])

        define_json = self._generate_update_data(rid, _obj["provider"],
                                                 define_json=_obj["define_json"],
                                                 update_data=update_data)

        self.update_data(rid, data={"status": "starting"})
        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        return self.update_data(rid, data={"status": "ok", "power_state": "start",
                                           "define_json": json.dumps(define_json)})

    def stop(self, rid):
        '''
        power_action: stop
        :param rid:
        :return:
        '''

        _obj = self.resource_object.show(rid)
        if not _obj:
            raise local_exceptions.ResourceNotFoundError("instance %s 不存在" % rid)

        update_data = {"power_action": "stop"}

        _path = self.create_workpath(rid,
                                     provider=_obj["provider"],
                                     region=_obj["region"])

        define_json = self._generate_update_data(rid, _obj["provider"],
                                                 define_json=_obj["define_json"],
                                                 update_data=update_data)

        self.update_data(rid, data={"status": "stopping"})
        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        return self.update_data(rid, data={"status": "ok", "power_state": "stop",
                                           "define_json": json.dumps(define_json)})
