# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.network.ccn_attach import CCNAttachApi


class CCNAttachController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = CCNAttachApi()

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

        validation.allowed_key(data, ["id", "provider", "region", 'resource_id', "ccn_id",
                                      "instance_type", "instance_region", "instance_id",
                                      "provider_id", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "ccn_id",
                                      "instance_id", "instance_type", "instance_region",
                                      "zone", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "ccn_id", "instance_id"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data.get("name"))
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("ccn_id", data.get("ccn_id"))
        validation.validate_string("instance_id", data["instance_id"])
        validation.validate_string("instance_type", data.get("instance_type"))
        validation.validate_string("instance_region", data.get("instance_region"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        vpc_id = data.pop("instance_id", None)
        instance_region = data.pop("instance_region", None)
        instance_type = data.pop("instance_type", None)
        provider_id = data.pop("provider_id", None)
        ccn_id = data.pop("ccn_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        _, result = self.resource.create(rid, name, provider_id,
                                         ccn_id, instance_id=vpc_id,
                                         instance_type=instance_type,
                                         instance_region=instance_region,
                                         region=region, zone=zone, extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return 1, res


class CCNAttachIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE')
    resource = CCNAttachApi()

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


class CCNAttachAddController(BaseController):
    allow_methods = ("POST",)
    resource = CCNAttachApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "ccn_id", "instance_id"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data.get("name"))
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("ccn_id", data.get("ccn_id"))
        validation.validate_string("instance_id", data["instance_id"])
        validation.validate_string("instance_type", data.get("instance_type"))
        validation.validate_string("instance_region", data.get("instance_region"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        vpc_id = data.pop("instance_id", None)
        instance_region = data.pop("instance_region", None)
        instance_type = data.pop("instance_type", None)
        provider_id = data.pop("provider_id", None)
        ccn_id = data.pop("ccn_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        _, result = self.resource.create(rid, name, provider_id,
                                         ccn_id, instance_id=vpc_id,
                                         instance_type=instance_type,
                                         instance_region=instance_region,
                                         region=region, zone=zone, extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return res


class CCNAttachDeleteController(BaseController):
    name = "CCNAttach"
    resource_describe = "CCNAttach"
    allow_methods = ("POST",)
    resource = CCNAttachApi()

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
