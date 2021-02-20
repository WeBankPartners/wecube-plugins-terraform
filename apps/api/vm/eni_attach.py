# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.configer.provider import ProviderApi
from apps.api.apibase import ApiBase
# from apps.background.resource.vm.eni import ENIObject
# from apps.background.resource.vm.eni import ENIAttachObject
# from apps.background.resource.vm.instance import InstanceObject
from apps.background.resource.resource_base import CrsObject


class ENIAttachApi(ApiBase):
    def __init__(self):
        super(ENIAttachApi, self).__init__()
        self.resource_name = "network_interface_attach"
        self.resource_workspace = "network_interface_attach"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        instance_id = create_data.get("instance_id")
        eni_id = create_data.get("network_interface_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _instance_status = define_relations_key("instance_id", instance_id, resource_property.get("instance_id"))
        _eni_status = define_relations_key("disk_id", eni_id, resource_property.get("eni_id"))

        ext_info = {}
        if instance_id and (not _instance_status):
            ext_info["instance_id"] = CrsObject("instance_id").object_resource_id(instance_id)
        if eni_id and (not _eni_status):
            ext_info["network_interface_id"] = CrsObject("network_interface").object_resource_id(eni_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"instance_id": create_data.get("instance_id"),
                         "network_interface_id": create_data.get("network_interface_id")}
        x_create_data = {}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None

    def attach(self, rid, provider, region, zone, secret,
               create_data, extend_info, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param zone:
        :param secret:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        return self.create(rid, provider, region, zone, secret,
                           create_data, extend_info, **kwargs)

    def detach(self, rid):
        '''

        :param rid:
        :return:
        '''

        resource_info = self.resource_object.show(rid)
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        if not self.destory_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="network interface detach %s %s failed" % (
                                                                self.resource_name, rid))

        return self.resource_object.delete(rid)
