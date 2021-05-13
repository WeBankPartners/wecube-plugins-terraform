# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.loadbalance.lb_rule import LBRuleApi
from apps.api.loadbalance.lb_rule import LBRuleBackendApi
from apps.controller.source_controller import BaseSourceController


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "listener_id", "extend_info", "lb_id",
                                      "security_group_id", "frontend_port",
                                      "name",
                                      # "domain", "url",
                                      # "health_check_http_code", "health_check_interval",
                                      # "health_check_uri", "health_check_connect_port",
                                      # "health_check_timeout", "health_check_http_method",
                                      # "scheduler", "certificate_id", "certificate_ca_id"
                                      ])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "lb_id"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_port(data.get("frontend_port"), permit_null=True)
        validation.validate_collector(data=data,
                                      strings=["id", "provider", "secret", "region", "zone",
                                               "listener_id", "lb_id",
                                               "security_group_id",
                                               "name",
                                               # "domain", "url",
                                               # "health_check_http_code", "health_check_interval",
                                               # "health_check_uri", "health_check_connect_port",
                                               # "health_check_timeout", "health_check_http_method",
                                               # "scheduler", "certificate_id", "certificate_ca_id"
                                               ],
                                      dicts=["extend_info"])

    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)

        frontend_port = validation.validate_port(data.pop("frontend_port", None), permit_null=True)

        create_data = {}
        for key in ["listener_id", "lb_id",
                    "security_group_id",
                    "name",
                    # "domain", "url",
                    # "health_check_http_code", "health_check_interval",
                    # "health_check_uri", "health_check_connect_port",
                    # "health_check_timeout", "health_check_http_method",
                    # "scheduler", "certificate_id", "certificate_ca_id"
                    ]:
            if data.get(key) is not None:
                create_data[key] = data.pop(key, None)

        if frontend_port:
            create_data["frontend_port"] = frontend_port

        asset_id = data.pop("asset_id", None)
        resource_id = data.pop("resource_id", None)

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    asset_id=asset_id,
                                    resource_id=resource_id,
                                    create_data=create_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))}
        return res, result


class LBRuleController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = LBRuleApi()

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
                                      "provider_id", "name", "lb_id", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return 1, res


class LBRuleIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE', 'PATCH')
    resource = LBRuleApi()

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


class LBRuleAddController(BaseController):
    allow_methods = ("POST",)
    resource = LBRuleBackendApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class LBRuleDeleteController(BaseController):
    name = "LBRule"
    resource_describe = "LBRule"
    allow_methods = ("POST",)
    resource = LBRuleBackendApi()

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


class LBRuleSourceController(BaseSourceController):
    name = "LBRule"
    resource_describe = "LBRule"
    allow_methods = ("POST",)
    resource = LBRuleBackendApi()
