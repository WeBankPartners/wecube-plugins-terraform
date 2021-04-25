# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.uuid_util import get_uuid
from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from apps.common.convert_keys import validate_convert_key
from apps.common.convert_keys import validate_convert_value
from apps.api.configer.resource import ResourceObject
from apps.api.configer.provider import ProviderObject
from .model_args import property_necessary
from .model_args import output_necessary
from .model_args import source_necessary


class ResourceController(BackendController):
    resource = ResourceObject()

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        validation.allowed_key(data, ["id", "provider", "resource_type", "resource_name",
                                      "data_source_argument", "data_source_name"])

        filter_string = None
        for key in ["resource_type", "provider", "resource_name", "data_source_name"]:
            if data.get(key):
                if filter_string:
                    filter_string += 'and ' + key + " like '%" + data.get(key) + "%' "
                else:
                    filter_string = key + " like '%" + data.get(key) + "%' "
                data.pop(key, None)

        return self.resource.list(filters=data, page=page,
                                  filter_string=filter_string,
                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "provider", "resource_type", "extend_info",
                                      "resource_name", "resource_property", "resource_output",
                                      "data_source", "data_source_name",
                                      "data_source_output", "data_source_argument"])
        validation.not_allowed_null(data=data,
                                    keys=["provider", "resource_type",
                                          "resource_name", "resource_property"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("provider", data["provider"])
        validation.validate_string("resource_type", data.get("resource_type"))

        # for resource
        validation.validate_string("resource_name", data.get("resource_name"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_dict("resource_property", data.get("resource_property"))
        validation.validate_dict("resource_output", data.get("resource_output"))

        # for data source
        validation.validate_string("data_source_name", data.get("data_source_name"))
        validation.validate_string("data_source_argument", data.get("data_source_argument"))
        validation.validate_dict("data_source", data.get("data_source"))
        validation.validate_dict("data_source_output", data.get("data_source_output"))

    def create(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        extend_info： {}  define example: {"version": "v1.1.0"}
        resource_property ｛｝define property for provider， example secret_key to key
        define example: {"secret_key": "key"}
        :param kwargs:
        :return:
        '''
        # todo  新增资源查询data resource 回刷定义/或启用新的资源进行定义

        # resource
        extend_info = validation.validate_dict("extend_info", data.get("extend_info")) or {}
        resource_property = validation.validate_dict("resource_property", data.get("resource_property")) or {}
        resource_output = validation.validate_dict("resource_output", data.get("resource_output")) or {}

        data_source = validation.validate_dict("data_source", data.get("data_source"))
        data_source_output = validation.validate_dict("data_source_output", data.get("data_source_output"))

        # for _, value in data_source_output.items():
        #     if not isinstance(value, basestring):
        #         raise ValueError("data_source_output 为key-value定义")

        validate_convert_key(resource_property)
        validate_convert_value(extend_info)
        validate_convert_value(resource_output)
        validate_convert_key(data_source_output)
        property_necessary(resource_name=data["resource_name"],
                           resource_property=resource_property)

        output_necessary(resource_name=data["resource_name"],
                         resource_output=resource_output)

        source_necessary(resource_name=data["resource_name"],
                         data_source=data_source)

        property_necessary(resource_name=data["resource_name"],
                           resource_property=data_source_output)

        ProviderObject().provider_name_object(data["provider"])
        create_data = {"id": data.get("id") or get_uuid(),
                       "provider": data["provider"],
                       "resource_type": data.get("resource_type"),
                       "resource_name": data.get("resource_name"),
                       "extend_info": json.dumps(extend_info),
                       "resource_property": json.dumps(resource_property),
                       "resource_output": json.dumps(resource_output),
                       "data_source_name": data.get("data_source_name"),
                       "data_source_argument": data.get("data_source_argument"),
                       "data_source_output": json.dumps(data_source_output),
                       "data_source": json.dumps(data_source)
                       }

        return self.resource.create(create_data)


class ResourceIdController(BackendIdController):
    resource = ResourceObject()

    def show(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.show(rid)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["provider", "resource_type", "extend_info",
                                      "resource_name", "resource_property",
                                      "enabled", "resource_output",
                                      "data_source", "data_source_name",
                                      "data_source_output", "data_source_argument"])

        validation.validate_string("provider", data["provider"])
        validation.validate_string("resource_type", data.get("resource_type"))

        # for resource
        validation.validate_string("resource_name", data.get("resource_name"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_dict("resource_property", data.get("resource_property"))
        validation.validate_dict("resource_output", data.get("resource_output"))

        # for data source
        validation.validate_string("data_source_name", data.get("data_source_name"))
        validation.validate_string("data_source_argument", data.get("data_source_argument"))
        validation.validate_dict("data_source", data.get("data_source"))
        validation.validate_dict("data_source_output", data.get("data_source_output"))

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        if data.get("extend_info") is not None:
            extend_info = validation.validate_dict("extend_info", data.get("extend_info"))
            validate_convert_value(extend_info)
            data["extend_info"] = json.dumps(extend_info)

        if data.get("resource_property") is not None:
            resource_property = validation.validate_dict("resource_property", data.get("resource_property")) or {}
            validate_convert_key(resource_property)
            property_necessary(resource_name=data["resource_name"],
                               resource_property=resource_property)

            data["resource_property"] = json.dumps(resource_property)

        if data.get("resource_output") is not None:
            resource_output = validation.validate_dict("resource_output", data.get("resource_output")) or {}
            validate_convert_value(resource_output)
            output_necessary(resource_name=data["resource_name"],
                             resource_output=resource_output)

            data["resource_output"] = json.dumps(resource_output)

        if data.get("data_source") is not None:
            data_source = validation.validate_dict("data_source", data.get("data_source"))
            source_necessary(resource_name=data["data_source"],
                             data_source=data_source)

            data["data_source"] = json.dumps(data_source)

        if data.get("data_source_output") is not None:
            data_source_output = validation.validate_dict("data_source_output", data.get("data_source_output"))

            property_necessary(resource_name=data["resource_name"],
                               resource_property=data_source_output)

            for _, value in data_source_output.items():
                if not isinstance(value, basestring):
                    raise ValueError("data_source_output 为key-value定义")

            data["data_source_output"] = json.dumps(data_source_output)

        if "provider" in data.keys():
            if not data.get("provider"):
                raise ValueError("provider 不能为空")
            ProviderObject().provider_name_object(data["provider"])

        return self.resource.update(rid, data)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.delete(rid)
