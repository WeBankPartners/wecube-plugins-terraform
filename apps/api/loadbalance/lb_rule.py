# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.uuid_util import get_uuid
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import validate_type
from apps.common.convert_keys import convert_key_only
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase_backend import ApiBackendBase


class Common(object):
    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param lb_id:
        :param listener_id:
        :return:
        '''
        lb_id = create_data.get("lb_id")
        listener_id = create_data.get("listener_id")
        sg_id = create_data.get("security_group_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _ll_status = define_relations_key("listener_id", listener_id, resource_property.get("listener_id"))
        _lb_status = define_relations_key("lb_id", lb_id, resource_property.get("lb_id"))
        _sg_status = define_relations_key("security_group_id", sg_id,
                                          resource_property.get("security_group_id"), is_update)

        ext_info = {}
        if listener_id and (not _ll_status):
            ext_info["listener_id"] = CrsObject("lb_listener").object_resource_id(listener_id)
        if lb_id and (not _lb_status):
            ext_info["lb_id"] = CrsObject("lb").object_resource_id(lb_id)
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

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"lb_id": create_data.get("lb_id"),
                         "listener_id": create_data.get("listener_id"),
                         "security_group_id": create_data.get("security_group_id")}

        x_create_data = {}
        for key in ["frontend_port", "name", "domain", "url",
                    "health_check_http_code", "health_check_interval",
                    "health_check_uri", "health_check_connect_port",
                    "health_check_timeout", "health_check_http_method",
                    "scheduler", "certificate_id", "certificate_ca_id"]:
            x_create_data[key] = create_data.get(key)
        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None


class LBRuleApi(Common, ApiBase):
    def __init__(self):
        super(LBRuleApi, self).__init__()
        self.resource_name = "lb_rule"
        self.resource_workspace = "lb_rule"
        self._flush_resobj()
        self.resource_keys_config = None

    def destroy(self, rid):
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

        if not self.destroy_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        status = self.run_destroy(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)


class LBRuleBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(LBRuleBackendApi, self).__init__()
        self.resource_name = "lb_rule"
        self.resource_workspace = "lb_rule"
        self._flush_resobj()
        self.resource_keys_config = None
