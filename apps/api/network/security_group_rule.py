# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase_backend import ApiBackendBase


class Common(object):
    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param create_data:
        :return:
        '''

        security_group_id = create_data.get("security_group_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _sg_status = define_relations_key("security_group_id", security_group_id,
                                          resource_property.get("security_group_id"))

        ext_info = {}
        if security_group_id and (not _sg_status):
            ext_info["security_group_id"] = CrsObject(self.owner_resource).object_resource_id(security_group_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"security_group_id": create_data.get("security_group_id")}

        type = create_data.get("type")
        ports = create_data.get("ports")
        cidr_ip = create_data.get("cidr_ip")
        policy = create_data.get("policy")
        ip_protocol = create_data.get("ip_protocol")
        description = create_data.get("description")
        description = description or "%s_%s_%s" % (type, ip_protocol, ports)

        create_data = {"description": description,
                       "type": type, "ports": ports,
                       "cidr_ip": cidr_ip,
                       "ip_protocol": ip_protocol,
                       "policy": policy}

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = create_data.get("security_group_id")
        return owner_id, None


class SecGroupRuleApi(Common, ApiBase):
    def __init__(self):
        super(SecGroupRuleApi, self).__init__()
        self.resource_name = "security_group_rule"
        self.resource_workspace = "security_group_rule"
        self.owner_resource = "security_group"
        self._flush_resobj()
        self.resource_keys_config = None


class SecGroupRuleBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(SecGroupRuleBackendApi, self).__init__()
        self.resource_name = "security_group_rule"
        self.resource_workspace = "security_group_rule"
        self.owner_resource = "security_group"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_source_asset(self, provider, query_data):
        for key in ["security_group_id"]:
            if query_data.get(key):
                query_data[key] = CrsObject().object_asset_id(query_data.get(key))

        return query_data
