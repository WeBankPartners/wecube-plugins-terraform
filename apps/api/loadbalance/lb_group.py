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
        instance_id = create_data.get("instance_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _lb_status = define_relations_key("lb_id", lb_id, resource_property.get("lb_id"))
        _ins_status = define_relations_key("instance_id", instance_id,
                                          resource_property.get("instance_id"), is_update)

        ext_info = {}

        if lb_id and (not _lb_status):
            ext_info["lb_id"] = CrsObject("lb").object_resource_id(lb_id)
        if instance_id and (not _ins_status):
            sg_property = resource_property.get("instance_id")
            if isinstance(sg_property, dict):
                if sg_property.get("type", "string") == "list":
                    sg_list = validate_type(instance_id, "list")
                    _sg_resource_ids = []
                    for _sg in sg_list:
                        _sg_resource_ids.append(CrsObject("instance").object_resource_id(_sg))
                else:
                    _sg_resource_ids = CrsObject("instance").object_resource_id(instance_id)

                ext_info["instance_id"] = _sg_resource_ids
            else:
                ext_info["instance_id"] = CrsObject("instance_id").object_resource_id(instance_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {
            "lb_id": create_data.get("lb_id"),
            "instance_id": create_data.get("instance_id")
        }

        x_create_data = {}
        for key in ["name", "port"]:
            x_create_data[key] = create_data.get(key)
        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None


class LBGroupApi(Common, ApiBase):
    def __init__(self):
        super(LBGroupApi, self).__init__()
        self.resource_name = "lb_server_group"
        self.resource_workspace = "lb_server_group"
        self._flush_resobj()
        self.resource_keys_config = None


class LBGroupBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(LBGroupBackendApi, self).__init__()
        self.resource_name = "lb_server_group"
        self.resource_workspace = "lb_server_group"
        self._flush_resobj()
        self.resource_keys_config = None

