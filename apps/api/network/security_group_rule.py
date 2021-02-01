# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.convert_keys import define_relations_key
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

    def before_keys_checks(self, provider, security_group_id):
        '''

        :param provider:
        :param security_group_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _sg_status = define_relations_key("security_group_id", security_group_id,
                                          resource_property.get("security_group_id"))

        ext_info = {}
        if security_group_id and (not _sg_status):
            ext_info["security_group_id"] = SecGroupObject().resource_id(security_group_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, name, security_group_id,
                  cidr_ip, ip_protocol, type,
                  description, ports, policy,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param name:
        :param security_group_id:
        :param cidr_ip:
        :param ip_protocol:
        :param type:
        :param description:
        :param ports:
        :param policy:
        :param provider:
        :param provider_id:
        :param region:
        :param zone:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

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
               zone, region, extend_info):
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

        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid

        description = description or "%s_%s_%s" % (type, ip_protocol, ports)
        name = name or description
        create_data = {"description": description,
                       "type": type, "ports": ports,
                       "cidr_ip": cidr_ip,
                       "ip_protocol": ip_protocol,
                       "policy": policy}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], security_group_id)

        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"], label_name=label_name,
                                              data=create_data, extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

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

        self.init_workspace(_path, provider_object["name"])

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data = {"status": "ok", "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        if not _update_data.get("resource_id"):
            _update_data["resource_id"] = self._fetch_id(result)

        _, res = self.update_data(rid, data=_update_data)

        return rid, res
