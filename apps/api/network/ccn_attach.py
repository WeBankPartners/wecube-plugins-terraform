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
from apps.background.resource.network.vpc import VpcObject
from apps.background.resource.network.connnect_network import CCNObject
from apps.background.resource.network.connnect_network import CCNAttachObject


class CCNAttachApi(ApiBase):
    def __init__(self):
        super(CCNAttachApi, self).__init__()
        self.resource_name = "ccn_attach"
        self.resource_workspace = "ccn_attach"
        self.resource_object = CCNAttachObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, ccn_id, vpc_id):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _vpc_status = define_relations_key("instance_id", vpc_id, resource_property.get("instance_id"))
        _ccn_status = define_relations_key("ccn_id", ccn_id, resource_property.get("ccn_id"))

        ext_info = {}
        if vpc_id and (not _vpc_status):
            ext_info["instance_id"] = VpcObject().vpc_resource_id(vpc_id)
        if ccn_id and (not _ccn_status):
            ext_info["ccn_id"] = CCNObject().resource_id(ccn_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, name, ccn_id, instance_id,
                  instance_type, instance_region,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param name:
        :param ccn_id:
        :param instance_id:
        :param instance_type:
        :param instance_region:
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
                                                 "status": status, "ccn_id": ccn_id,
                                                 "instance_type": instance_type,
                                                 "instance_region": instance_region,
                                                 "instance_id": instance_id,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def region_name(self, provider, region):
        return ProviderApi().region_info(provider, region)

    def create(self, rid, name, provider_id,
               ccn_id, instance_id,
               instance_type, instance_region,
               region, zone, extend_info):

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

        instance_type = instance_type or "VPC"
        extend_info = extend_info or {}
        create_data = {"instance_type": instance_type}
        label_name = self.resource_name + "_" + rid

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)

        if instance_region:
            create_data["instance_region"] = self.region_name(provider_object["name"], instance_region)

        _relations_id_dict = self.before_keys_checks(provider_object["name"], ccn_id,
                                                     vpc_id=instance_id)

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
                       ccn_id=ccn_id, instance_id=instance_id,
                       instance_region=instance_region,
                       instance_type=instance_type,
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

        _update_data = {"status": "ok", "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        if not _update_data.get("resource_id"):
            _update_data["resource_id"] = self._fetch_id(result)

        _, res = self.update_data(rid, data=_update_data)

        return rid, res
