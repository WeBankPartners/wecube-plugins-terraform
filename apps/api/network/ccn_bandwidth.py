# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.common.convert_keys import define_relations_key
from apps.background.resource.configr.resource import ResourceObject
from apps.background.resource.resource_base import CrsObject


class CCNBandwidthApi(ApiBase):
    def __init__(self):
        super(CCNBandwidthApi, self).__init__()
        self.resource_name = "ccn_bandwidth"
        self.resource_workspace = "ccn_bandwidth"
        self.owner_resource = "ccn"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        ccn_id = create_data.get("ccn_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _ccn_status = define_relations_key("ccn_id", ccn_id, resource_property.get("ccn_id"))

        ext_info = {}
        if ccn_id and (not _ccn_status):
            ext_info["ccn_id"] = CrsObject(self.owner_resource).object_resource_id(ccn_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def region_name(self, provider, region):
        return ProviderApi().region_info(provider, region)

    def create(self, rid, name, provider_id, ccn_id,
               from_region, dest_region, bandwidth,
               region, zone, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param region:
        :param zone:
        :param extend_info:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        create_data = {"bandwidth": bandwidth, "ccn_id": ccn_id}
        _r_create_data = {"ccn_id": ccn_id}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)

        if from_region:
            create_data["from_region"] = self.region_name(provider_object["name"], from_region)
        if dest_region:
            create_data["dest_region"] = self.region_name(provider_object["name"], dest_region)

        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=ccn_id,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
