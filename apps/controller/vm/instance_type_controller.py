# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.uuid_util import get_uuid
from core import validation
from core.controller import BackendController
from apps.api.vm.instance_type import InstanceTypeApi


class InstanceTypeController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = InstanceTypeApi()

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

        validation.allowed_key(data, ["id", "provider", "origin_name", "cpu", "memory",
                                      "provider_id", "name", "enabled"])
        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "provider_id", "origin_name",
                                      "cpu", "memory", "network", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["provider_id", "origin_name", "name", "cpu", "memory"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("origin_name", data["origin_name"])
        validation.validate_int("cpu", data.get("cpu"))
        validation.validate_int("memory", data["memory"])
        validation.validate_string("network", data.get("network"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def create(self, request, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        name = data.pop("name", None)
        origin_name = data.pop("origin_name", None)
        cpu = data.pop("cpu", None)
        memory = data.pop("memory", None)
        network = data.pop("network", None)
        provider_id = data.pop("provider_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        data.update(extend_info)

        create_data = {"id": rid,
                       "name": name,
                       "origin_name": origin_name,
                       "cpu": cpu, "memory": memory,
                       "network": network,
                       "extend_info": json.dumps(extend_info),
                       }

        return self.resource.resource_object.create(create_data)


class InstanceTypeIdController(BackendController):
    allow_methods = ('GET', 'DELETE', 'PATCH')
    resource = InstanceTypeApi()

    def show(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.resource_object.show(rid)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["name", "provider_id", "origin_name",
                                      "cpu", "memory", "network", "extend_info"])

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("origin_name", data["origin_name"])
        validation.validate_int("cpu", data.get("cpu"))
        validation.validate_int("memory", data["memory"])
        validation.validate_string("network", data.get("network"))
        validation.validate_string("provider_id", data.get("provider_id"))
        validation.validate_dict("extend_info", data.get("extend_info"))

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)

        if data.get("extend_info") is not None:
            extend_info = validation.validate_dict("extend_info", data.get("extend_info"))
            data["extend_info"] = json.dumps(extend_info)

        return self.resource.resource_object.update(rid, data)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.resource_object.delete(rid)
