# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json

from apps.api.configer.provider import ProviderApi
from apps.api.configer.provider import ProviderObject
from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from lib.uuid_util import get_uuid


class ProviderController(BackendController):
    allow_methods = ('GET', "POST")
    resource = ProviderObject()

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        validation.allowed_key(data.keys(), ["id", "name", "region", "enabled"])
        return self.resource.list(filters=data, page=page,
                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "zone", "secret_id",
                                      "secret_key", "region", "enabled",
                                      "extend_info", "plugin_source",
                                      "provider_property"])
        validation.not_allowed_null(data=data,
                                    keys=["name", "secret_id", "secret_key", "region"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data.get("region"))
        validation.validate_string("zone", data.get("zone"))
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
        ProviderApi().create_provider_workspace(provider=name)
        create_data = {"id": get_uuid(), "name": data["name"],
                       "secret_id": data.get("secret_id"),
                       "secret_key": data.get("secret_key"),
                       "region": data.get("region"),
                       "zone": data.get("zone"),
                       "extend_info": json.dumps(data.get("extend_info", {})),
                       "provider_property": json.dumps(data.get("provider_property", {})),
                       "is_init": 1
                       }

        return self.resource.create(create_data)


class ProviderIdController(BackendIdController):
    resource = ProviderObject()

    def show(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.show(rid)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["zone", "secret_id",
                                      "secret_key", "region", "enabled",
                                      "extend_info", "provider_property"])

        validation.validate_string("region", data.get("region"))
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("secret_id", data.get("secret_id"))
        validation.validate_string("secret_key", data.get("secret_key"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_dict("provider_property", data.get("provider_property"))

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        if data.get("extend_info") is not None:
            data["extend_info"] = json.dumps(data.get("extend_info", {}))

        if data.get("provider_property") is not None:
            data["provider_property"] = json.dumps(data.get("provider_property", {}))

        return self.resource.update(rid, data)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.delete(rid)
