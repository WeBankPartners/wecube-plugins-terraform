# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import copy
from lib.logs import logger
from core import validation
from core.controller import BaseController
from lib.uuid_util import get_uuid
from core import local_exceptions
from apps.api.configer.resource import ResourceObject
from apps.controller.source_controller import BaseSourceController
from apps.api.conductor.provider import ProviderConductor
from apps.api.conductor.region import RegionConductor
from apps.api.conductor.type_format import TypeFormat
# from apps.api.conductor.apply_data_conductor import apply_data_builder
# from apps.api.conductor.source_data_conductor import query_data_builder
from apps.api.apibase_backend import ApiBackendBase
from apps.api.configer.region import ZoneApi
from apps.controller.configer.model_args import source_columns_outputs


def not_null(key, data):
    if not data:
        raise ValueError("%s 不能为空" % key)


def filter_action_output(out_datas, filters):
    res = []
    for out_data in out_datas:
        for key, value in filters.items():
            s_value = out_data.get(key)
            if isinstance(s_value, (basestring, int, float)):
                res.append({value: s_value})
            elif isinstance(s_value, list):
                for s in s_value:
                    res.append({value: s})
            else:
                logger.info("output value not string/int/list, skip ...")

    return res


class BackendClient(object):
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
        '''

        :param provider:
        :param region:
        :param data:
        :return:
        '''

        zone = data.get("zone")
        if not zone:
            return "", {}

        not_null("zone", zone)
        _, zone_info = RegionConductor().provider_zone_info(provider=provider, region=region, zone=zone)
        return zone_info.get("name"), zone_info

    @classmethod
    def get_secret(cls, provider, region, data):
        secret = data.get("secret")
        not_null("secret", secret)
        return secret

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
        '''

        :param data:
        :return:
        '''

        provider, provider_data = cls.get_provider(data)
        region, region_info = cls.get_region(provider, data)
        zone, zone_info = cls.get_zone(provider, region_info.get("id"), data)
        secret = cls.get_secret(provider=provider, region=region_info.get("name"), data=data)

        main_info = dict(provider=provider, region=region, zone=zone, secret=secret)
        main_body = dict(provider_data=provider_data, region_info=region_info, zone_info=zone_info)
        return main_info, main_body

    @classmethod
    def create(cls, resource, data, **kwargs):
        '''

        :param resource:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = cls.get_id(data)
        base_info, base_bodys = cls.apply_main_infos(data)

        # 兼容extend info字段
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        asset_id = data.pop("asset_id", None)
        resource_id = data.pop("resource_id", None)

        _, result = resource.create(rid=rid, base_info=base_info, base_bodys=base_bodys,
                                    create_data=data, extend_info=extend_info,
                                    asset_id=asset_id, resource_id=resource_id)

        return result

    @classmethod
    def source_pre_action(cls, rid, base_info, base_bodys, resource_object, data):
        pre_action = resource_object.get("pre_action")
        pre_action_output = resource_object.get("pre_action_output")
        if pre_action and pre_action_output:
            client = ApiBackendBase(resource_name=pre_action, resource_workspace=pre_action)
            results = client.get_remote_source(rid, base_info, base_bodys, query_data=data)
            return filter_action_output(results, filters=pre_action_output)

        return []

    @classmethod
    def data_source_action(cls):
        pass

    @classmethod
    def format_query_data(cls):
        pass

    @classmethod
    def get_resource_object(cls, provider, resource_name):
        resource_object = ResourceObject().query_one(where_data={"provider": provider,
                                                                 "resource_type": resource_name})
        if not resource_object:
            raise local_exceptions.ResourceConfigError("%s 资源未初始化完成配置" % resource_name)

        return resource_object

    @classmethod
    def adder_return(cls, data, results, resource_name):
        # 将传入参数返回
        res = []
        for result in results:
            if isinstance(result, basestring):
                res.append(result)
            else:
                for key, value in data.items():
                    if value and not result.get(key):
                        result[key] = value

                x_add = source_columns_outputs(resource_name)
                x_add.update(result)
                res.append(x_add)

        return res

    @classmethod
    def skipper_results(cls, provider, region, results, ignore_resources):
        '''

        :param provider:  name
        :param region:  id
        :return:
        '''
        ignore_resources = TypeFormat.f_list(ignore_resources)
        register_zones = ZoneApi().region_zones(region, provider)

        res = []
        for result in results:
            if isinstance(result, basestring):
                res.append(result)
            else:
                if result.get("zone") and (result.get("zone") not in register_zones):
                    logger.info("resource: %s ,zone: %s searched not in register zone, skip it" % (
                        result.get("resource_id"), result.get("zone")))
                elif result.get("resource_id") and result.get("resource_id") in ignore_resources:
                    logger.info("ignore_resources skip id: %s" % (result.get("resource_id")))
                else:
                    res.append(result)

        return res

    @classmethod
    def filter_data(cls, data, pre_results):
        resource_ids = TypeFormat.f_list(data.get("resource_id"))
        ignore_resources = TypeFormat.f_list(data.get("ignore_ids"))

        res = []
        if resource_ids:
            for result in pre_results:
                if result.get("resource_id") in resource_ids:
                    t_data = copy.deepcopy(data)
                    t_data.update(result)
                    res.append(t_data)

            return res

        if ignore_resources:
            for result in pre_results:
                if result.get("resource_id") and result.get("resource_id") in ignore_resources:
                    logger.info("skip resource id : %s" % (result.get("resource_id")))
                else:
                    t_data = copy.deepcopy(data)
                    t_data.update(result)
                    res.append(t_data)

            return res

        for result in pre_results:
            t_data = copy.deepcopy(data)
            t_data.update(result)
            res.append(t_data)

        return res or [data]

    @classmethod
    def one_query(cls, resource, rid, data, base_info, base_bodys):
        provider_object = base_bodys["provider_data"]
        region_object = base_bodys["region_info"]
        results = resource.get_remote_source(rid, base_info, base_bodys, query_data=data)
        results = cls.skipper_results(provider=provider_object["name"], region=region_object["id"],
                                      results=results, ignore_resources=data.get("ignore_resources"))
        results = cls.adder_return(data, results, resource_name=resource.resource_name)
        return results

    @classmethod
    def main_query(cls, resource, rid, data, base_info, base_bodys):
        provider_object = base_bodys["provider_data"]
        resource_object = cls.get_resource_object(provider=provider_object["name"],
                                                  resource_name=resource.resource_name)

        pre_results = cls.source_pre_action(rid, base_info, base_bodys, resource_object, data)
        query_datas = cls.filter_data(data, pre_results)

        result = []
        for query_data in query_datas:
            x_res = cls.one_query(resource, rid, query_data, base_info, base_bodys)
            result += x_res

        return result

    @classmethod
    def query(cls, resource, data, **kwargs):
        '''

        :param resource:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = cls.get_id(data)
        base_info, base_bodys = cls.apply_main_infos(data)

        # 兼容extend info字段
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)
        return cls.main_query(resource, rid, data, base_info, base_bodys)


class BackendAddController(BaseController):
    name = "BackendAdd"
    resource_describe = "BackendAdd"
    allow_methods = ("POST",)
    resource = None

    def before_handler(self, request, data, **kwargs):
        BackendClient.not_null(data)
        BackendClient.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        return BackendClient.create(resource=self.resource, data=data)


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


class BackendSourceController(BaseController):
    name = "Backend"
    resource_describe = "Backend"
    allow_methods = ("POST",)
    resource = None

    def before_handler(self, request, data, **kwargs):
        BackendClient.not_null(data)
        BackendClient.validate_keys(data)

    def response_templete(self, data):
        return []

    def main_response(self, request, data, **kwargs):
        return BackendClient.query(resource=self.resource, data=data)
