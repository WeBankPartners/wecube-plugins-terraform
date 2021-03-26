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

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"eip_id": create_data.get("eip_id"),
                         "instance_id": create_data.get("instance_id"),
                         "eni_id": create_data.get("eni_id")}
        create_data = {"private_ip": create_data.get("private_ip")}

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None


class EipAssociationApi(Common, ApiBase):
    def __init__(self):
        super(EipAssociationApi, self).__init__()
        self.resource_name = "eip_association"
        self.resource_workspace = "eip_association"
        self._flush_resobj()
        self.resource_keys_config = None


class EipAssociationBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(EipAssociationBackendApi, self).__init__()
        self.resource_name = "eip_association"
        self.resource_workspace = "eip_association"
        self._flush_resobj()
        self.resource_keys_config = None
