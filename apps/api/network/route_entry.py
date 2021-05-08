# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.convert_keys import define_relations_key
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase import ApiBase
from apps.api.conductor.valueReverse import ValueResetConductor
from apps.api.apibase_backend import ApiBackendBase


class Common(object):

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :param route_table_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")
        route_table_id = create_data.get("route_table_id")
        next_hub = create_data.get("next_hub")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _rt_status = define_relations_key("route_table_id", route_table_id, resource_property.get("route_table_id"))
        _ne_status = define_relations_key("next_hub", next_hub, resource_property.get("next_hub"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject("vpc").object_resource_id(vpc_id)
        if route_table_id and (not _rt_status):
            ext_info["route_table_id"] = CrsObject(self.owner_resource).object_resource_id(route_table_id)
        if next_hub and (not _ne_status):
            ext_info["next_hub"] = CrsObject(self.owner_resource).object_resource_assetid(next_hub)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("vpc_id"),
                         "next_hub": create_data.get("next_hub"),
                         "route_table_id": create_data.get("route_table_id")}

        create_data = {"name": create_data.get("name"),
                       "destination": create_data.get("destination"),
                       "next_type": create_data.get("next_type"),
                       }

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = create_data.get("route_table_id")
        return owner_id, None


class RouteEntryApi(Common, ApiBase):
    def __init__(self):
        super(RouteEntryApi, self).__init__()
        self.resource_name = "route_entry"
        self.resource_workspace = "route_entry"
        self.owner_resource = "route_table"
        self._flush_resobj()
        self.resource_keys_config = None


class RouteEntryBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(RouteEntryBackendApi, self).__init__()
        self.resource_name = "route_entry"
        self.resource_workspace = "route_entry"
        self.owner_resource = "route_table"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_source_asset(self, provider, query_data):
        for key in ["route_table_id", "vpc_id", "next_hub"]:
            if query_data.get(key):
                query_data[key] = CrsObject().object_asset_id(query_data.get(key))

        return query_data

    def reverse_asset_ids(self):
        return ['vpc_id', "route_table_id", "next_hub"]

    def run_query(self, rid, region, zone,
                  provider_object, provider_info,
                  query_data, **kwargs):
        '''

        :param rid:
        :param region:
        :param zone:
        :param owner_id:
        :param relation_id:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        # extend_info = extend_info or {}
        label_name = self.resource_name + "_q_" + rid

        define_json, resource_keys_config = self.source_filter_controller(provider_name=provider_object["name"],
                                                                          label_name=label_name,
                                                                          query_data=query_data
                                                                          )

        result = self._run_create_and_read_result(rid, provider=provider_object["name"],
                                                  region=region, provider_info=provider_info,
                                                  define_json=define_json)

        data_source_argument = resource_keys_config.get("data_source_argument")
        output_json = self.read_query_result_controller(provider_object["name"], result,
                                                        data_source_argument)

        result_list = []
        for out_data in output_json:
            count = 0
            for _, x_value in out_data.items():
                if not x_value:
                    count += 1
            if count == len(out_data):
                logger.info("out data columns is null, skip ...")
                continue

            x_json = ValueResetConductor().reset_values(provider=provider_object["name"],
                                                        resource_name=self.resource_name,
                                                        data=out_data)

            x_json = self.reverse_asset_object(provider=provider_object["name"], data=x_json)
            result_list.append(x_json)

        return result_list
