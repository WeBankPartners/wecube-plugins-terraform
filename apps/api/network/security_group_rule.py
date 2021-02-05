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


class SecGroupRuleApi(ApiBase):
    def __init__(self):
        super(SecGroupRuleApi, self).__init__()
        self.resource_name = "security_group_rule"
        self.resource_workspace = "security_group_rule"
        self.owner_resource = "security_group"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
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

    def create(self, rid, name, provider_id,
               security_group_id, type,
               cidr_ip, ip_protocol,
               ports, policy, description,
               zone, region, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param security_group_id:
        :param type:
        :param cidr_ip:
        :param ip_protocol:
        :param ports:
        :param policy:
        :param description:
        :param zone:
        :param region:
        :param extend_info:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        description = description or "%s_%s_%s" % (type, ip_protocol, ports)

        create_data = {"description": description,
                       "type": type, "ports": ports,
                       "cidr_ip": cidr_ip,
                       "ip_protocol": ip_protocol,
                       "policy": policy}

        _r_create_data = {"security_group_id": security_group_id}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=security_group_id,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
