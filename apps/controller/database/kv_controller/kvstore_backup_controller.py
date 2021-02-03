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
        kvstore_id = self.keyname()

        validation.allowed_key(data, ["id", "name", "provider_id",
                                      "backup_time", "backup_period",
                                      "zone", "region", "extend_info", self.keyname()])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "zone",
                                          "backup_time", "backup_period", kvstore_id]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string(kvstore_id, data.get(kvstore_id))
        validation.validate_string("backup_time", data["backup_time"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        kvstore_id = self.keyname()

        rid = data.pop("id", None) or get_uuid()
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        kvstore_id = data.pop(kvstore_id, None)
        backup_time = data.pop("backup_time", None)
        backup_period = data.pop("backup_period", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)

        _, result = self.resource.create(rid, provider_id,
                                         kvstore_id, backup_time, backup_period,
                                         zone, region, extend_info=data)

        return 1, {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}


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
        kvstore_id = self.keyname()

        validation.allowed_key(data, ["id", "name", "provider_id",
                                      "backup_time", "backup_period",
                                      "zone", "region", "extend_info", self.keyname()])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "zone",
                                          "backup_time", "backup_period", kvstore_id]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string(kvstore_id, data.get(kvstore_id))
        validation.validate_string("backup_time", data["backup_time"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        kvstore_id = self.keyname()

        rid = data.pop("id", None) or get_uuid()
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        kvstore_id = data.pop(kvstore_id, None)
        backup_time = data.pop("backup_time", None)
        backup_period = data.pop("backup_period", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)

        _, result = self.resource.create(rid, provider_id,
                                         kvstore_id, backup_time, backup_period,
                                         zone, region, extend_info=data)

        return {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}


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
