# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
# from apps.background.resource.network.vpc import VpcObject
# from apps.background.resource.network.route_table import RouteTableObject
from apps.background.resource.resource_base import CrsObject
from apps.api.conductor.provider import ProviderConductor
from apps.api.apibase_backend import ApiBackendBase


class PeerConnApi(ApiBase):
    def __init__(self):
        super(PeerConnApi, self).__init__()
        self.resource_name = "peer_connection"
        self.resource_workspace = "peer_connection"
        self.owner_resource = ""
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")
        peer_vpc_id = create_data.get("peer_vpc_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject(self.owner_resource).object_resource_id(vpc_id)
        if peer_vpc_id and (not _vpc_status):
            ext_info["peer_vpc_id"] = CrsObject(self.owner_resource).object_resource_id(peer_vpc_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("vpc_id"),
                         "peer_vpc_id": create_data.get("peer_vpc_id")}
        create_data = {
            "name": create_data.get("name")
        }

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        return None, None

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

        x_create_data, r_create_data = self.generate_create_data(zone, create_data,
                                                                 provider=provider_object["name"])
        peer_region = create_data.get("region")
        if peer_region:
            peer_region = ProviderConductor().region_info(provider=provider_object["name"], region=peer_region)
            x_create_data["peer_region"] = peer_region

        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

        x_create_data.update(_relations_id_dict)

        owner_id, relation_id = self.generate_owner_data(create_data)
        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=owner_id, relation_id=relation_id,
                                     create_data=x_create_data,
                                     extend_info=extend_info,
                                     **kwargs)

        return count, res


class PeerConnBackendApi(ApiBackendBase):
    def __init__(self):
        super(PeerConnBackendApi, self).__init__()
        self.resource_name = "peer_connection"
        self.resource_workspace = "peer_connection"
        self.owner_resource = ""
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")
        peer_vpc_id = create_data.get("peer_vpc_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject(self.owner_resource).object_resource_id(vpc_id)
        if peer_vpc_id and (not _vpc_status):
            ext_info["peer_vpc_id"] = CrsObject(self.owner_resource).object_resource_id(peer_vpc_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("vpc_id"),
                         "peer_vpc_id": create_data.get("peer_vpc_id")}
        create_data = {
            "name": create_data.get("name")
        }

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        return None, None

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

        extend_info = extend_info or {}
        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        x_create_data, r_create_data = self.generate_create_data(zone, create_data,
                                                                 provider=provider_object["name"])
        peer_region = create_data.get("region")
        if peer_region:
            peer_region = ProviderConductor().region_info(provider=provider_object["name"], region=peer_region)
            x_create_data["peer_region"] = peer_region

        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

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
