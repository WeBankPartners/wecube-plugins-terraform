# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from lib.uuid_util import get_uuid
from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from core import local_exceptions as exception_common
from apps.api.network.vpc import VpcApi


class VPCController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = VpcApi()

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
                                      "provider_id", "zone", "name", "cidr", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "region", "cidr", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "name", "cidr"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_string("cidr", data.get("cidr"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        cidr = data.pop("cidr", None)
        region = data.pop("region", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        _, result = self.resource.create(rid, name, cidr, provider_id, region=region, extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return 1, res


class VPCIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE')
    resource = VpcApi()

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


class VPCAddController(BaseController):
    allow_methods = ("POST",)
    resource = VpcApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "name", "cidr"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_string("cidr", data.get("cidr"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        cidr = data.pop("cidr", None)
        region = data.pop("region", None)
        provider_id = data.pop("provider_id", None)

        _, result = self.resource.create(rid, name, cidr, provider_id, region=region, extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return res


class VPCDeleteController(BaseController):
    name = "VPC"
    resource_describe = "VPC"
    allow_methods = ("POST",)
    resource = VpcApi()

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
