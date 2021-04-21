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
from apps.api.conductor.provider import ProviderConductor
from apps.api.apibase_backend import ApiBackendBase


class CCNAttachApi(ApiBase):
    def __init__(self):
        super(CCNAttachApi, self).__init__()
        self.resource_name = "ccn_attach"
        self.resource_workspace = "ccn_attach"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
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

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("instance_id"),
                         "ccn_id": create_data.get("ccn_id")}

        instance_type = create_data.get("instance_type") or "VPC"
        create_data = {"instance_type": instance_type}

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None

    def create(self, rid, provider, region, zone, secret,
               create_data, extend_info, **kwargs):

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

        extend_info = extend_info or {}
        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        zone = ProviderConductor().zone_info(provider=provider_object["name"], zone=zone)
        x_create_data, r_create_data = self.generate_create_data(zone, create_data)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

        instance_region = create_data.get("instance_region")
        if instance_region:
            create_data["instance_region"] = self.region_name(provider_object["name"], instance_region)

        x_create_data.update(_relations_id_dict)

        owner_id, relation_id = self.generate_owner_data(create_data)
        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=owner_id, relation_id=relation_id,
                                     create_data=x_create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res


class CCNAttachBackendApi(ApiBackendBase):
    def __init__(self):
        super(CCNAttachBackendApi, self).__init__()
        self.resource_name = "ccn_attach"
        self.resource_workspace = "ccn_attach"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
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

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("instance_id"),
                         "ccn_id": create_data.get("ccn_id")}

        instance_type = create_data.get("instance_type") or "VPC"
        create_data = {"instance_type": instance_type}

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None

    def apply(self, rid, provider, region, zone, secret,
              create_data, extend_info,
              asset_id=None, resource_id=None,
              **kwargs):
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

        region = self.region_object(provider, region)
        zone = self.zone_object(provider, zone)
        
        extend_info = extend_info or {}
        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        zone = ProviderConductor().zone_info(provider=provider_object["name"], zone=zone)
        x_create_data, r_create_data = self.generate_create_data(zone, create_data)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

        instance_region = create_data.get("instance_region")
        if instance_region:
            instance_region = self.region_object(provider_object["name"], instance_region)
            create_data["instance_region"] = self.region_name(provider_object["name"], instance_region)

        x_create_data.update(_relations_id_dict)

        owner_id, relation_id = self.generate_owner_data(create_data)
        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     asset_id=asset_id, resource_id=resource_id,
                                     owner_id=owner_id, relation_id=relation_id,
                                     create_data=x_create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
