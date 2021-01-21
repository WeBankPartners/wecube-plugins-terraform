# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BaseController
from core.controller import BackendIdController
from lib.uuid_util import get_uuid
from apps.api.network.nat_gateway import NatGatewayApi


class NatGatewayController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = NatGatewayApi()

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
                                      "provider_id", "name", "vpc", "subnet",
                                      "ipaddress", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "vpc_id",
                                      "subnet_id", "eip",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "name", "vpc_id"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("vpc_id", data["vpc_id"])
        validation.validate_string("subnet_id", data.get("subnet_id"))
        validation.validate_string("eip", data.get("eip"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        vpc_id = data.pop("vpc_id", None)
        subnet_id = data.pop("subnet_id", None)
        eip = data.pop("eip", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        rid, result = self.resource.create(rid, name, provider_id,
                                           vpc_id, subnet_id, eip,
                                           zone, region, extend_info=data)
        res = {"id": rid, "ipaddress": result.get("ipaddress"),
               "resource_id": str(result.get("resource_id"))[:64]}
        return 1, res


class NatGatewayIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE')
    resource = NatGatewayApi()

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

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["name"])
        validation.not_allowed_null(data=data,
                                    keys=["name"]
                                    )

        validation.validate_string("name", data["name"])


class NatGatewayAddController(BaseController):
    allow_methods = ("POST",)
    resource = NatGatewayApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "name", "vpc_id"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("vpc_id", data["vpc_id"])
        validation.validate_string("subnet_id", data.get("subnet_id"))
        validation.validate_string("eip", data.get("eip"))
        validation.validate_string("provider_id", data.get("provider_id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        vpc_id = data.pop("vpc_id", None)
        subnet_id = data.pop("subnet_id", None)
        eip = data.pop("eip", None)
        provider_id = data.pop("provider_id", None)

        _, result = self.resource.create(rid, name, provider_id,
                                           vpc_id, subnet_id, eip,
                                           zone, region, extend_info=data)

        return {"id": rid, "ipaddress": result.get("ipaddress"),
                "resource_id": str(result.get("resource_id"))[:64]}


class NatGatewayDeleteController(BaseController):
    name = "NatGateway"
    resource_describe = "NatGateway"
    allow_methods = ("POST",)
    resource = NatGatewayApi()

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
