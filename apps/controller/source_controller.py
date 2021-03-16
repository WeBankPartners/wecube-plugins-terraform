# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from lib.uuid_util import get_uuid
from core import validation
from core.controller import BaseController
from core import local_exceptions as exception_common


class BaseSourceController(BaseController):
    name = ""
    resource_describe = ""
    allow_methods = ("POST",)
    resource = None

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "resource_id", "provider",
                                      "secret", "region", "zone"])

        validation.not_allowed_null(data=data,
                                    keys=["resource_id", "provider", "region"]
                                    )

        validation.validate_collector(data=data,
                                      strings=["id", "resource_id", "provider",
                                               "secret", "region", "zone"])

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)
        resource_id = data.get("resource_id")

        result = self.resource.get_remote_source(rid=rid, provider=provider,
                                                 region=region, zone=zone,
                                                 secret=secret, resource_id=resource_id)
        return result
