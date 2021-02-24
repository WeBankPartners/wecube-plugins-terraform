# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.database.kvstore.kvstore_backup import KvBackupApi


class ResBase(object):
    @classmethod
    def allow_key(cls, data, keyname):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "extend_info", "backup_time",
                                      "backup_period", keyname])

    @classmethod
    def not_null(cls, data, keyname):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "zone",
                                          "backup_time", "backup_period", keyname]
                                    )

    @classmethod
    def validate_keys(cls, data, keyname):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "region", "zone",
                                               "provider", "secret", "backup_time",
                                               "backup_period", keyname],
                                      dicts=["extend_info"])

    @classmethod
    def create(cls, resource, data, keyname, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)
        name = data.pop("name", None)
        kvstore_id = data.pop(keyname, None)
        backup_time = data.pop("backup_time", None)
        backup_period = data.pop("backup_period", None)

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        d = dict(kvstore_id=kvstore_id,
                 backup_time=backup_time,
                 backup_period=backup_period)

        create_data = {"name": name}
        create_data.update(d)
        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    create_data=create_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return res, result


class KvBackupController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = KvBackupApi()

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        '''

        :param request:
        :param data:
        :param orderby:
        :param page:
        :param pagesize:
        :param kwargs:
        :return:
        '''

        validation.allowed_key(data, ["id", "provider", "region", "zone", "provider_id",
                                      'resource_id', "kvstore_id"])

        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def keyname(self):
        return "kvstore_id"

    def before_handler(self, request, data, **kwargs):
        keyname = self.keyname()
        ResBase.allow_key(data, keyname)
        ResBase.not_null(data, keyname)
        ResBase.validate_keys(data, keyname)

    def create(self, request, data, **kwargs):
        keyname = self.keyname()
        res, _ = ResBase.create(resource=self.resource, data=data, keyname=keyname)
        return 1, res


class KvBackupIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = KvBackupApi()

    def show(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        return self.resource.resource_object.show(rid)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        force_delete = data.get("force_delete", False)
        return self.resource.destory(rid, force_delete=force_delete)


class KvBackupAddController(BaseController):
    allow_methods = ("POST",)
    resource = KvBackupApi()

    def keyname(self):
        return "kvstore_id"

    def before_handler(self, request, data, **kwargs):
        keyname = self.keyname()
        ResBase.not_null(data, keyname)
        ResBase.validate_keys(data, keyname)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        keyname = self.keyname()
        res, _ = ResBase.create(resource=self.resource, data=data, keyname=keyname)
        return res


class KvBackupDeleteController(BaseController):
    name = "KvBackup"
    resource_describe = "KvBackup"
    allow_methods = ("POST",)
    resource = KvBackupApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["id"]
                                    )

        validation.validate_string("id", data.get("id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        force_delete = data.get("force_delete", False)
        result = self.resource.destory(rid, force_delete=force_delete)
        return {"result": result}
