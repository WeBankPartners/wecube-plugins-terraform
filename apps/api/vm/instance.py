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
from apps.api.apibase import ApiBase
from apps.background.resource.vm.instance_type import InstanceTypeObject
from apps.background.resource.resource_base import CrsObject
from apps.api.conductor.provider import ProviderConductor


class InstanceApi(ApiBase):
    def __init__(self):
        super(InstanceApi, self).__init__()
        self.resource_name = "instance"
        self.resource_workspace = "instance"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")
        subnet_id = create_data.get("subnet_id")
        sg_id = create_data.get("security_group_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _subnet_status = define_relations_key("subnet", subnet_id, resource_property.get("subnet_id"))
        _sg_status = define_relations_key("security_group_id", sg_id, resource_property.get("security_group_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject("vpc").object_resource_id(vpc_id)
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = CrsObject("subnet").object_resource_id(subnet_id)
        if sg_id and (not _sg_status):
            sg_property = resource_property.get("security_group_id")
            if isinstance(sg_property, dict):
                if sg_property.get("type", "string") == "list":
                    sg_list = validate_type(sg_id, "list")
                    _sg_resource_ids = []
                    for _sg in sg_list:
                        _sg_resource_ids.append(CrsObject("security_group").object_resource_id(_sg))
                else:
                    _sg_resource_ids = CrsObject("security_group").object_resource_id(sg_id)

                ext_info["security_group_id"] = _sg_resource_ids
            else:
                ext_info["security_group_id"] = CrsObject("security_group").object_resource_id(sg_id)

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

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("vpc_id"),
                         "subnet_id": create_data.get("subnet_id"),
                         "security_group_id": create_data.get("security_group_id")}

        x_create_data = {"name": create_data.get("name"),
                         "hostname": create_data.get("hostname"),
                         "disk_type": create_data.get("disk_type"),
                         "disk_size": create_data.get("disk_size"),
                         "data_disks": create_data.get("data_disks"),
                         "zone": zone, "image": create_data.get("image")}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        r_id = {"subnet_id": create_data.get("subnet_id")}
        return None, r_id

    def create(self, rid, provider, region, zone, secret,
               create_data, extend_info, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
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

        password = create_data.get("password") or "Terraform.123"
        origin_type, instance_type_data = InstanceTypeObject().convert_resource_id(provider_object.get("id"),
                                                                                   create_data.get("instance_type"))

        cpu = instance_type_data.get("cpu")
        memory = instance_type_data.get("memory")
        kwargs["cpu"] = cpu
        kwargs["memory"] = memory

        x_create_data["password"] = password
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
        
        return self.resource_object.delete(rid, update_data=None)

        # return self.resource_object.delete(rid, update_data={"status": "deleted",
        #                                                      "power_state": "stop"})

                                                             

        
        

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
