# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.eip import EipObject
from apps.background.resource.network.eip import EipAssociationObject
from apps.api.apibase import ApiBase


class EipAssociationApi(ApiBase):
    def __init__(self):
        super(EipAssociationApi, self).__init__()
        self.resource_name = "eip_association"
        self.resource_workspace = "eip_association"
        self.resource_object = EipAssociationObject()
        self.resource_keys_config = None

    def formate_result(self, result):
        return result

    def save_data(self, rid, name, eip,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "eip_id": eip,
                                                 "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id, eip_id,
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

        eip_resource_id = EipObject().eip_resource_id(eip_id)
        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)

        create_data = {"name": name, "eip_id": eip_resource_id}

        define_json = self._generate_resource(provider_object["name"], rid,
                                          data=create_data, extend_info=extend_info)

        define_json.update(provider_info)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       eip=eip_id,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
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
