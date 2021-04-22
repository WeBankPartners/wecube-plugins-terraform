# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase_backend import ApiBackendBase


class Common(object):

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")
        subnet_id = create_data.get("subnet_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _subnet_status = define_relations_key("subnet", subnet_id, resource_property.get("subnet_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject("vpc").object_resource_id(vpc_id)
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = CrsObject("subnet").object_resource_id(subnet_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("vpc_id"),
                         "subnet_id": create_data.get("subnet_id")}
        create_data = {"network_type": create_data.get("network_type"),
                       "name": create_data.get("name")}

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None


class LBApi(Common, ApiBase):
    def __init__(self):
        super(LBApi, self).__init__()
        self.resource_name = "lb"
        self.resource_workspace = "lb"
        self._flush_resobj()
        self.resource_keys_config = None


class LBBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(LBBackendApi, self).__init__()
        self.resource_name = "lb"
        self.resource_workspace = "lb"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_source_asset(self, provider, query_data):
        for key in ["vpc_id", "subnet_id"]:
            if query_data.get(key):
                query_data[key] = CrsObject().object_asset_id(query_data.get(key))

        return query_data

    def reverse_asset_ids(self):
        return ['vpc_id', "subnet_id"]

