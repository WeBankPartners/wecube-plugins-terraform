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
from apps.background.resource.resource_base import CrsObject


class NatGatewayApi(ApiBase):
    def __init__(self):
        super(NatGatewayApi, self).__init__()
        self.resource_name = "nat"
        self.resource_workspace = "nat"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")
        subnet_id = create_data.get("subnet_id")
        eip = create_data.get("eip")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _subnet_status = define_relations_key("subnet_id", subnet_id, resource_property.get("subnet_id"))
        _eip_status = define_relations_key("eip", eip, resource_property.get("eip"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject("vpc").object_resource_id(vpc_id)
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = CrsObject("subnet").object_resource_id(subnet_id)
        if eip and (not _eip_status):
            # eip 特殊处理
            _eip_ip = eip.split(",")
            for _ip in _eip_ip:
                CrsObject("eip").object_resource_id(_ip)
            ext_info["eip"] = eip

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def create(self, rid, name, provider_id,
               vpc_id, subnet_id, eip,
               zone, region, extend_info, **kwargs):
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

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        create_data = {"name": name, "eip": eip}

        _r_create_data = {"vpc_id": vpc_id,
                          "subnet_id": subnet_id, }

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=vpc_id,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
