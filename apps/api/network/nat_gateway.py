# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.vpc import VpcObject
from apps.background.resource.network.subnet import SubnetObject
from apps.background.resource.network.eip import EipObject
from apps.background.resource.network.nat_gateway import NatGatewayObject


class NatGatewayApi(ApiBase):
    def __init__(self):
        super(NatGatewayApi, self).__init__()
        self.resource_name = "nat"
        self.resource_workspace = "nat"
        self.resource_object = NatGatewayObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, vpc_id, subnet_id, eip):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _subnet_status = define_relations_key("subnet_id", subnet_id, resource_property.get("subnet_id"))
        _eip_status = define_relations_key("eip", eip, resource_property.get("eip"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = VpcObject().vpc_resource_id(vpc_id)
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = SubnetObject().subnet_resource_id(subnet_id)
        if eip and (not _eip_status):
            # eip 特殊处理
            _eip_ip = eip.split(",")
            for _ip in _eip_ip:
                EipObject().eip_resource_id(_ip)
            ext_info["eip"] = eip

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, name, vpc,
                  subnet, ipaddress,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param name:
        :param vpc:
        :param subnet:
        :param ipaddress:
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
        if ipaddress:
            # todo 处理其他ipaddress情况
            if isinstance(ipaddress, list):
                ipaddress = ",".join(ipaddress)

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "ipaddress": ipaddress,
                                                 "vpc": vpc, "subnet": subnet,
                                                 "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id,
               vpc_id, subnet_id, eip,
               zone, region, extend_info):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param vpc_id:
        :param subnet_id:
        :param eip:
        :param zone:
        :param region:
        :param extend_info:
        :return:
        '''

        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid

        create_data = {"name": name}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"],
                                                     vpc_id=vpc_id, subnet_id=subnet_id,
                                                     eip=eip)

        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"],
                                              label_name=label_name,
                                              data=create_data, extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       vpc=vpc_id, subnet=subnet_id,
                       ipaddress=eip,
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

        _, data = self.update_data(rid, data=_update_data)
        return rid, data
