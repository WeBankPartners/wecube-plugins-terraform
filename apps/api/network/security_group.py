# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
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

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject(self.relation_resource).object_resource_id(vpc_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("vpc_id")}
        create_data = {"name": create_data.get("name")}

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        r_id = create_data.get("vpc_id")
        return None, r_id

    def sg_vpc_relationship(self, rid, provider, region, zone, secret,
                            resource_id, **kwargs):

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", "0000000", resource_property.get("vpc_id"))
        if _vpc_status:
            return []
        else:
            return self.get_remote_source(rid, provider, region, zone, secret,
                                          resource_id, **kwargs)


class SecGroupApi(Common, ApiBase):
    def __init__(self):
        super(SecGroupApi, self).__init__()
        self.resource_name = "security_group"
        self.resource_workspace = "security_group"
        self.relation_resource = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None


class SecGroupBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(SecGroupBackendApi, self).__init__()
        self.resource_name = "security_group"
        self.resource_workspace = "security_group"
        self.relation_resource = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_source_asset(self, provider, query_data):
        for key in ["vpc_id"]:
            if query_data.get(key):
                query_data[key] = CrsObject().object_asset_id(query_data.get(key))

        return query_data

    def reverse_asset_ids(self):
        return ['vpc_id']
