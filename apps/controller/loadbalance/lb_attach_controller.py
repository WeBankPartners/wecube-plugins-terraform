# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.loadbalance.lb_attach import LBAttachApi
from apps.api.loadbalance.lb_attach import LBAttachBackendApi
from apps.controller.source_controller import BaseSourceController


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "extend_info", "lb_id",
                                      "listener_id", "backend_servers"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "lb_id", "backend_servers"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "region", "zone",
                                               "provider", "secret", "lb_id",
                                               "listener_id"],
                                      lists=["backend_servers"],
                                      dicts=["extend_info"])

    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)
        name = data.pop("name", None)
        lb_id = data.pop("lb_id", None)
        listener_id = data.pop("listener_id", None)
        backend_servers = validation.validate_list("backend_servers", data.pop("backend_servers", None))

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

        if not backend_servers:
            raise local_exceptions.ValueValidateError("backend_servers", "backend servers not permit null")

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        asset_id = data.pop("asset_id", None)
        resource_id = data.pop("resource_id", None)

        create_data = {"name": name, "lb_id": lb_id,
                       "listener_id": listener_id,
                       "backend_servers": backend_servers}
        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    asset_id=asset_id,
                                    resource_id=resource_id,
                                    create_data=create_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return res, result


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
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return 1, res


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
        return self.resource.destroy(rid)


class LBDetachController(BackendIdController):
    allow_methods = ('DELETE',)
    resource = LBAttachApi()

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        instance_id = kwargs.pop("instance", None)
        return self.resource.remove_instance(rid, instance_id)


class LBAttachAddController(BaseController):
    allow_methods = ("POST",)
    resource = LBAttachBackendApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class LBAttachDeleteController(BaseController):
    name = "LBAttach"
    resource_describe = "LBAttach"
    allow_methods = ("POST",)
    resource = LBAttachBackendApi()

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


class LBAttachSourceController(BaseSourceController):
    name = "VPC"
    resource_describe = "VPC"
    allow_methods = ("POST",)
    resource = LBAttachBackendApi()

