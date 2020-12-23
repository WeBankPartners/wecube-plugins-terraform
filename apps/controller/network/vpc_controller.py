# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.network.vpc import VpcApi
from apps.api.network.vpc import VpcObject
from core import local_exceptions as exception_common
from core import validation
from core.controller import BaseController
from core.controller import BackendController
from core.controller import BackendIdController


class VPCBaseController(BaseController):
    pass


class VPCController(BackendController):
    resource = VpcObject()

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

        validation.allowed_key(data, ["id", "provider", "region",
                                      "zone", "name", "cider", "enabled"])
        return self.resource.list(filters=data, page=page,
                                  pagesize=pagesize, orderby=orderby)


class VPCIdController(BackendController):
    resource = VpcObject()

    def show(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        return self.resource.show(rid)


class VPCAddController(VPCBaseController):
    name = "VPC"
    resource_describe = "VPC"
    allow_methods = ("POST",)
    resource = VpcObject()

    def not_null_keys(self):
        return ["provider", "region", "name", "cider"]

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider", "region",
                                      "zone", "cider", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=self.not_null_keys()
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("provider", data.get("provider"))
        validation.validate_string("region", data.get("region"))
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("cider", data.get("cider"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def response_templete(self, data):
        # todo detail VPC create
        return {}

    def main_response(self, request, data, **kwargs):
        result = VpcApi().create(data)
        return {"result": result}


class VPCUpdateController(VPCBaseController):
    name = "VPC"
    resource_describe = "VPC"
    allow_methods = ("POST",)
    resource = VpcObject()

    def before_handler(self, request, data, **kwargs):
        pass

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        result = self.resource.update(rid, data)
        if not result:
            raise exception_common.ResourceNotFoundError()

        return result


class VPCDeleteController(VPCBaseController):
    name = "VPC"
    resource_describe = "VPC"
    allow_methods = ("POST",)
    resource = VpcObject()

    def before_handler(self, request, data, **kwargs):
        pass

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        result = self.resource.delete(rid)
        if not result:
            raise exception_common.ResourceNotFoundError()

        return result
