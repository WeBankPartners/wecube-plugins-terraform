# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.loadbalance.listener import LBListenerApi


class LBListenerController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = LBListenerApi()

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
                                      "provider_id", "name", "lb_id", "port", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "lb_id",
                                      "port", "protocol", "backend_port",
                                      "health_check", "health_check_uri",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "lb_id", "port"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("lb_id", data["lb_id"])
        validation.validate_port(data.get("port"))
        validation.validate_string("protocol", data.get("protocol"))
        validation.validate_port(data.get("backend_port"), permit_null=True)
        validation.validate_string("health_check", data.get("health_check"))
        validation.validate_string("health_check_uri", data.get("health_check_uri"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        lb_id = data.pop("lb_id", None)
        port = int(data.pop("port"))
        protocol = data.pop("protocol", None)
        backend_port = validation.validate_port(data.get("backend_port"), permit_null=True)
        health_check = data.pop("health_check", None)
        health_check_uri = data.pop("health_check_uri", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        result = self.resource.create(rid, name, provider_id,
                                      lb_id, port, protocol, backend_port,
                                      health_check, health_check_uri,
                                      zone, region, extend_info=data)
        return 1, result


class LBListenerIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE', 'PATCH')
    resource = LBListenerApi()

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


class LBListenerAddController(BaseController):
    allow_methods = ("POST",)
    resource = LBListenerApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "lb_id", "port"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("lb_id", data["lb_id"])
        validation.validate_port(data.get("port"))
        validation.validate_string("protocol", data.get("protocol"))
        validation.validate_port(data.get("backend_port"), permit_null=True)
        validation.validate_string("health_check", data.get("health_check"))
        validation.validate_string("health_check_uri", data.get("health_check_uri"))
        validation.validate_string("provider_id", data.get("provider_id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        lb_id = data.pop("lb_id", None)
        port = int(data.pop("port"))
        protocol = data.pop("protocol", None)
        backend_port = validation.validate_port(data.get("backend_port"), permit_null=True)
        health_check = data.pop("health_check", None)
        health_check_uri = data.pop("health_check_uri", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        result = self.resource.create(rid, name, provider_id,
                                      lb_id, port, protocol, backend_port,
                                      health_check, health_check_uri,
                                      zone, region, extend_info=data)

        return {"result": result}


class LBListenerDeleteController(BaseController):
    name = "LBListener"
    resource_describe = "LBListener"
    allow_methods = ("POST",)
    resource = LBListenerApi()

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
