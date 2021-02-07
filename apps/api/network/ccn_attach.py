# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.api.configer.provider import ProviderApi
from apps.api.apibase import ApiBase
from apps.common.convert_keys import define_relations_key
from apps.background.resource.resource_base import CrsObject


class CCNAttachApi(ApiBase):
    def __init__(self):
        super(CCNAttachApi, self).__init__()
        self.resource_name = "ccn_attach"
        self.resource_workspace = "ccn_attach"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''
        vpc_id = create_data.get("vpc_id")
        ccn_id = create_data.get("ccn_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("instance_id", vpc_id, resource_property.get("instance_id"))
        _ccn_status = define_relations_key("ccn_id", ccn_id, resource_property.get("ccn_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["instance_id"] = CrsObject("vpc").object_resource_id(vpc_id)
        if ccn_id and (not _ccn_status):
            ext_info["ccn_id"] = CrsObject("ccn").object_resource_id(ccn_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def region_name(self, provider, region):
        return ProviderApi().region_info(provider, region)

    def create(self, rid, name, provider_id,
               ccn_id, instance_id,
               instance_type, instance_region,
               region, zone, extend_info, **kwargs):

        '''

        :param rid:
        :param name:
        :param provider_id:
        :param ccn_id:
        :param instance_id:
        :param instance_type:
        :param instance_region:
        :param region:
        :param zone:
        :param extend_info:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        instance_type = instance_type or "VPC"
        extend_info = extend_info or {}
        create_data = {"instance_type": instance_type}

        _r_create_data = {"vpc_id": instance_id,
                          "ccn_id": ccn_id}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)

        if instance_region:
            create_data["instance_region"] = self.region_name(provider_object["name"], instance_region)

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
