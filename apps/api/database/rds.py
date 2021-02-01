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
from apps.background.resource.network.subnet import SubnetObject
from apps.background.resource.database.rds import RdsDBObject
from apps.background.resource.vm.instance_type import InstanceTypeObject


class RdsDBApi(ApiBase):
    def __init__(self):
        super(RdsDBApi, self).__init__()
        self.resource_name = "rds"
        self.resource_workspace = "rds"
        self.resource_object = RdsDBObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, subnet_id, **kwargs):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _subnet_status = define_relations_key("subnet_id", subnet_id, resource_property.get("subnet_id"))

        ext_info = {}
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = SubnetObject().subnet_resource_id(subnet_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, name, subnet_id,
                  version, instance_type, port,
                  user, password, cpu, memory,
                  disk_type, disk_size,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):

        '''

        :param rid:
        :param name:
        :param subnet_id:
        :param version:
        :param instance_type:
        :param port:
        :param user:
        :param password:
        :param disk_type:
        :param disk_size:
        :param provider:
        :param provider_id:
        :param region:
        :param zone:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

        password = base64.b64encode(password) if password else password
        port = str(port) if port else port

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "version": version,
                                                 "instance_type": instance_type, "user": user,
                                                 "port": port, "password": password,
                                                 "disk_type": disk_type, "disk_size": disk_size,
                                                 "subnet_id": subnet_id, "status": status,
                                                 "provider_id": provider_id,
                                                 "cpu": cpu, "memory": memory,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id, version,
               instance_type, subnet_id, port, password,
               user, disk_type, disk_size,
               zone, region, extend_info, **kwargs):

        '''

        :param rid:
        :param name:
        :param provider_id:
        :param version:
        :param instance_type:
        :param subnet_id:
        :param port:
        :param password:
        :param user:
        :param disk_type:
        :param disk_size:
        :param zone:
        :param region:
        :param extend_info:
        :return:
        '''

        extend_info = extend_info or {}
        create_data = {"name": name, "engine": self.resource_name, "zone": zone,
                       "version": version, "instance_type": instance_type,
                       "password": password, "user": user, "port": port,
                       "disk_type": disk_type, "disk_size": disk_size}
        label_name = self.resource_name + "_" + rid

        origin_type, instance_type_data = InstanceTypeObject().type_resource_id(provider_id, instance_type)
        cpu = instance_type_data.get("cpu")
        memory = instance_type_data.get("memory")

        create_data["instance_type"] = origin_type
        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], subnet_id)

        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"],
                                              label_name=label_name,
                                              data=create_data, extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       subnet_id=subnet_id, version=version,
                       instance_type=instance_type,
                       port=port, password=password,
                       user=user, disk_type=disk_type,
                       disk_size=disk_size,
                       cpu=cpu, memory=memory,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)

        self.init_workspace(_path, provider_object["name"])

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data = {"status": "ok", "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        if not _update_data.get("resource_id"):
            _update_data["resource_id"] = self._fetch_id(result)

        self.update_data(rid, data=_update_data)

        return rid

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
