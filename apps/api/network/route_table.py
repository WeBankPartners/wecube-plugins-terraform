# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.vpc import VpcObject
from apps.background.resource.network.route_table import RouteTableObject
from apps.api.apibase import ApiBase


class RouteTableApi(ApiBase):
    def __init__(self):
        super(RouteTableApi, self).__init__()
        self.resource_name = "route_table"
        self.resource_workspace = "route_table"
        self.resource_object = RouteTableObject()
        self.resource_keys_config = None

    def formate_result(self, result):
        return result

    def save_data(self, rid, name, vpc,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name,
                                                 "vpc": vpc, "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id, vpc_id,
               zone, region, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param cidr:
        :param provider_id:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        extend_info = extend_info or {}
        vpc_resource_id = VpcObject().vpc_resource_id(vpc_id)

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)

        create_data = {"name": name, "vpc_id": vpc_resource_id}
        define_json = self._generate_resource(provider_object["name"], rid,
                                          data=create_data, extend_info=extend_info)

        define_json.update(provider_info)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       vpc=vpc_id,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))
        resource_id = self._fetch_id(result)

        _update_data = {"status": "ok",
                        "resource_id": resource_id,
                        "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))
        self.update_data(rid, data=_update_data)

        return rid

    def update(self, rid, name, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _obj = self.resource_object.show(rid)
        if not _obj:
            raise local_exceptions.ResourceNotFoundError("Route Table %s 不存在" % rid)

        vpc_resource_id = _obj.get("vpc")

        provider_object, provider_info = ProviderApi().provider_info(_obj["provider_id"],
                                                                     region=_obj["region"])
        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=_obj["region"])

        create_data = {"name": name, "vpc_id": vpc_resource_id}

        define_json = self._generate_resource(provider_object["name"], rid,
                                          data=create_data, extend_info=extend_info)
        define_json.update(provider_info)

        self.update_data(rid, data={"status": "updating"})
        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        return self.update_data(rid, data={"status": "ok", "name": name,
                                           "define_json": json.dumps(define_json)})
