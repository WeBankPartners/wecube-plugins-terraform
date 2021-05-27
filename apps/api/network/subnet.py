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
from apps.api.apibase_backend_v2 import ApiBackendBase


class SubnetApi(ApiBase):
    def __init__(self):
        super(SubnetApi, self).__init__()
        self.resource_name = "subnet"
        self.resource_workspace = "subnet"
        self.owner_resource = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject(self.owner_resource).object_resource_id(vpc_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("vpc_id")}
        x_create_data = {"cidr": create_data.get("cidr"),
                         "name": create_data.get("name"),
                         "zone": zone}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = create_data.get("vpc_id")
        return owner_id, None


class SubnetBackendApi(ApiBackendBase):
    def __init__(self):
        super(SubnetBackendApi, self).__init__()
        self.resource_name = "subnet"
        self.resource_workspace = "subnet"
        self._flush_resobj()
        self.resource_keys_config = None
