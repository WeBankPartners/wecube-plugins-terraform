# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.uuid_util import get_uuid
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import convert_key_only
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
# from apps.background.resource.vm.instance import InstanceObject
# from apps.background.resource.loadbalance.lb import LBObject
# from apps.background.resource.loadbalance.listener import LBListenerObject
# from apps.background.resource.loadbalance.lb_attach import LBAttachObject
# from apps.background.resource.loadbalance.lb_attach import LBAttachInstanceObject
from apps.background.resource.resource_base import CrsObject


class LBAttachApi(ApiBase):
    def __init__(self):
        super(LBAttachApi, self).__init__()
        self.resource_name = "lb_attach"
        self.resource_workspace = "lb_attach"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param lb_id:
        :param listener_id:
        :return:
        '''
        lb_id = create_data.get("lb_id")
        listener_id = create_data.get("listener_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _ll_status = define_relations_key("listener_id", listener_id, resource_property.get("listener_id"))
        _lb_status = define_relations_key("lb_id", lb_id, resource_property.get("lb_id"))

        ext_info = {}
        if listener_id and (not _ll_status):
            ext_info["listener_id"] = CrsObject("lb_listener").object_resource_id(listener_id)
        if lb_id and (not _lb_status):
            ext_info["lb_id"] = CrsObject("lb").object_resource_id(lb_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def validate_instance(self, provider, instances):
        result = []
        self.resource_info(provider)
        resource_values_config = self.values_config(provider)
        resource_property = self.resource_keys_config["resource_property"]

        for instance_dict in instances:
            if not instance_dict.get("instance_id"):
                raise ValueError("instance not permit null")
            else:
                instance_dict["instance_id"] = CrsObject("instance").object_resource_id(
                    instance_dict.get("instance_id"))

                resource_columns = {}
                for key, value in instance_dict.items():
                    if resource_values_config.get(key):
                        _values_configs = resource_values_config.get(key)
                        value = convert_value(value, _values_configs.get(value))

                    resource_columns[key] = value

                resource_columns = convert_keys(resource_columns, defines=resource_property, is_update=True)
                result.append(resource_columns)

        return result

    # def save_lb_instance(self, rid, lb_id, listener_id,
    #                      instance_id, port, weight,
    #                      provider, region):
    #     '''
    #
    #     :param rid:
    #     :param lb_id:
    #     :param listener_id:
    #     :param instance_id:
    #     :param port:
    #     :param weight:
    #     :param provider:
    #     :param region:
    #     :return:
    #     '''
    #     rid = get_uuid()
    #     self.resource_object.create(create_data={"id": rid, "provider": provider,
    #                                              "region": region,
    #                                              "lb_id": lb_id, "listener_id": listener_id,
    #                                              "instance_id": instance_id,
    #                                              "port": port, "weight": weight})

    def create(self, rid, name, provider_id,
               lb_id, listener_id, backend_servers,
               zone, region, extend_info, **kwargs):
        '''
        :param rid:
        :param name:
        :param provider_id:
        :param lb_id:
        :param port:
        :param protocol:
        :param backend_port:
        :param health_check:
        :param health_check_uri:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        create_data = {}
        _r_create_data = {"lb_id": lb_id, "listener_id": listener_id}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        create_data["backend_servers"] = self.validate_instance(provider_object["name"], instances=backend_servers)

        # for _instance_ in backend_servers:
        #     self.save_lb_instance("", lb_id, listener_id=listener_id,
        #                           instance_id=_instance_.get("instance_id"),
        #                           port=_instance_.get("port"), weight=_instance_.get("weight"),
        #                           provider=provider_object["name"], region=region)

        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=None,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res

    def destory(self, rid):
        '''
        :param rid:
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

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)

    def _generate_remove_instance(self, rid, provider, define_json, origin_instance_id):
        self.resource_info(provider)

        resource_name = self.resource_keys_config["property"]
        resource_property = self.resource_keys_config["resource_property"]

        column_server = convert_key_only("backend_servers",
                                         define=resource_property.get("backend_servers", "backend_servers"))
        column_instance = convert_key_only("instance_id",
                                           define=resource_property.get("instance_id", "instance_id"))

        _t = define_json["resource"][resource_name]
        label_name = self.resource_name + "_" + rid
        origin_columns = _t[label_name]

        instances = origin_columns[column_server]
        new_instances = []
        for instance in instances:
            if instance.get(column_instance) != origin_instance_id:
                new_instances.append(instance)

        origin_columns[column_server] = new_instances

        define_json["resource"] = {
            resource_name: {
                label_name: origin_columns
            }
        }
        logger.info("_generate_remove_instance format json: %s" % (format_json_dumps(define_json)))
        return define_json

    def remove_instance(self, rid, instance_id):
        '''

        :param rid:
        :param instance_id:
        :return:
        '''

        resource_info = self.resource_object.show(rid)

        _filter_instance = {}
        if resource_info["lb_id"]:
            _filter_instance["lb_id"] = resource_info["lb_id"]
        if resource_info["listener_id"]:
            _filter_instance["listener_id"] = resource_info["listener_id"]

        _filter_instance["instance_id"] = instance_id
        # _attach_status = LBAttachInstanceObject().query_one(where_data=_filter_instance)
        # if not _attach_status:
        #     raise local_exceptions.ResourceValidateError("lb attach instance", "lb %s 未关联实例 %s" % (rid, instance_id))
        _instance_data = CrsObject("instance").ora_show(rid=instance_id)

        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        if not self.destory_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        define_json = self._generate_remove_instance(rid, provider=resource_info["provider"],
                                                     define_json=resource_info["define_json"],
                                                     origin_instance_id=_instance_data["resource_id"])

        self.write_define(rid, _path, define_json=define_json)
        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="detach %s %s failed" % (self.resource_name, rid))

        count, data = self.resource_object.update(rid, update_data={"define_json": define_json})

        return count
