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
from apps.background.resource.resource_base import CrsObject
from apps.api.conductor.provider import ProviderConductor
from apps.api.apibase_backend import ApiBackendBase


class CCNBandwidthApi(ApiBase):
    def __init__(self):
        super(CCNBandwidthApi, self).__init__()
        self.resource_name = "ccn_bandwidth"
        self.resource_workspace = "ccn_bandwidth"
        self.owner_resource = "ccn"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
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

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"ccn_id": create_data.get("ccn_id")}
        create_data = {
            "bandwidth": create_data.get("bandwidth"),
            "ccn_id": create_data.get("ccn_id")
        }

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None

    def create(self, rid, provider, region, zone, secret,
               create_data, extend_info, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param secret:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        zone = ProviderConductor().zone_info(provider=provider_object["name"], zone=zone)
        x_create_data, r_create_data = self.generate_create_data(zone, create_data)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

        from_region = create_data.get("from_region")
        dest_region = create_data.get("dest_region")
        if from_region:
            x_create_data["from_region"] = self.region_name(provider_object["name"], from_region)
        if dest_region:
            x_create_data["dest_region"] = self.region_name(provider_object["name"], dest_region)

        x_create_data.update(_relations_id_dict)

        owner_id, relation_id = self.generate_owner_data(create_data)
        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=owner_id, relation_id=relation_id,
                                     create_data=x_create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res


class CCNBandwidthBackendApi(ApiBackendBase):
    def __init__(self):
        super(CCNBandwidthBackendApi, self).__init__()
        self.resource_name = "ccn_bandwidth"
        self.resource_workspace = "ccn_bandwidth"
        self.owner_resource = "ccn"
        self._flush_resobj()
        self.resource_keys_config = None
