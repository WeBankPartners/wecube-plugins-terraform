# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.vpc import VpcObject
from apps.background.resource.network.route_table import RouteTableObject


class RouteTableApi(ApiBase):
    def __init__(self):
        super(RouteTableApi, self).__init__()
        self.resource_name = "route_table"
        self.resource_workspace = "route_table"
        self.resource_object = RouteTableObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, vpc_id):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = VpcObject().vpc_resource_id(vpc_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, name, vpc,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param name:
        :param vpc:
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
                                                 "region": region, "zone": zone,
                                                 "name": name,
                                                 "vpc": vpc, "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id, vpc_id,
               zone, region, extend_info):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param vpc_id:
        :param zone:
        :param region:
        :param extend_info:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return _exists_data

        extend_info = extend_info or {}
        create_data = {"name": name}
        label_name = self.resource_name + "_" + rid

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], vpc_id)

        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"],
                                              label_name=label_name,
                                              data=create_data, extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

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

        self.init_workspace(_path, provider_object["name"])

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data = {"status": "ok", "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        if not _update_data.get("resource_id"):
            _update_data["resource_id"] = self._fetch_id(result)

        _, res = self.update_data(rid, data=_update_data)

        return rid, res

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

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        return self.update_data(rid, data={"status": "ok", "name": name,
                                           "define_json": json.dumps(define_json)})
