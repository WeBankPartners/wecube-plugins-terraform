# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.network.route_table import RouteTableApi


class RouteTableController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = RouteTableApi()

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
                                      "provider_id", "name", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "vpc_id",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "vpc_id", "name"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("vpc_id", data["vpc_id"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        vpc_id = data.pop("vpc_id", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        result = self.resource.create(rid, name, provider_id, vpc_id,
                                      zone, region, extend_info=data)
        return 1, result


class RouteTableIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE', 'PATCH')
    resource = RouteTableApi()

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

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        name = data.pop("name", None)
        return self.resource.update(rid, name, extend_info={})


class RouteTableAddController(BaseController):
    allow_methods = ("POST",)
    resource = RouteTableApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "vpc_id"
                                                                   "zone", "name", "cider"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("vpc_id", data["vpc_id"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_string("cider", data.get("cider"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        cider = data.pop("cider", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        vpc_id = data.pop("vpc_id", None)
        provider_id = data.pop("provider_id", None)

        result = self.resource.create(rid, name, cider, provider_id,
                                      vpc_id, region, zone,
                                      extend_info=data)

        return {"result": result}


class RouteTableDeleteController(BaseController):
    name = "RouteTable"
    resource_describe = "RouteTable"
    allow_methods = ("POST",)
    resource = RouteTableApi()

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
