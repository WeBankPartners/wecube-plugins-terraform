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


class RouteEntryApi(ApiBase):
    def __init__(self):
        super(RouteEntryApi, self).__init__()
        self.resource_name = "route_entry"
        self.resource_workspace = "route_entry"
        self.owner_resource = "route_table"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param vpc_id:
        :param route_table_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")
        route_table_id = create_data.get("route_table_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _rt_status = define_relations_key("route_table_id", route_table_id, resource_property.get("route_table_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject("vpc").object_resource_id(vpc_id)
        if route_table_id and (not _rt_status):
            ext_info["route_table_id"] = CrsObject(self.owner_resource).object_resource_id(route_table_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def create(self, rid, name, provider_id, zone, region,
               vpc_id, route_table, next_type, next_hub,
               destination, extend_info, **kwargs):

        '''

        :param rid:
        :param name:
        :param provider_id:
        :param zone:
        :param region:
        :param vpc_id:
        :param route_table:
        :param next_type:
        :param next_hub:
        :param destination:
        :param extend_info:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        # todo 依据不同的next type转化不同的id
        extend_info = extend_info or {}

        create_data = {"name": name,
                       "destination": destination,
                       "next_type": next_type,
                       "next_hub": next_hub
                       }

        _r_create_data = {"vpc_id": vpc_id,
                          "route_table_id": route_table}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=route_table,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
