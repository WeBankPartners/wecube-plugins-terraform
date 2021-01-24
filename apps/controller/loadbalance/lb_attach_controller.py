# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.loadbalance.lb_attach import LBAttachApi


class LBAttachController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = LBAttachApi()

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

        # todo 使用instance id 进行搜索/ instance
        validation.allowed_key(data, ["id", "provider", "region", 'resource_id',
                                      "provider_id", "listener_id", "lb_id"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "lb_id",
                                      "listener_id", "backend_servers",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "lb_id", "backend_servers"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("lb_id", data["lb_id"])
        validation.validate_string("listener_id", data.get("listener_id"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_list("backend_servers", data.get("backend_servers"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        lb_id = data.pop("lb_id", None)
        listener_id = data.pop("listener_id", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        backend_servers = validation.validate_list("backend_servers", data.pop("backend_servers", None))

        if not backend_servers:
            raise local_exceptions.ValueValidateError("backend_servers", "backend servers not permit null")

        data.update(extend_info)
        _, result = self.resource.create(rid, name, provider_id,
                                         lb_id, listener_id, backend_servers,
                                         zone, region, extend_info=data)

        return 1, {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}


class LBAttachIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = LBAttachApi()

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


class LBDetachController(BackendIdController):
    allow_methods = ('DELETE',)
    resource = LBAttachApi()

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        instance_id = kwargs.pop("instance", None)
        return self.resource.remove_instance(rid, instance_id)


class LBAttachAddController(BaseController):
    allow_methods = ("POST",)
    resource = LBAttachApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "lb_id", "backend_servers"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("lb_id", data["lb_id"])
        validation.validate_string("listener_id", data.get("listener_id"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_list("backend_servers", data.get("backend_servers"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        lb_id = data.pop("lb_id", None)
        listener_id = data.pop("listener_id", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        backend_servers = validation.validate_list("backend_servers", data.pop("backend_servers", None))

        if not backend_servers:
            raise local_exceptions.ValueValidateError("backend_servers", "backend servers not permit null")

        data.update(extend_info)
        if not backend_servers:
            instance_id = data.pop("instance_id", None)
            backend_servers = {"instance_id": instance_id}
            if not instance_id:
                raise local_exceptions.ValueValidateError("backend_servers", "backend servers not permit null")

            weight = data.pop("weight", None)
            port = data.pop("port", None)
            if weight is not None:
                backend_servers["weight"] = weight
            if port is not None:
                backend_servers["port"] = port

        data.update(extend_info)
        _, result = self.resource.create(rid, name, provider_id,
                                         lb_id, listener_id, backend_servers,
                                         zone, region, extend_info=data)

        return {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}


class LBAttachDeleteController(BaseController):
    name = "LBAttach"
    resource_describe = "LBAttach"
    allow_methods = ("POST",)
    resource = LBAttachApi()

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


class LBDetachBackendController(BaseController):
    name = "LBDetach"
    resource_describe = "LBDetach"
    allow_methods = ("POST",)
    resource = LBAttachApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["id", "instance_id"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("instance_id", data.get("instance_id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        instance_id = data.pop("instance_id", None)
        result = self.resource.remove_instance(rid, instance_id)
        return {"result": result}
