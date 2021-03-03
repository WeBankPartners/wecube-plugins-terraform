# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import define_relations_key
from apps.api.configer.provider import ProviderApi
from apps.api.apibase import ApiBase
# from apps.background.resource.network.subnet import SubnetObject
# from apps.background.resource.database.rds import RdsDBObject
from apps.background.resource.vm.instance_type import InstanceTypeObject
from apps.background.resource.resource_base import CrsObject
from apps.api.conductor.provider import ProviderConductor


class RdsDBApi(ApiBase):
    def __init__(self):
        super(RdsDBApi, self).__init__()
        self.resource_name = "rds"
        self.resource_workspace = "rds"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''
        subnet_id = create_data.get("subnet_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _subnet_status = define_relations_key("subnet_id", subnet_id, resource_property.get("subnet_id"))

        ext_info = {}
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = CrsObject("rds").object_resource_id(subnet_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"subnet_id": create_data.get("subnet_id")}

        password = create_data.get("password") or "Terraform.123"
        x_create_data = {"name": create_data.get("name"),
                         "engine": self.resource_name, "zone": zone,
                         "version": create_data.get("version"),
                         "instance_type": create_data.get("instance_type"),
                         "password": password,
                         "user": create_data.get("user"),
                         "port": create_data.get("port"),
                         "disk_type": create_data.get("disk_type"),
                         "disk_size": create_data.get("disk_size")}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        r_id = create_data.get("subnet_id")
        return None, r_id

    def create(self, rid, provider, region, zone, secret,
               create_data, extend_info, **kwargs):

        '''

        :param rid:
        :param provider:
        :param region:
        :param zone:
        :param secret:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        zone = ProviderConductor().zone_info(provider=provider_object["name"], zone=zone)
        x_create_data, r_create_data = self.generate_create_data(zone, create_data,
                                                                 provider=provider_object["name"])

        origin_type, instance_type_data = InstanceTypeObject().convert_resource_id(provider_object.get("id"),
                                                                                   create_data.get("instance_type"))

        cpu = instance_type_data.get("cpu")
        memory = instance_type_data.get("memory")
        kwargs["cpu"] = cpu
        kwargs["memory"] = memory
        x_create_data["instance_type"] = origin_type

        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

        x_create_data.update(_relations_id_dict)

        owner_id, relation_id = self.generate_owner_data(create_data)
        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=owner_id, relation_id=relation_id,
                                     create_data=x_create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res

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

    def destory(self, rid, force_delete=False):
        '''

        :param rid:
        :param force_delete:
        :return:
        '''

        resource_info = self.resource_object.show(rid)
        if not resource_info:
            return 0

        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        if not self.destory_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        if force_delete:
            update_data = {"force_delete": "true"}
            define_json = self._generate_update_data(rid, resource_info["provider"],
                                                     define_json=resource_info["define_json"],
                                                     update_data=update_data)

            self.write_define(rid, _path, define_json=define_json)

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid, update_data={"status": "deleted"})
