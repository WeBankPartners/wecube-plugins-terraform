# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.configer.resource import ResourceObject
# from apps.api.loadbalance.lb_group import BackendApi
# from apps.api.loadbalance.lb_group import BackendBackendApi

from apps.controller.source_controller import BaseSourceController
from apps.api.conductor.provider import ProviderConductor
from apps.api.conductor.region import RegionConductor
from apps.api.conductor.apply_data_conductor import apply_data_builder
from apps.api.conductor.source_data_conductor import query_data_builder


# todo provider校验
# todo  region / zone 信息校验
# todo   add data 获取
# @ todo   add  data数据校验，数据转换， 资产id转换， 数据格式生成

def not_null(key, data):
    if not data:
        raise ValueError("%s 不能为空" % key)


class ResBase(object):
    @classmethod
    def get_id(cls, data):
        return data.get("id") or get_uuid()

    @classmethod
    def get_provider(cls, data):
        '''

        :param data:
        :return:
        '''

        provider = data.get("provider")
        not_null("provider", provider)

        provider_data = ProviderConductor().find_provider_info(provider)
        provider = provider_data.get("name")
        return provider, provider_data

    @classmethod
    def get_region(cls, provider, data):
        '''

        :param provider:
        :param data:
        :return:
        '''

        region = data.get("region")
        not_null("region", region)
        _, region_info = RegionConductor().provider_region_info(provider=provider, region=region)
        return region_info.get("name"), region_info

    @classmethod
    def get_zone(cls, provider, region, data):
        zone = data.get("zone")
        not_null("zone", zone)
        _, zone_info = RegionConductor().provider_zone_info(provider=provider, region=region, zone=zone)
        return zone_info.get("name"), zone_info

    @classmethod
    def get_secret(cls, provider, region, data, provider_data):
        secret = data.get("secret")
        not_null("secret", secret)
        secret_info = ProviderConductor().producer_secret_info(provider=provider, region=region,
                                                               secret=secret, provider_data=provider_data)

        return secret, secret_info

    @classmethod
    def get_define_data(cls, provider, resource_name):
        return ResourceObject().query_one(where_data={"provider": provider,
                                                      "resource_name": resource_name})

    @classmethod
    def get_resource_define(cls, provider, resource_name):
        data = cls.get_define_data(provider, resource_name)
        return data.get("resource_property") or {}

    @classmethod
    def get_data_source_define(cls, provider, resource_name):
        data = cls.get_define_data(provider, resource_name)
        return data.get("data_source") or {}

    # @classmethod
    # def allow_key(cls, data):
    #     common_keys = ["id", "provider", "secret", "region", "zone"]
    #
    #     validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
    #                                   "name", "lb_id", "instance_id", "port"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "region", "zone", "provider", "secret"],
                                      dicts=["extend_info"])


    @classmethod
    def apply_main_infos(cls, data):
        provider, provider_data = cls.get_provider(data)
        region, region_info = cls.get_region(provider, data)
        zone, zone_info = cls.get_zone(provider, region, data)
        secret, secret_info = cls.get_secret(provider=provider, region=region,
                                             data=data, provider_data=provider_data)

        main_info = dict(provider=provider, region=region,
                         zone=zone, secret=secret)
        main_body = dict(provider_data=provider_data, region_info=region_info,
                         zone_info=zone_info, secret_info=secret_info)
        return main_info, main_body

    @classmethod
    def conductor_apply_data(cls, data):
        apply_data_builder(provider, datas, defines, resource_values_config)


    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = cls.get_id(data)
        main_info, main_body = cls.apply_main_infos(data)


        # rid = data.pop("id", None) or get_uuid()
        # secret = data.pop("secret", None)
        # region = data.pop("region", None)
        # zone = data.pop("zone", None)
        # provider = data.pop("provider", None)
        name = data.pop("name", None)
        lb_id = data.pop("lb_id", None)
        x_port = data.pop("port", None)
        port = int(x_port) if x_port is not None else None
        instance_id = data.pop("instance_id", None)

        asset_id = data.pop("asset_id", None)
        resource_id = data.pop("resource_id", None)

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        create_data = {"name": name, "lb_id": lb_id, "port": port,
                       "instance_id": instance_id}
        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    asset_id=asset_id,
                                    resource_id=resource_id,
                                    create_data=create_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))}
        return res, result


class BackendAddController(BaseController):
    name = "BackendAdd"
    resource_describe = "BackendAdd"
    allow_methods = ("POST",)
    resource = None

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class BackendDeleteController(BaseController):
    name = "Backend"
    resource_describe = "Backend"
    allow_methods = ("POST",)
    resource = None

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


class BackendSourceController(BaseSourceController):
    name = "Backend"
    resource_describe = "Backend"
    allow_methods = ("POST",)
    resource = None
