# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from lib.encrypt_helper import decrypt_str
from apps.api.database.mysql.instance import MysqlApi
from apps.api.database.mysql.instance import MysqlBackendApi
from apps.controller.source_controller import BaseSourceController


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "extend_info", "subnet_id",
                                      "user", "password", "port", "disk_type",
                                      "disk_size", "version", "instance_type",
                                      "vpc_id", "security_group_id",
                                      "second_slave_zone", "first_slave_zone"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "name",
                                          "version", "subnet_id", "instance_type"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "region", "zone",
                                               "provider", "secret", "subnet_id",
                                               "user", "password",  "disk_type",
                                               "version", "instance_type",
                                               "vpc_id", "second_slave_zone",
                                               "first_slave_zone"],
                                      ports=["port"],
                                      ints=["disk_size"],
                                      lists=["security_group_id"],
                                      dicts=["extend_info"])

    @classmethod
    def decrypt_key(cls, str):
        if str:
            if str.startswith("{cipher_a}"):
                str = str[len("{cipher_a}"):]
                str = decrypt_str(str)

        return str

    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)
        name = data.pop("name", None)
        subnet_id = data.pop("subnet_id", None)
        port = data.pop("port", None)
        password = data.pop("password", None)
        user = data.pop("user", None)
        version = data.pop("version", None)
        disk_type = data.pop("disk_type", None)
        disk_size = data.pop("disk_size", None)
        instance_type = data.pop("instance_type", None)
        first_slave_zone = data.pop("first_slave_zone", None)
        second_slave_zone = data.pop("second_slave_zone", None)
        vpc_id = data.pop("vpc_id", None)
        security_group_id = validation.validate_list("security_group_id", data.pop("security_group_id", None))

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        asset_id = data.pop("asset_id", None)
        resource_id = data.pop("resource_id", None)

        d = dict(version=version, port=port,
                 password=password, user=user,
                 instance_type=instance_type,
                 vpc_id=vpc_id, first_slave_zone=first_slave_zone,
                 second_slave_zone=second_slave_zone,
                 security_group_id=security_group_id,
                 disk_type=disk_type, disk_size=disk_size,
                 subnet_id=subnet_id)

        create_data = {"name": name}
        create_data.update(d)
        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    asset_id=asset_id,
                                    resource_id=resource_id,
                                    create_data=create_data,
                                    extend_info=data)

        _password = cls.decrypt_key(result.get("password"))
        res = {"id": rid, "ipaddress": result.get("ipaddress"),
               "port": result.get("port"), "user": result.get("user"),
               "password": _password,
               "resource_id": str(result.get("resource_id"))[:64]}

        return res, result


class MysqlController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = MysqlApi()

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

        validation.allowed_key(data, ["id", "provider", "region", 'resource_id',
                                      "provider_id", "name", "enabled",
                                      "subnet_id", "instance_type", "version",
                                      "ipaddress", "port",
                                      "disk_type", "disk_size"])

        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return 1, res


class MysqlIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = MysqlApi()

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
        return self.resource.destroy(rid)


class MysqlAddController(BaseController):
    allow_methods = ("POST",)
    resource = MysqlBackendApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class MysqlDeleteController(BaseController):
    name = "Mysql"
    resource_describe = "Mysql"
    allow_methods = ("POST",)
    resource = MysqlBackendApi()

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
        result = self.resource.destroy(rid)
        return {"result": result}


class MysqlSourceController(BaseSourceController):
    name = "Mysql"
    resource_describe = "Mysql"
    allow_methods = ("POST",)
    resource = MysqlBackendApi()

