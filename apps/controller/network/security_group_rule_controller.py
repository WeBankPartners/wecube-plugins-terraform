# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.network.security_group_rule import SecGroupRuleApi


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
        '''
        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        validation.allowed_key(data, ["id", "name", "provider_id", "security_group_id",
                                      "zone", "region", "type", "cidr_ip", "ip_protocol",
                                      "ports", "policy", "description", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "security_group_id",
                                          "type", "cidr_ip", "ip_protocol", "ports", "policy"
                                          ]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("type", data["type"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_string("cidr_ip", data.get("cidr_ip"))
        validation.validate_string("ip_protocol", data.get("ip_protocol"))
        validation.validate_string("ports", data.get("ports"))
        validation.validate_string("policy", data.get("policy"))
        validation.validate_string("security_group_id", data.get("security_group_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        security_group_id = data.pop("security_group_id", None)
        type = data.pop("type", None)
        cidr_ip = data.pop("cidr_ip", None)
        ip_protocol = data.pop("ip_protocol", None)
        ports = data.pop("ports", None)
        policy = data.pop("policy", None)
        description = data.pop("description")
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)
        _, result = self.resource.create(rid, name, provider_id,
                                      security_group_id, type,
                                      cidr_ip, ip_protocol,
                                      ports, policy, description,
                                      zone, region, extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
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
        '''
        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        validation.not_allowed_null(data=data,
                                    keys=["region", "provider_id", "security_group_id",
                                          "type", "cidr_ip", "ip_protocol", "ports", "policy"
                                          ]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data["region"])
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("type", data["type"])
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_string("cidr_ip", data.get("cidr_ip"))
        validation.validate_string("ip_protocol", data.get("ip_protocol"))
        validation.validate_string("ports", data.get("ports"))
        validation.validate_string("policy", data.get("policy"))
        validation.validate_string("security_group_id", data.get("security_group_id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        zone = data.pop("zone", None)
        region = data.pop("region", None)
        security_group_id = data.pop("security_group_id", None)
        type = data.pop("type", None)
        cidr_ip = data.pop("cidr_ip", None)
        ip_protocol = data.pop("ip_protocol", None)
        ports = data.pop("ports", None)
        policy = data.pop("policy", None)
        description = data.pop("description")
        provider_id = data.pop("provider_id", None)

        _, result = self.resource.create(rid, name, provider_id,
                                      security_group_id, type,
                                      cidr_ip, ip_protocol,
                                      ports, policy, description,
                                      zone, region, extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
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
