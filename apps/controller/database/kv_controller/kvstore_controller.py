# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.database.kvstore.kvstore import KvStoreApi


class KvStoreController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = KvStoreApi()

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
                                      'resource_id', "name", "enabled",
                                      "subnet_id", "instance_type", "version",
                                      "ipaddress", "port", 'engine'])

        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "subnet_id",
                                      "password", "port", "version", "instance_type",
                                      "vpc_id", "security_group_id", "engine",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "zone", "name",
                                          "version", "subnet_id", "instance_type"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("engine", data.get("engine"))
        validation.validate_string("subnet_id", data["subnet_id"])
        validation.validate_string("version", data["version"])
        validation.validate_string("password", data.get("password"))
        validation.validate_string("instance_type", data.get("instance_type"))
        validation.validate_list("security_group_id", data.get("security_group_id"))
        validation.validate_string("vpc_id", data.get("vpc_id"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        subnet_id = data.pop("subnet_id", None)
        port = data.pop("port", None)
        password = data.pop("password", None)
        version = data.pop("version", None)
        instance_type = data.pop("instance_type", None)
        provider_id = data.pop("provider_id", None)
        engine = data.pop("engine", None)
        vpc_id = data.pop("vpc_id", None)
        security_group_id = validation.validate_list("security_group_id", data.pop("security_group_id", None))
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)

        _, result = self.resource.create(rid, name=name, provider_id=provider_id,
                                         version=version, port=port,
                                         password=password, engine=engine,
                                         instance_type=instance_type,
                                         vpc_id=vpc_id,
                                         security_group_id=security_group_id,
                                         subnet_id=subnet_id, zone=zone,
                                         region=region, extend_info=data)

        _password = base64.b64decode(result.get("password")) if result.get("password") else None
        return 1, {"id": rid, "ipaddress": result.get("ipaddress"),
                   "port": result.get("port"),
                   "resource_id": str(result.get("resource_id"))[:64]}


class KvStoreIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = KvStoreApi()

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


class KvStoreAddController(BaseController):
    allow_methods = ("POST",)
    resource = KvStoreApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "zone", "name",
                                          "version", "subnet_id", "instance_type"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("engine", data.get("engine"))
        validation.validate_string("subnet_id", data["subnet_id"])
        validation.validate_string("version", data["version"])
        validation.validate_string("password", data.get("password"))
        validation.validate_string("instance_type", data.get("instance_type"))
        validation.validate_list("security_group_id", data.get("security_group_id"))
        validation.validate_string("vpc_id", data.get("vpc_id"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        subnet_id = data.pop("subnet_id", None)
        port = data.pop("port", None)
        password = data.pop("password", None)
        version = data.pop("version", None)
        instance_type = data.pop("instance_type", None)
        provider_id = data.pop("provider_id", None)
        engine = data.pop("engine", None)
        vpc_id = data.pop("vpc_id", None)
        security_group_id = validation.validate_list("security_group_id", data.pop("security_group_id", None))
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)

        _, result = self.resource.create(rid, name=name, provider_id=provider_id,
                                         version=version, port=port,
                                         password=password, engine=engine,
                                         instance_type=instance_type,
                                         vpc_id=vpc_id,
                                         security_group_id=security_group_id,
                                         subnet_id=subnet_id, zone=zone,
                                         region=region, extend_info=data)

        _password = base64.b64decode(result.get("password")) if result.get("password") else None
        return {"id": rid, "ipaddress": result.get("ipaddress"),
                "port": result.get("port"),
                "resource_id": str(result.get("resource_id"))[:64]}


class KvStoreDeleteController(BaseController):
    name = "KvStore"
    resource_describe = "KvStore"
    allow_methods = ("POST",)
    resource = KvStoreApi()

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
