# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import local_exceptions
from apps.api.apibase import ApiBase
from apps.api.conductor.provider import ProviderConductor
from apps.api.apibase_backend import ApiBackendBase


class DiskApi(ApiBase):
    def __init__(self):
        super(DiskApi, self).__init__()
        self.resource_name = "disk"
        self.resource_workspace = "disk"
        self._flush_resobj()
        self.resource_keys_config = None

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {}

        if zone:
            zone = ProviderConductor().zone_info(provider=kwargs.get("provider"),
                                                 zone=zone)

        x_create_data = {"type": create_data.get("type"),
                         "size": create_data.get("size"),
                         "charge_type": create_data.get("charge_type"),
                         "name": create_data.get("name"),
                         "zone": zone}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None

    def destroy(self, rid):
        '''

        :param rid:
        :return:
        '''

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


class DiskBackendApi(ApiBackendBase):
    def __init__(self):
        super(DiskBackendApi, self).__init__()
        self.resource_name = "disk"
        self.resource_workspace = "disk"
        self._flush_resobj()
        self.resource_keys_config = None
