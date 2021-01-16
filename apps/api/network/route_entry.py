# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.vpc import VpcObject
from apps.background.resource.network.route_table import RouteTableObject
from apps.background.resource.network.route_entry import RouteEntryObject


class RouteEntryApi(ApiBase):
    def __init__(self):
        super(RouteEntryApi, self).__init__()
        self.resource_name = "route_entry"
        self.resource_workspace = "route_entry"
        self.resource_object = RouteEntryObject()
        self.resource_keys_config = None

    def save_data(self, rid, name, vpc, destination,
                  route_table, next_type, next_hub,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param name:
        :param vpc:
        :param destination:
        :param route_table:
        :param next_type:
        :param next_hub:
        :param provider:
        :param provider_id:
        :param region:
        :param zone:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "provider_id": provider_id,
                                                 "region": region, "zone": zone,
                                                 "name": name, "vpc": vpc,
                                                 "route_table": route_table,
                                                 "next_type": next_type,
                                                 "next_hub": next_hub,
                                                 "status": status,
                                                 "destination": destination,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def before_keys_checks(self, provider, vpc_id, route_table_id):
        '''

        :param provider:
        :param vpc_id:
        :param route_table_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _rt_status = define_relations_key("route_table_id", route_table_id, resource_property.get("route_table_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = VpcObject().vpc_resource_id(vpc_id)
        if route_table_id and (not _rt_status):
            ext_info["route_table_id"] = RouteTableObject().routeTable_resource_id(route_table_id)

        return ext_info

    def create(self, rid, name, provider_id, zone, region,
               vpc_id, route_table, next_type, next_hub,
               destination, extend_info):

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

        # todo 依据不同的next type转化不同的id
        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid
        create_data = {"name": name,
                       "destination": destination,
                       "next_type": next_type,
                       "next_hub": next_hub}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], vpc_id, route_table)

        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"], rid,
                                              data=create_data, extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       vpc=vpc_id, route_table=route_table,
                       next_type=next_type, next_hub=next_hub,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       destination=destination,
                       region=region, zone=zone,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data = {"status": "ok", "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        if not _update_data.get("resource_id"):
            _update_data["resource_id"] = self._fetch_id(result)

        self.update_data(rid, data=_update_data)

        return rid
