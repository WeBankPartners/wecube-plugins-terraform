# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import datetime
from lib.uuid_util import get_uuid
from apps.background.models.dbserver import ConfigManager


class ValueConfigObject(object):
    def __init__(self):
        self.resource = ConfigManager()

    def list(self, filters=None, page=None, pagesize=None, orderby=None):
        count, results = self.resource.list(filters=filters, pageAt=page,
                                            pageSize=pagesize, orderby=orderby)
        data = []
        for res in results:
            res["value_config"] = json.loads(res["value_config"])
            data.append(res)

        return count, data

    def create(self, create_data):
        create_data["id"] = create_data.get("id") or get_uuid()
        create_data["created_time"] = datetime.datetime.now()
        create_data["updated_time"] = create_data["created_time"]
        return self.resource.create(data=create_data)

    def show(self, rid, where_data=None):
        where_data = where_data or {}
        filters = where_data.update({"id": rid})
        return self.query_one(filters)

    def query_one(self, where_data):
        data = self.resource.get(filters=where_data)
        if data:
            data["value_config"] = json.loads(data["value_config"])
        return data

    def resource_value_configs(self, provider, resource):
        where_data = {"provider": provider, "resource": resource}
        count, datas = self.list(filters=where_data)
        res = {}
        for data in datas:
            res[data["property"]] = data["value_config"]

        if "zone" not in res.keys():
            _zone = self.query_one(where_data={"provider": provider, "resource": "zone"})
            if _zone:
                res["zone"] = _zone["value_config"]

        return res

    def update(self, rid, update_data, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        update_data["updated_time"] = datetime.datetime.now()
        count, data = self.resource.update(filters=where_data, data=update_data)
        if data:
            data["value_config"] = json.loads(data["value_config"])
        return count, data

    def delete(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        return self.resource.delete(filters=where_data)
