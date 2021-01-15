# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from core import local_exceptions
from lib.json_helper import format_json_dumps
from lib.logs import logger
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.vpc import VpcObject
from apps.api.apibase import ApiBase


class VpcApi(ApiBase):
    def __init__(self):
        super(VpcApi, self).__init__()
        self.resource_name = "vpc"
        self.resource_workspace = "vpc"
        self.resource_object = VpcObject()
        self.resource_keys_config = None

    def formate_result(self, result):
        # todo 获取vpc创建信息
        return result

    def save_data(self, rid, name, provider,
                  provider_id, region, zone,
                  cidr, extend_info, define_json,
                  status, result_json):
        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "cidr": cidr,
                                                 "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, cidr, provider_id, region, extend_info, **kwargs):
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

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        create_data = {"cidr": cidr, "name": name}

        define_json = self._generate_resource(provider_object["name"], rid,
                                              data=create_data, extend_info=extend_info)
        define_json.update(provider_info)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       provider_id=provider_id,
                       provider=provider_object["name"],
                       region=region, cidr=cidr,
                       zone="",
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
        _update_data.update(self._read_other_result(result))
        self.update_data(rid, data=_update_data)

        return rid

    def destory(self, rid):
        resource_info = self.resource_object.show(rid)
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        status = self.run_destory(_path)
        if status == 2021:
            self.write_define(rid, _path, define_json=resource_info["define_json"])
            status = self.run_destory(_path)
            if not status:
                raise local_exceptions.ResourceOperateException(self.resource_name,
                                                                msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)
