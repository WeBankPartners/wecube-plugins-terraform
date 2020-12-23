# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from apps.api.configer.provider import ProviderApi
from apps.api.configer.provider import ProviderObject
from core import local_exceptions as exception_common
from core import validation
from core.controller import BaseController
from lib.uuid_util import get_uuid


class ProviderBaseController(BaseController):
    def not_null_keys(self):
        return ["name", "secret_id", "secret_key"]

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=self.not_null_keys()
                                    )

        validation.validate_string("name", data["name"])
        validation.validate_string("source", data.get("source"))
        validation.validate_string("secret_id", data.get("secret_id"))
        validation.validate_string("secret_key", data.get("secret_key"))
        validation.validate_string("location", data.get("location"))
        validation.validate_dict("extend_info", data.get("extend_info"))


class ProviderListController(BaseController):
    name = "Provider"
    resource_describe = "Provider"
    allow_methods = ('POST',)
    resource = ProviderObject()

    def response_templete(self, data):
        return []

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "enabled"])

    def main_response(self, request, data, **kwargs):
        count, result = self.resource.list(data)
        return result


class ProviderAddController(ProviderBaseController):
    name = "Provider"
    resource_describe = "Provider"
    allow_methods = ("POST",)
    resource = ProviderObject()

    def not_null_keys(self):
        return ["name", "secret_id", "secret_key", "region"]

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "zone", "secret_id",
                                      "secret_key", "region", "enabled",
                                      "extend_info", "plugin_source",
                                      "provider_property"])
        validation.not_allowed_null(data=data,
                                    keys=self.not_null_keys()
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("region", data.get("region"))
        validation.validate_string("zone", data.get("zone"))
        validation.validate_string("secret_id", data.get("secret_id"))
        validation.validate_string("secret_key", data.get("secret_key"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_dict("provider_property", data.get("provider_property"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        name = data.get("name")
        ProviderApi().create_provider_workspace(provider=name)
        rid = get_uuid()
        create_data = {"id": rid, "name": data["name"],
                       "secret_id": data.get("secret_id"),
                       "secret_key": data.get("secret_key"),
                       "region": data.get("region"),
                       "zone": data.get("zone"),
                       "extend_info": json.dumps(data.get("extend_info", {})),
                       "provider_property": json.dumps(data.get("provider_property", {})),
                       "is_init": 1
                       }
        result = self.resource.create(create_data)
        return {"result": result}


class ProviderIdController(BaseController):
    name = "Provider.id"
    resource_describe = "Provider"
    allow_methods = ("POST",)
    resource = ProviderObject()

    def before_handler(self, request, data, **kwargs):
        pass


    def response_templete(self, data):
        # todo detail Provider
        return {}

    def main_response(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)

        result = self.resource.show(rid)
        if not result:
            raise exception_common.ResourceNotFoundError()

        return result


class ProviderUpdateController(ProviderBaseController):
    name = "Provider"
    resource_describe = "Provider"
    allow_methods = ("POST",)
    resource = ProviderObject()

    def before_handler(self, request, data, **kwargs):
        pass

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        result = self.resource.update(rid, data)
        if not result:
            raise exception_common.ResourceNotFoundError()

        return result

class ProviderDeleteController(ProviderBaseController):
    name = "Provider"
    resource_describe = "Provider"
    allow_methods = ("POST",)
    resource = ProviderObject()

    def before_handler(self, request, data, **kwargs):
        pass

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        result = self.resource.delete(rid)
        if not result:
            raise exception_common.ResourceNotFoundError()

        return result
