# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from lib.logs import logger
from core.response_hooks import format_string
from apps.controller.configer.model_args import source_columns_outputs
from apps.api.configer.region import ZoneApi
from apps.api.network.route_entry import RouteEntryApi
from apps.api.network.route_entry import RouteEntryBackendApi
from apps.controller.source_controller import BaseSourceController


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "vpc_id", "destination",
                                      "route_table_id", "next_type",
                                      "next_hub", "extend_info"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "name", "vpc_id",
                                          "route_table_id", "next_type",
                                          "next_hub", "destination"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "region", "zone",
                                               "provider", "secret", "vpc_id", "destination",
                                               "route_table_id", "next_type", "next_hub"],
                                      dicts=["extend_info"])

    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)
        name = data.pop("name", None)
        vpc_id = data.pop("vpc_id", None)
        route_table = data.pop("route_table_id", None)
        next_type = data.pop("next_type", None)
        next_hub = data.pop("next_hub", None)
        destination = data.pop("destination", None)

        asset_id = data.pop("asset_id", None)
        resource_id = data.pop("resource_id", None)

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        create_data = {"name": name, "vpc_id": vpc_id, "destination": destination,
                       "route_table_id": route_table, "next_type": next_type,
                       "next_hub": next_hub}

        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    asset_id=asset_id,
                                    resource_id=resource_id,
                                    create_data=create_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return res, result


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
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
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
        return self.resource.destroy(rid)


class RouteEntryAddController(BaseController):
    allow_methods = ("POST",)
    resource = RouteEntryBackendApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class RouteEntryDeleteController(BaseController):
    name = "RouteEntry"
    resource_describe = "RouteEntry"
    allow_methods = ("POST",)
    resource = RouteEntryBackendApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["id"]
                                    )

        validation.validate_string("id", data.get("id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        result = self.resource.destroy(rid)
        return {"result": result}


class RTRuleSourceController(BaseSourceController):
    name = "RouteEntry"
    resource_describe = "RouteEntry"
    allow_methods = ("POST",)
    resource = RouteEntryBackendApi()

    def one_query(self, rid, provider, region, zone, secret,
                  resource_id, ignore_ids, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param zone:
        :param secret:
        :param resource_id:
        :param ignore_ids:
        :param kwargs:
        :return:
        '''

        result = self.fetch_source(rid=rid, provider=provider, region=region, zone=zone,
                                   secret=secret, resource_id=resource_id,
                                   **kwargs)
        result_data = []

        register_zones = ZoneApi().region_zones(region, provider)

        for x_result in result:
            x_res = source_columns_outputs(self.resource.resource_name)
            x_res.update(x_result)

            route_table_id = kwargs.get("route_table_id")
            if not x_res.get("route_table_id") and route_table_id:
                x_res["route_table_id"] = route_table_id

            res = {"region": region, "secret": secret, "provider": provider}

            if x_res.get("resource_id") in ignore_ids:
                continue

            if x_res.get("zone") and (x_res.get("zone") not in register_zones):
                logger.info("resource: %s ,zone: %s searched not in register zone, skip it" % (
                    x_res.get("resource_id"), x_res.get("zone")))
                if x_res.get("x_ora_zone") and (x_res.get("x_ora_zone") not in register_zones):
                    continue

            x_res.pop("x_ora_zone", None)

            for x, value in x_res.items():
                if isinstance(value, dict):
                    res[x] = format_string(value)
                else:
                    if value is None:
                        res[x] = ''
                    else:
                        res[x] = str(value)

            result_data.append(res)

        return result_data
