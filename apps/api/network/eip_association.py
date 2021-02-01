# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.eip import EipObject
from apps.background.resource.network.eip import EipAssociationObject
from apps.background.resource.vm.instance import InstanceObject


class EipAssociationApi(ApiBase):
    def __init__(self):
        super(EipAssociationApi, self).__init__()
        self.resource_name = "eip_association"
        self.resource_workspace = "eip_association"
        self.resource_object = EipAssociationObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, eip_id, instance_id, eni_id):
        '''

        :param provider:
        :param eip_id:
        :param instance_id:
        :param eni_id:
        :return:
        '''

        # todo 校验instance eni 弹性网卡
        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _eip_status = define_relations_key("eip_id", eip_id, resource_property.get("eip_id"))
        _instance_status = define_relations_key("instance_id", instance_id,
                                                resource_property.get("instance_id"))

        ext_info = {}
        if eip_id and (not _eip_status):
            ext_info["eip_id"] = EipObject().eip_resource_id(eip_id)
        if instance_id and (not _instance_status):
            ext_info["instance_id"] = InstanceObject().vm_resource_id(instance_id)
        if eni_id:
            # 统一不使用eni
            pass

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, name, eip, instance_id,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param name:
        :param eip:
        :param provider:
        :param provider_id:
        :param region:
        :param zone:
        :param instance_id:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "eip_id": eip,
                                                 "status": status, "instance_id": instance_id,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id, eip_id,
               instance_id, eni_id, private_ip,
               zone, region, extend_info):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param eip_id:
        :param zone:
        :param region:
        :param extend_info:
        :return:
        '''

        # todo 依据不同云厂商， 转换对应的参(参考resource_property 定义)
        extend_info = extend_info or {}

        create_data = {"private_ip": private_ip}
        label_name = self.resource_name + "_" + rid

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"],
                                                     eip_id=eip_id,
                                                     instance_id=instance_id,
                                                     eni_id=eni_id)

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
                       eip=eip_id,
                       instance_id=instance_id,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
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
