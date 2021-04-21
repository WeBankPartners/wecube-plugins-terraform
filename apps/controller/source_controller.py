# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from lib.uuid_util import get_uuid
from core import validation
from core.controller import BaseController
from core.response_hooks import format_string
from core import local_exceptions as exception_common
from apps.controller.configer.model_args import source_columns_outputs


class BaseSourceController(BaseController):
    name = ""
    resource_describe = ""
    allow_methods = ("POST",)
    resource = None

    def before_handler(self, request, data, **kwargs):
        # validation.allowed_key(data, ["id", "resource_id", "provider",
        #                               "secret", "region", "zone", "ignore_ids"])

        validation.not_allowed_null(data=data,
                                    keys=["provider", "region"]
                                    )

        validation.validate_collector(data=data,
                                      strings=["id", "resource_id", "provider",
                                               "secret", "region", "zone"],
                                      lists=["ignore_ids"])

    def response_templete(self, data):
        return {}

    def fetch_source(self, rid, provider, region, zone, secret, resource_id, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param zone:
        :param secret:
        :param resource_id:
        :param kwargs:
        :return:
        '''
        query_args = {}
        for key, value in kwargs.items():
            if value is not None:
                if not isinstance(value, (basestring, int, bool, float)):
                    raise ValueError("查询条件需为字符串/数字/布尔值")

                if value != '':
                    query_args[key] = value

        return self.resource.get_remote_source(rid=rid, provider=provider,
                                               region=region, zone=zone,
                                               secret=secret,
                                               resource_id=resource_id,
                                               **query_args)

    def one_query(self, rid, provider, region, zone, secret,
                  resource_id, ignore_ids, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param zone:
        :param secret:
        :param resource_id:
        :param ignore_ids:
        :param kwargs:
        :return:
        '''

        result = self.fetch_source(rid=rid, provider=provider, region=region, zone=zone,
                                   secret=secret, resource_id=resource_id,
                                   **kwargs)
        result_data = []
        for x_result in result:
            x_res = source_columns_outputs(self.resource.resource_name)
            x_res.update(x_result)
            res = {"region": region, "secret": secret, "provider": provider}
            for x, value in x_res.items():
                if isinstance(value, dict):
                    res[x] = format_string(value)
                else:
                    if value is None:
                        res[x] = ''
                    else:
                        res[x] = str(value)

            if res.get("resource_id") in ignore_ids:
                continue

            result_data.append(res)

        return result_data

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)
        resource_id = data.pop("resource_id", None)
        ignore_ids = data.pop("ignore_ids", [])

        if resource_id:
            resource_id = resource_id.strip()
            if resource_id.startswith("[") and resource_id.endswith("]"):
                resource_id = eval(resource_id)

            if resource_id == "*":
                resource_id = None

        if resource_id:
            result = []
            if isinstance(resource_id, basestring):
                result = self.one_query(rid=rid, provider=provider,
                                        region=region, zone=zone,
                                        secret=secret, resource_id=resource_id,
                                        ignore_ids=ignore_ids, **data)
            elif isinstance(resource_id, list):
                for r_resource_id in resource_id:
                    result += self.one_query(rid=rid, provider=provider,
                                             region=region, zone=zone,
                                             secret=secret, resource_id=r_resource_id,
                                             ignore_ids=ignore_ids, **data)
            else:
                raise ValueError("resource id error, please check")

            # return {"datas": result}
            return result

        result_data = self.one_query(rid=rid, provider=provider,
                                     region=region, zone=zone,
                                     secret=secret, resource_id=resource_id,
                                     ignore_ids=ignore_ids, **data)
        return result_data
