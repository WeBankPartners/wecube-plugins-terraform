# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.network.route_entry import RouteEntryApi


class RouteEntryController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = RouteEntryApi()

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

        validation.allowed_key(data, ["id", "provider", "region", 'resource_id', 'destination',
                                      "provider_id", "name", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "vpc_id", "destination",
                                      "route_table_id", "next_type", "next_hub",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "vpc_id", "name",
                                          "route_table_id", "next_type", "next_hub", "destination"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("vpc_id", data["vpc_id"])
        validation.validate_string("route_table_id", data.get("route_table_id"))
        validation.validate_string("next_type", data.get("next_type"))
        validation.validate_string("next_hub", data.get("next_hub"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_string("destination", data.get("destination"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        vpc_id = data.pop("vpc_id", None)
        provider_id = data.pop("provider_id", None)
        route_table = data.pop("route_table_id", None)
        next_type = data.pop("next_type", None)
        next_hub = data.pop("next_hub", None)
        destination = data.pop("destination", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        _, result = self.resource.create(rid, name, provider_id, zone, region,
                                      vpc_id, route_table, next_type, next_hub,
                                      destination=destination, extend_info=data)

        res = {"id": rid, "resource_id": result.get("resource_id")}
        return 1, res


class RouteEntryIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE', 'PATCH')
    resource = RouteEntryApi()

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


class RouteEntryAddController(BaseController):
    allow_methods = ("POST",)
    resource = RouteEntryApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "vpc_id", "name",
                                          "route_table_id", "next_type", "next_hub", "destination"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("vpc_id", data["vpc_id"])
        validation.validate_string("route_table_id", data.get("route_table_id"))
        validation.validate_string("next_type", data.get("next_type"))
        validation.validate_string("next_hub", data.get("next_hub"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_string("destination", data.get("destination"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        vpc_id = data.pop("vpc_id", None)
        provider_id = data.pop("provider_id", None)
        route_table = data.pop("route_table_id", None)
        next_type = data.pop("next_type", None)
        next_hub = data.pop("next_hub", None)
        destination = data.pop("destination", None)

        _, result = self.resource.create(rid, name, provider_id, zone, region,
                                      vpc_id, route_table, next_type, next_hub,
                                      destination=destination, extend_info=data)

        res = {"id": rid, "resource_id": result.get("resource_id")}
        return res


class RouteEntryDeleteController(BaseController):
    name = "RouteEntry"
    resource_describe = "RouteEntry"
    allow_methods = ("POST",)
    resource = RouteEntryApi()

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
