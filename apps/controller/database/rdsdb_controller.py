# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.database.rds import RdsDBApi


class InstanceController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = RdsDBApi()

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
                                      "provider_id", "name", "enabled", "subnet_id",
                                      "engine", "version", "instance_type",
                                      "port", "ipaddress", "disk_type", "disk_size"])

        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "subnet_id",
                                      "instance_type",
                                      "disk_type", "disk_size",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "zone", "name",
                                          "hostname", "subnet_id", "image", "instance_type"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("subnet_id", data["subnet_id"])
        validation.validate_string("hostname", data.get("hostname"))
        validation.validate_string("image", data.get("image"))
        validation.validate_string("instance_type", data.get("instance_type"))
        validation.validate_string("disk_type", data.get("disk_type"))
        validation.validate_int("disk_size", data.get("disk_size"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        subnet_id = data.pop("subnet_id", None)
        hostname = data.pop("hostname", None)
        image = data.pop("image", None)
        disk_type = data.pop("disk_type")
        disk_size = data.pop("disk_size", 40)
        instance_type = data.pop("instance_type")
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)

        rid, name, provider_id, version,
        instance_type, subnet_id, port, password,
        user, disk_type, disk_size,
        zone, region, extend_info

        result = self.resource.create(rid, name=name, provider_id=provider_id,
                                      version=version, image=image,
                                      instance_type=instance_type,
                                      disk_type=disk_type, disk_size=disk_size,
                                      subnet_id=subnet_id, zone=zone,
                                      region=region, extend_info=data)
        return 1, result


class InstanceIdController(BackendController):
    allow_methods = ('GET', 'DELETE', 'PATCH')
    resource = InstanceApi()

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

    def before_handler(self, request, data, **kwargs):
        if not data:
            raise ValueError("没有需要更新的配置")

        validation.allowed_key(data, ["name", "instance_type", "image", "extend_info"])
        validation.validate_string("name", data.get("name"))
        validation.validate_string("instance_type", data.get("instance_type"))
        validation.validate_string("image", data.get("image"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        name = data.pop("name", None)
        instance_type = data.pop("instance_tpe")
        image = data.pop("image")
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        return self.resource.update(rid, name, instance_type, image, extend_info)


class InstanceActionController(BackendController):
    allow_methods = ('PATCH',)
    resource = InstanceApi()

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["action"])
        validation.not_allowed_null(data=data,
                                    keys=["action"]
                                    )

        validation.validate_string("action", data["action"])

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        action = data.get("action", None)
        if action.lower() == "start":
            return self.resource.start(rid)
        elif action.lower == "stop":
            return self.resource.stop(rid)
        else:
            raise local_exceptions.ValueValidateError("action", "VM 开关机操作，请使用合法值 start/stop")


class InstanceAddController(BaseController):
    allow_methods = ("POST",)
    resource = InstanceApi()

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "subnet_id",
                                      "hostname", "image", "instance_type",
                                      "disk_type", "disk_size",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "zone", "name",
                                          "hostname", "subnet_id", "image", "instance_type"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("subnet_id", data["subnet_id"])
        validation.validate_string("hostname", data.get("hostname"))
        validation.validate_string("image", data.get("image"))
        validation.validate_string("instance_type", data.get("instance_type"))
        validation.validate_string("disk_type", data.get("disk_type"))
        validation.validate_int("disk_size", data.get("disk_size"))
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
        hostname = data.pop("hostname", None)
        image = data.pop("image", None)
        disk_type = data.pop("disk_type")
        disk_size = data.pop("disk_size", 40)
        instance_type = data.pop("instance_type")
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        result = self.resource.create(rid, name=name, provider_id=provider_id,
                                      hostname=hostname, image=image,
                                      instance_type=instance_type,
                                      disk_type=disk_type, disk_size=disk_size,
                                      subnet_id=subnet_id, zone=zone,
                                      region=region, extend_info=data)

        return {"result": result}


class InstanceDeleteController(BaseController):
    name = "Instance"
    resource_describe = "Instance"
    allow_methods = ("POST",)
    resource = InstanceApi()

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
