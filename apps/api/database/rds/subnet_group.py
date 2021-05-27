# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
from core import local_exceptions
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.api.configer.provider import ProviderApi
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.common.convert_keys import validate_type
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase_backend import ApiBackendBase


class SubnetGroupApi(ApiBase):
    def __init__(self):
        super(SubnetGroupApi, self).__init__()
        self.resource_name = "db_subnet_group"
        self.resource_workspace = "db_subnet_group"
        self.owner_resource = "rds"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param subnet_id:
        :return:
        '''

        subnet_id = create_data.get("subnet_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _subnet_status = define_relations_key("subnet_id", subnet_id, resource_property.get("subnet_id"))

        ext_info = {}
        if subnet_id and (not _subnet_status):
            # ext_info["subnet_id"] = CrsObject("mysql").object_resource_id(subnet_id)

            sg_property = resource_property.get("subnet_id")
            if isinstance(sg_property, dict):
                if sg_property.get("type", "string") == "list":
                    sg_list = validate_type(subnet_id, "list")
                    _sg_resource_ids = []
                    for _sg in sg_list:
                        _sg_resource_ids.append(CrsObject("subnet").object_resource_id(_sg))
                else:
                    _sg_resource_ids = CrsObject("subnet").object_resource_id(subnet_id)

                ext_info["subnet_id"] = _sg_resource_ids
            else:
                ext_info["subnet_id"] = CrsObject("subnet").object_resource_id(subnet_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"subnet_id": create_data.get("subnet_id")}

        x_create_data = {"name": create_data.get("name")}
        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        # owner_id = create_data.get("subnet_id")
        return None, None


class SubnetGroupBackendApi(ApiBackendBase):
    def __init__(self):
        super(SubnetGroupBackendApi, self).__init__()
        self.resource_name = "db_subnet_group"
        self.resource_workspace = "db_subnet_group"
        self.owner_resource = "rds"
        self._flush_resobj()
        self.resource_keys_config = None
