# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.uuid_util import get_uuid
from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from apps.api.configer.region import RegionObject
from apps.api.configer.region import ZoneObject
from apps.api.configer.provider import ProviderObject


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "name", "region_id",
                                      "region", "asset_id", "extend_info"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["asset_id", "provider", "region_id"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "provider", "asset_id", "region_id"],
                                      dicts=["extend_info"])

    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        asset_id = data.pop("asset_id", None)
        provider = data.pop("provider", None)
        region = data.pop("region_id", None) or data.pop("region", None)

        ProviderObject().provider_name_object(provider)
        RegionObject().region_object(region)

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        create_data = {"id": rid,
                       "name": name,
                       "region": region,
                       "asset_id": asset_id,
                       "provider": provider,
                       "extend_info": json.dumps(extend_info),
                       }

        return resource.create(create_data)


class ZoneController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = ZoneObject()

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

        validation.allowed_key(data, ["id", "provider", "name", 'asset_id', "region"])
        count, res = self.resource.list(filters=data, page=page,
                                   pagesize=pagesize, orderby=orderby)
        result = []
        for x_res in res:
            x_res["region_id"] = x_res["region"]
            result.append(x_res)

        return count, res

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        return ResBase.create(resource=self.resource, data=data)


class ZoneIdController(BackendIdController):
    allow_methods = ('GET', 'PATCH', 'DELETE')
    resource = ZoneObject()

    def show(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        return self.resource.show(rid)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["provider", "name", "asset_id", "extend_info", "region", "region_id"])
        ResBase.validate_keys(data)

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)

        if "provider" in data.keys():
            ProviderObject().provider_name_object(data.get("provider"))

        if "region" in data.keys():
            RegionObject().region_object(data.get("region"))

        if data.get("extend_info") is not None:
            extend_info = validation.validate_dict("extend_info", data.get("extend_info"))
            data["extend_info"] = json.dumps(extend_info)

        return self.resource.update(rid, data)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.delete(rid)


class ZoneAddController(BaseController):
    allow_methods = ("POST",)
    resource = ZoneObject()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.get("id", None)
        data.pop("secret", None)
        if rid:
            if self.resource.show(rid):
                if data.get("extend_info") is not None:
                    extend_info = validation.validate_dict("extend_info", data.get("extend_info"))
                    data["extend_info"] = json.dumps(extend_info)

                if "provider" in data.keys():
                    ProviderObject().provider_name_object(data.get("provider"))

                if "region" in data.keys():
                    RegionObject().region_object(data.get("region"))

                self.resource.update(rid, data)
                return {"result": rid}

        count, res = ResBase.create(resource=self.resource, data=data)
        return {"result": res}


class ZoneDeleteController(BaseController):
    name = "Zone"
    resource_describe = "Zone"
    allow_methods = ("POST",)
    resource = ZoneObject()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["id"]
                                    )

        validation.validate_string("id", data.get("id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        result = self.resource.delete(rid)
        return {"result": result}


class ZoneSourceController(BaseController):
    name = "Zone"
    resource_describe = "Zone"
    allow_methods = ("POST",)
    resource = ZoneObject()

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

        # validation.allowed_key(data, ["id", "provider", "name", 'asset_id', "region"])
        return self.resource.list(filters=data, page=page,
                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        pass

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        query_data = {}
        for key in ["id", "provider", "name", 'asset_id', "region_id"]:
            if data.get(key):
                if key == "region_id":
                    query_data["region"] = data.get(key)
                else:
                    query_data[key] = data.get(key)

        orderby = data.get("orderby")
        page = data.get("page", 0)
        pagesize = data.get("pagesize", 1000)

        count, result = self.list(request, data=query_data,
                                  orderby=orderby, page=page,
                                  pagesize=pagesize, **kwargs)
        res = []
        for x in result:
            x["region_id"] = x["region"]
            res.append(x)

        return res
