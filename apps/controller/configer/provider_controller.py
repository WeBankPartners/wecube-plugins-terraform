# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.uuid_util import get_uuid
from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from apps.common.convert_keys import validate_convert_key
from apps.common.convert_keys import validate_convert_value
from apps.api.configer.provider import ProviderApi
from apps.api.configer.provider import ProviderObject
from .model_args import property_necessary


class ProviderController(BackendController):
    allow_methods = ('GET', "POST")
    resource = ProviderObject()

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        validation.allowed_key(data.keys(), ["id", "name", "display_name", "region", "enabled"])
        return self.resource.list(filters=data, page=page,
                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "zone", "secret_id",
                                      "secret_key", "region", "enabled",
                                      "extend_info", "plugin_source",
                                      "provider_property", "display_name"])
        validation.not_allowed_null(data=data,
                                    keys=["name", "secret_id", "secret_key"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("display_name", data.get("display_name"))
        validation.validate_string("secret_id", data.get("secret_id"))
        validation.validate_string("secret_key", data.get("secret_key"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_dict("provider_property", data.get("provider_property"))

    def create(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        extend_info： {}  define example: {"version": "v1.1.0"}
        provider_property ｛｝revert property for provider， example secret_key to key
        define example: {"secret_key": "key"}
        :param kwargs:
        :return:
        '''

        name = data.get("name")
        extend_info = validation.validate_dict("extend_info", data.get("extend_info")) or {}
        provider_property = validation.validate_dict("provider_property", data.get("provider_property")) or {}
        validate_convert_key(provider_property)
        validate_convert_value(extend_info)
        property_necessary(resource_name="provider",
                           resource_property=provider_property)

        ProviderApi().create_provider_workspace(provider=name)
        create_data = {"id": data.get("id") or get_uuid(),
                       "name": data["name"],
                       "display_name": data.get("display_name"),
                       "secret_id": data.get("secret_id"),
                       "secret_key": data.get("secret_key"),
                       "extend_info": json.dumps(extend_info),
                       "provider_property": json.dumps(provider_property),
                       "is_init": 1
                       }

        return self.resource.create(create_data)


class ProviderIdController(BackendIdController):
    resource = ProviderObject()

    def show(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.show(rid)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["secret_id", "secret_key", "enabled",
                                      "name", "extend_info", "provider_property"])

        validation.validate_string("name", data.get("name"))
        validation.validate_string("secret_id", data.get("secret_id"))
        validation.validate_string("secret_key", data.get("secret_key"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_dict("provider_property", data.get("provider_property"))

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)

        if data.get("extend_info") is not None:
            extend_info = validation.validate_dict("extend_info", data.get("extend_info"))
            validate_convert_value(extend_info)
            data["extend_info"] = json.dumps(extend_info)

        if data.get("provider_property") is not None:
            provider_property = validation.validate_dict("provider_property", data.get("provider_property")) or {}
            validate_convert_key(provider_property)
            property_necessary(resource_name="provider",
                               resource_property=provider_property)
            data["provider_property"] = json.dumps(provider_property)

        return self.resource.update(rid, data)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.delete(rid)
