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


class EipAssociationApi(ApiBase):
    def __init__(self):
        super(EipAssociationApi, self).__init__()
        self.resource_name = "eip_association"
        self.resource_workspace = "eip_association"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param eip_id:
        :param instance_id:
        :param eni_id:
        :return:
        '''

        eip_id = create_data.get("eip_id")
        instance_id = create_data.get("instance_id")
        eni_id = create_data.get("eni_id")

        # todo 校验instance eni 弹性网卡
        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _eip_status = define_relations_key("eip_id", eip_id, resource_property.get("eip_id"))
        _instance_status = define_relations_key("instance_id", instance_id,
                                                resource_property.get("instance_id"))

        ext_info = {}
        if eip_id and (not _eip_status):
            ext_info["eip_id"] = CrsObject("eip").object_resource_id(eip_id)
        if instance_id and (not _instance_status):
            ext_info["instance_id"] = CrsObject("instance").object_resource_id(instance_id)
        if eni_id:
            # 统一不使用eni
            pass

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def create(self, rid, name, provider_id, eip_id,
               instance_id, eni_id, private_ip,
               zone, region, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param eip_id:
        :param zone:
        :param region:
        :param extend_info:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        # todo 依据不同云厂商， 转换对应的参(参考resource_property 定义)
        extend_info = extend_info or {}

        create_data = {"private_ip": private_ip, }

        _r_create_data = {"eip_id": eip_id,
                          "instance_id": instance_id, "eni_id": eni_id}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=None,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
