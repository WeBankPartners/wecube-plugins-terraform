# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.storage.bucket_object import BucketObjectApi


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "extend_info", "bucket_id",
                                      "key", "content", "source"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "bucket_id"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "region", "zone",
                                               "provider", "secret", "bucket_id",
                                               "key", "content", "source"],
                                      dicts=["extend_info"])

    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)
        name = data.pop("name", None)
        bucket_id = data.pop("bucket_id", None)
        key = data.pop("appid", None)
        content = data.pop("content", None)
        source = data.pop("source", None)

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        if source is None and content is None:
            raise ValueError("source 和 content 不能同时为null")

        create_data = {"name": name, "bucket_id": bucket_id, "key": key,
                       "content": content, "source": source}
        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    create_data=create_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64]}
        return res, result


class BucketObjectController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = BucketObjectApi()

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
                                      "provider_id", "bucket_id", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return 1, res


class BucketObjectIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE')
    resource = BucketObjectApi()

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


class BucketObjectAddController(BaseController):
    allow_methods = ("POST",)
    resource = BucketObjectApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class BucketObjectDeleteController(BaseController):
    name = "BucketObject"
    resource_describe = "BucketObject"
    allow_methods = ("POST",)
    resource = BucketObjectApi()

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
