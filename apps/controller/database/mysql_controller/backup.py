# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.database.mysql.backup import MysqlBackupApi


class MysqlBackupController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = MysqlBackupApi()

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

        validation.allowed_key(data, ["id", "provider", "region", "rds_id", "name", "enabled"])

        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "mysql_id",
                                      "backup_model", "backup_time",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "backup_time",
                                          "backup_model", "mysql_id"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("backup_model", data.get("backup_model"))
        validation.validate_string("backup_time", data.get("backup_time"))
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("mysql_id", data["mysql_id"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        backup_time = data.pop("backup_time", None)
        backup_model = data.pop("backup_model", None)
        mysql_id = data.pop("mysql_id", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        result = self.resource.create(rid, name, provider_id,
                                      mysql_id, backup_model, backup_time,
                                      zone, region, extend_info=data)

        return 1, result


class MysqlBackupIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = MysqlBackupApi()

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
        return self.resource.destory(rid)


class MysqlBackupAddController(BaseController):
    allow_methods = ("POST",)
    resource = MysqlBackupApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "backup_time",
                                          "backup_model", "mysql_id"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("backup_model", data.get("backup_model"))
        validation.validate_string("backup_time", data.get("backup_time"))
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("mysql_id", data["mysql_id"])
        validation.validate_string("provider_id", data.get("provider_id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        backup_time = data.pop("backup_time", None)
        backup_model = data.pop("backup_model", None)
        mysql_id = data.pop("mysql_id", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        result = self.resource.create(rid, name, provider_id,
                                      mysql_id, backup_model, backup_time,
                                      zone, region, extend_info=data)

        return {"result": result}


class MysqlBackupDeleteController(BaseController):
    name = "MysqlBackup"
    resource_describe = "MysqlBackup"
    allow_methods = ("POST",)
    resource = MysqlBackupApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["id"]
                                    )

        validation.validate_string("id", data.get("id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        result = self.resource.destory(rid)
        return {"result": result}
