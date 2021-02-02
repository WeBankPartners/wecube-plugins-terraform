# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import base64
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import validate_type
from apps.common.convert_keys import convert_extend_propertys
from apps.common.convert_keys import define_relations_key
from apps.api.configer.provider import ProviderApi
from apps.api.apibase import ApiBase
from apps.background.resource.network.vpc import VpcObject
from apps.background.resource.network.subnet import SubnetObject
from apps.background.resource.network.security_group import SecGroupObject
from apps.background.resource.vm.instance_type import InstanceTypeObject
from apps.background.resource.vm.instance import InstanceObject


class InstanceApi(ApiBase):
    def __init__(self):
        super(InstanceApi, self).__init__()
        self.resource_name = "instance"
        self.resource_workspace = "instance"
        self.resource_object = InstanceObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, vpc_id, subnet_id, sg_id):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _subnet_status = define_relations_key("subnet", subnet_id, resource_property.get("subnet_id"))
        _sg_status = define_relations_key("security_group_id", sg_id, resource_property.get("security_group_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = VpcObject().vpc_resource_id(vpc_id)
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = SubnetObject().subnet_resource_id(subnet_id)
        if sg_id and (not _sg_status):
            sg_property = resource_property.get("security_group_id")
            if isinstance(sg_property, dict):
                if sg_property.get("type", "string") == "list":
                    sg_list = validate_type(sg_id, "list")
                    _sg_resource_ids = []
                    for _sg in sg_list:
                        _sg_resource_ids.append(SecGroupObject().resource_id(_sg))
                else:
                    _sg_resource_ids = SecGroupObject().resource_id(sg_id)

                ext_info["security_group_id"] = _sg_resource_ids
            else:
                ext_info["security_group_id"] = SecGroupObject().resource_id(sg_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def _generate_update_data(self, rid, provider, define_json, update_data, extend_info):
        self.resource_info(provider)
        resource_values_config = self.values_config(provider)

        resource_name = self.resource_keys_config["property"]
        resource_property = self.resource_keys_config["resource_property"]
        resource_extend_info = self.resource_keys_config["extend_info"]

        resource_columns = {}
        for key, value in update_data.items():
            if resource_values_config.get(key):
                _values_configs = resource_values_config.get(key)
                value = convert_value(value, _values_configs.get(value))

            resource_columns[key] = value

        resource_columns = convert_keys(resource_columns, defines=resource_property, is_update=True)
        if extend_info:
            _extend_columns = convert_extend_propertys(datas=extend_info,
                                                       extend_info=resource_extend_info,
                                                       is_update=True)
            resource_columns.update(_extend_columns)

        _t = define_json["resource"][resource_name]
        label_name = self.resource_name + "_" + rid
        origin_columns = _t[label_name]

        origin_columns.update(resource_columns)

        define_json["resource"] = {
            resource_name: {
                label_name: origin_columns
            }
        }
        logger.info(format_json_dumps(define_json))
        return define_json

    def save_data(self, rid, name, hostname,
                  instance_type, disk_type,
                  disk_size, image, cpu, memory,
                  provider, provider_id, region,
                  subnet_id, zone, password,
                  extend_info, define_json,
                  status, result_json):

        '''

        :param rid:
        :param name:
        :param hostname:
        :param instance_type:
        :param disk_type:
        :param disk_size:
        :param image:
        :param cpu:
        :param memory:
        :param provider:
        :param provider_id:
        :param region:
        :param subnet_id:
        :param zone:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

        password = base64.b64encode(password)
        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "hostname": hostname,
                                                 "instance_type": instance_type,
                                                 "disk_type": disk_type,
                                                 "disk_size": disk_size,
                                                 "subnet_id": subnet_id,
                                                 "password": password,
                                                 "power_state": "start",
                                                 "image": image, "cpu": cpu,
                                                 "memory": memory, "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id, hostname,
               instance_type, image, disk_type,
               subnet_id, disk_size, password,
               security_group_id, vpc_id, data_disks,
               zone, region, extend_info):

        '''

        :param rid:
        :param name:
        :param provider_id:
        :param hostname:
        :param instance_type:
        :param image:
        :param disk_type:
        :param subnet_id:
        :param disk_size:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        # todo 校验 data disks ， 定义type模型

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return _exists_data

        extend_info = extend_info or {}
        create_data = {"name": name, "hostname": hostname,
                       "disk_type": disk_type,
                       "disk_size": disk_size,
                       "data_disks": data_disks,
                       "zone": zone, "image": image}

        password = password or "Terraform.123"
        label_name = self.resource_name + "_" + rid
        origin_type, instance_type_data = InstanceTypeObject().type_resource_id(provider_id, instance_type)
        cpu = instance_type_data.get("cpu")
        memory = instance_type_data.get("memory")

        create_data["password"] = password
        create_data["instance_type"] = origin_type
        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], vpc_id, subnet_id, security_group_id)

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
                       hostname=hostname, instance_type=instance_type,
                       disk_type=disk_type, disk_size=disk_size,
                       image=image, cpu=cpu, memory=memory,
                       subnet_id=subnet_id,
                       password=password,
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
        resource_id = self._fetch_id(result)

        _update_data = {"status": "ok",
                        "resource_id": resource_id,
                        "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        return self.update_data(rid, data=_update_data)

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
                                                     update_data=update_data, extend_info={})

            self.write_define(rid, _path, define_json=define_json)

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid, update_data={"status": "deleted",
                                                             "power_state": "stop"})

    def update(self, rid, name, instance_type, image, security_group_id, extend_info):
        '''

        :param rid:
        :param name:
        :param instance_type:
        :param image:
        :param security_group_id:
        :param extend_info:
        :return:
        '''

        _update_data = {}
        _obj = self.resource_object.show(rid)
        if not _obj:
            raise local_exceptions.ResourceNotFoundError("instance %s 不存在" % rid)

        update_data = {}
        if name:
            update_data["name"] = name
        if instance_type:
            origin_type, instance_type_data = InstanceTypeObject().type_resource_id(_obj["provider_id"], instance_type)
            cpu = instance_type_data.get("cpu")
            memory = instance_type_data.get("memory")
            _update_data = {"cpu": cpu, "memory": memory}
            update_data["instance_type"] = instance_type
        if image:
            update_data["image"] = image
        if security_group_id:
            _relations_id_dict = self.before_keys_checks(_obj["provider"],
                                                         vpc_id=None,
                                                         subnet_id=None,
                                                         sg_id=security_group_id)

            update_data.update(_relations_id_dict)

        define_json = self._generate_update_data(rid, _obj["provider"],
                                                 define_json=_obj["define_json"],
                                                 update_data=update_data,
                                                 extend_info=extend_info)

        _path = self.create_workpath(rid,
                                     provider=_obj["provider"],
                                     region=_obj["region"])

        update_data["status"] = "updating"
        self.update_data(rid, data=update_data)
        self.write_define(rid, _path, define_json=define_json)

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data.update({"status": "ok",
                             "result_json": format_json_dumps(result)})

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
                                                 update_data=update_data,
                                                 extend_info={})

        self.update_data(rid, data={"status": "starting"})
        self.write_define(rid, _path, define_json=define_json)

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

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
                                                 update_data=update_data,
                                                 extend_info={})

        self.update_data(rid, data={"status": "stopping"})
        self.write_define(rid, _path, define_json=define_json)

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        return self.update_data(rid, data={"status": "ok", "power_state": "stop",
                                           "define_json": json.dumps(define_json)})
