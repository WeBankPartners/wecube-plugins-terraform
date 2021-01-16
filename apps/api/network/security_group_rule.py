# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.security_group import SecGroupObject
from apps.background.resource.network.security_group import SecGroupRuleObject


class SecGroupRuleApi(ApiBase):
    def __init__(self):
        super(SecGroupRuleApi, self).__init__()
        self.resource_name = "security_group_rule"
        self.resource_workspace = "security_group_rule"
        self.resource_object = SecGroupRuleObject()
        self.resource_keys_config = None

    def formate_result(self, result):
        return result

    def save_data(self, rid, name, security_group_id,
                  cidr_ip, ip_protocol, type,
                  description, ports, policy,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        description = description or "%s_%s_%s" % (type, ip_protocol, ports)
        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "security_group_id": security_group_id,
                                                 "name": name, "cidr_ip": cidr_ip,
                                                 "ip_protocol": ip_protocol, "type": type,
                                                 "ports": ports, "policy": policy,
                                                 "status": status, "description": description,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id,
               security_group_id, type,
               cidr_ip, ip_protocol,
               ports, policy, description,
               zone, region, extend_info, **kwargs):
        '''

        :param rid:
        :param security_group_id:
        :param type:
        :param cidr_ip:
        :param ip_protocol:
        :param ports:
        :param policy:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        secGroup_object_id = SecGroupObject().resource_id(security_group_id)

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)

        create_data = {"description": description,
                       "security_group_id": secGroup_object_id,
                       "type": type, "ports": ports,
                       "cidr_ip": cidr_ip,
                       "ip_protocol": ip_protocol,
                       "policy": policy}

        define_json = self._generate_resource(provider_object["name"], rid,
                                          data=create_data, extend_info=extend_info)

        define_json.update(provider_info)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       security_group_id=security_group_id,
                       cidr_ip=cidr_ip, ip_protocol=ip_protocol,
                       type=type, policy=policy,
                       description=description, ports=ports,
                       provider_id=provider_id,
                       region=region, zone=zone,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))
        resource_id = self._fetch_id(result)

        _update_data = {"status": "ok",
                        "resource_id": resource_id[:36],
                        "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))
        self.update_data(rid, data=_update_data)

        return rid
