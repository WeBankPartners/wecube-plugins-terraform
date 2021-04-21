# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.api.apibase import ApiBase
from apps.api.conductor.provider import ProviderConductor
from apps.api.apibase_backend import ApiBackendBase
from apps.background.resource.resource_base import CrsObject


class Common(object):
    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {}

        if zone:
            zone = ProviderConductor().zone_info(provider=kwargs.get("provider"),
                                                 zone=zone)

        x_create_data = {"type": create_data.get("type"),
                         "size": create_data.get("size"),
                         "name": create_data.get("name"),
                         "zone": zone}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None


class DiskApi(Common, ApiBase):
    def __init__(self):
        super(DiskApi, self).__init__()
        self.resource_name = "disk"
        self.resource_workspace = "disk"
        self._flush_resobj()
        self.resource_keys_config = None

    def destroy(self, rid):
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

        if not self.destroy_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        status = self.run_destroy(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)


class DiskBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(DiskBackendApi, self).__init__()
        self.resource_name = "disk"
        self.resource_workspace = "disk"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_source_asset(self, provider, query_data):
        for key in ["instance_id"]:
            if query_data.get(key):
                query_data[key] = CrsObject().object_asset_id(query_data.get(key))

        return query_data
