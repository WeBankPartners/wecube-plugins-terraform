# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import local_exceptions
from apps.api.apibase import ApiBase
from apps.api.apibase_backend import ApiBackendBase


class ObjectStorageApi(ApiBase):
    def __init__(self):
        super(ObjectStorageApi, self).__init__()
        self.resource_name = "object_storage"
        self.resource_workspace = "object_storage"
        self._flush_resobj()
        self.resource_keys_config = None

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {}

        name = create_data.get("name")
        appid = create_data.get("appid")
        if appid:
            name = "%s-%s" % (name, appid)

        x_create_data = {"acl": create_data.get("acl"),
                         "name": name}

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


class ObjectStorageBackendApi(ApiBackendBase):
    def __init__(self):
        super(ObjectStorageBackendApi, self).__init__()
        self.resource_name = "object_storage"
        self.resource_workspace = "object_storage"
        self._flush_resobj()
        self.resource_keys_config = None
