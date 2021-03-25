# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.network.security_group_rule import SecGroupRuleApi
from apps.controller.source_controller import BaseSourceController


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "extend_info", "security_group_id",
                                      "type", "cidr_ip", "ip_protocol",
                                      "ports", "policy", "description"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "security_group_id",
                                          "type", "cidr_ip", "ip_protocol", "ports", "policy"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "region", "zone",
                                               "provider", "secret",
                                               "type", "cidr_ip", "ip_protocol",
                                               "ports", "policy", "security_group_id"],
                                      dicts=["extend_info"])

    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        provider = data.pop("provider", None)

        zone = data.pop("zone", None)
        security_group_id = data.pop("security_group_id", None)
        type = data.pop("type", None)
        cidr_ip = data.pop("cidr_ip", None)
        ip_protocol = data.pop("ip_protocol", None)
        ports = data.pop("ports", None)
        policy = data.pop("policy", None)
        description = data.pop("description")
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)

        create_data = {"name": name, "security_group_id": security_group_id,
                       "type": type, "cidr_ip": cidr_ip, "ip_protocol": ip_protocol,
                       "ports": ports, "policy": policy, "description": description}
        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    create_data=create_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return res, result


class SecGroupRuleController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = SecGroupRuleApi()

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
                                      "provider_id", "security_group_id", "name"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return 1, res


class SecGroupRuleIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE')
    resource = SecGroupRuleApi()

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


class SecGroupRuleAddController(BaseController):
    allow_methods = ("POST",)
    resource = SecGroupRuleApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class SecGroupRuleDeleteController(BaseController):
    name = "SecGroupRule"
    resource_describe = "SecGroupRule"
    allow_methods = ("POST",)
    resource = SecGroupRuleApi()

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


class SGRuleSourceController(BaseSourceController):
    name = "SecGroupRule"
    resource_describe = "SecGroupRule"
    allow_methods = ("POST",)
    resource = SecGroupRuleApi()

