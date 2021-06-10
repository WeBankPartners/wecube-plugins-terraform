# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.uuid_util import get_uuid
from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from apps.common.convert_keys import validate_convert_key
from apps.common.convert_keys import validate_convert_value
from apps.api.configer.value_config import ValueConfigObject


class ConfigController(BackendController):
    resource = ValueConfigObject()

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

        validation.allowed_key(data, ["id", "resource", "provider", "property", "enabled"])

        filter_string = None
        for key in ["resource", "provider", "property"]:
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
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        validation.allowed_key(data, ["id", "provider", "resource", "property", "value_config"])
        validation.not_allowed_null(data=data,
                                    keys=["provider", "property", "resource"]

                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("provider", data["provider"])
        validation.validate_dict("value_config", data.get("value_config"))
        validation.validate_string("property", data.get("property"))
        validation.validate_string("resource", data.get("resource"))

    def create(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        value_config = validation.validate_dict("value_config", data.get("value_config")) or {}
        validate_convert_value(value_config)
        create_data = {"id": data.get("id") or get_uuid(),
                       "resource": data["resource"],
                       "provider": data.get("provider"),
                       "property": data.get("property"),
                       "value_config": json.dumps(value_config)
                       }

        return self.resource.create(create_data)


class ConfigIdController(BackendIdController):
    resource = ValueConfigObject()

    def show(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        return self.resource.show(rid)

    def before_handler(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        validation.allowed_key(data, ["provider", "resource", "property", "value_config"])

        validation.validate_bool("enabled", data.get("enabled"))
        validation.validate_string("id", data.get("id"))
        validation.validate_string("provider", data.get("provider"))
        validation.validate_dict("value_config", data.get("value_config"))
        validation.validate_string("property", data.get("property"))
        validation.validate_string("resource", data.get("resource"))

    def update(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        if data.get("value_config") is not None:
            value_config = validation.validate_dict("value_config", data.get("value_config"))
            validate_convert_value(value_config)
            data["value_config"] = json.dumps(value_config)

        return self.resource.update(rid, data)

    def delete(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        return self.resource.delete(rid)


class ConfigAttrController(BackendIdController):
    resource = ValueConfigObject()
    allow_methods = ('GET',)

    def get_configs(self, data):
        data["resource"] = data.pop("resource_type", None)
        _, config_datas = self.resource.list(filters=data)

        res = {}
        for xdata in config_datas:
            res[xdata["property"]] = xdata.get("value_config")

        return res

    def show(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''
        validation.allowed_key(data, ["resource_type", "provider"])
        validation.not_allowed_null(["resource_type", "provider"], data)

        configs = self.get_configs(data)

        columns = configs.keys()
        res = []
        for column in columns:
            res.append({"id": column, "name": column})

        return {"resource": res, "attribute": configs}


class ConfigListController(BackendIdController):
    resource = ValueConfigObject()
    allow_methods = ('GET',)

    def get_configs(self, data):
        data["resource"] = data.pop("resource_type", None)
        config_data = self.resource.query_one(where_data=data)

        return config_data.get("value_config") or {}

    def show(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''
        validation.allowed_key(data, ["resource_type", "provider", "property"])
        validation.not_allowed_null(["resource_type", "provider", "property"], data)

        configs = self.get_configs(data)

        res = []
        for key, value in configs.items():
            res.append({"id": key, "name": key, "origin_name": value})
        return {"resource": res}
