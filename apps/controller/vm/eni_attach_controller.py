# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.vm.eni_attach import ENIAttachApi


class EniAttachController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = ENIAttachApi()

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
                                      "provider_id", "network_interface_id", "instance_id", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id",
                                      "network_interface_id", "instance_id",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "zone",
                                          "network_interface_id", "instance_id", "name"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("network_interface_id", data["network_interface_id"])
        validation.validate_int("instance_id", data.get("instance_id"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        network_interface_id = data.pop("network_interface_id", None)
        instance_id = data.pop("instance_id", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        _, result = self.resource.attach(rid, name=name, provider_id=provider_id,
                                      network_interface_id=network_interface_id,
                                      instance_id=instance_id,
                                      zone=zone, region=region, extend_info=data)

        res = {"id": rid, "resource_id": result.get("resource_id"),
               "instance_id": instance_id}
        return 1, res


class EniAttachIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE', 'PATCH')
    resource = ENIAttachApi()

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
        return self.resource.detach(rid)


class EniAttachAddController(BaseController):
    allow_methods = ("POST",)
    resource = ENIAttachApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "zone",
                                          "network_interface_id", "instance_id", "name"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("network_interface_id", data["network_interface_id"])
        validation.validate_int("instance_id", data.get("instance_id"))
        validation.validate_string("provider_id", data.get("provider_id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        network_interface_id = data.pop("network_interface_id", None)
        instance_id = data.pop("instance_id", None)
        provider_id = data.pop("provider_id", None)

        _, result = self.resource.attach(rid, name=name, provider_id=provider_id,
                                      network_interface_id=network_interface_id,
                                      instance_id=instance_id,
                                      zone=zone, region=region, extend_info=data)

        res = {"id": rid, "resource_id": result.get("resource_id"),
               "instance_id": instance_id}
        return res


class EniDetachController(BaseController):
    name = "EniDetach"
    resource_describe = "EniDetach"
    allow_methods = ("POST",)
    resource = ENIAttachApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["id"]
                                    )

        validation.validate_string("id", data.get("id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        result = self.resource.detach(rid)
        return {"result": result}
