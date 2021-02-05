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


class RouteTableApi(ApiBase):
    def __init__(self):
        super(RouteTableApi, self).__init__()
        self.resource_name = "route_table"
        self.resource_workspace = "route_table"
        self.owner_resource = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject(self.owner_resource).object_resource_id(vpc_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def create(self, rid, name, provider_id, vpc_id,
               zone, region, extend_info, **kwargs):
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
            return 1, _exists_data

        extend_info = extend_info or {}
        create_data = {"name": name}
        _r_create_data = {"vpc_id": vpc_id}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=vpc_id,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res

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
