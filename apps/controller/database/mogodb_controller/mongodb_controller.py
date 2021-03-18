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
from apps.api.database.nosql.mogodb import MongodbApi
from apps.controller.source_controller import BaseSourceController


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "extend_info", "subnet_id", "password",
                                      "disk_size", "version", "instance_type",
                                      "vpc_id", "security_group_id"])

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
                                               "password", "disk_type",
                                               "version", "instance_type",
                                               "vpc_id"],
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
        version = data.pop("version", None)
        disk_size = data.pop("disk_size", None)
        instance_type = data.pop("instance_type", None)
        vpc_id = data.pop("vpc_id", None)
        security_group_id = validation.validate_list("security_group_id", data.pop("security_group_id", None))

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        d = dict(version=version, port=port,
                 password=password,
                 instance_type=instance_type,
                 vpc_id=vpc_id,
                 security_group_id=security_group_id,
                 disk_size=disk_size,
                 subnet_id=subnet_id)

        create_data = {"name": name}
        create_data.update(d)
        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    create_data=create_data,
                                    extend_info=data)

        _password = cls.decrypt_key(result.get("password"))
        res = {"id": rid, "ipaddress": result.get("ipaddress"),
               "port": result.get("port"),
               "resource_id": str(result.get("resource_id"))[:64]}

        return res, result


class MongoDBController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = MongodbApi()

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
                                      "subnet_id", "instance_type", "version"])

        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return 1, res


class MongoDBIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = MongodbApi()

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


class MongoDBAddController(BaseController):
    allow_methods = ("POST",)
    resource = MongodbApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class MongoDBDeleteController(BaseController):
    name = "MongoDB"
    resource_describe = "MongoDB"
    allow_methods = ("POST",)
    resource = MongodbApi()

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


class MongoDBSourceController(BaseSourceController):
    name = "MongoDB"
    resource_describe = "MongoDB"
    allow_methods = ("POST",)
    resource = MongodbApi()

