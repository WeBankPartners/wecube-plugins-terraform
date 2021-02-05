# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.api.configer.provider import ProviderApi
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject


class DiskApi(ApiBase):
    def __init__(self):
        super(DiskApi, self).__init__()
        self.resource_name = "disk"
        self.resource_workspace = "disk"
        self._flush_resobj()
        self.resource_keys_config = None

    def create(self, rid, name, provider_id, type, size,
               zone, region, extend_info, **kwargs):

        '''

        :param rid:
        :param name:
        :param provider_id:
        :param type:
        :param size:
        :param zone:
        :param region:
        :param extend_info:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        create_data = {"name": name, "type": type, "size": size}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)

        if zone:
            zone = ProviderApi().zone_info(provider_object["name"], zone)

        create_data["zone"] = zone
        _relations_id_dict = self.before_keys_checks(provider_object["name"], create_data)
        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=None,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res

    def destory(self, rid):
        '''

        :param rid:
        :return:
        '''

        # todo 校验disk 没有attach到主机/没有被使用
        resource_info = self.resource_object.show(rid)
        if not resource_info:
            return 0
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        if not self.destory_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)
