# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.uuid_util import get_uuid
from lib.json_helper import format_json_dumps
from apps.background.models.dbserver import HistoryManager


class HistoryObject(object):
    def __init__(self):
        self.resource = HistoryManager()

    def list(self, filters=None, page=None, pagesize=None, orderby=None):
        filters = filters or {}

        count, results = self.resource.list(filters=filters, pageAt=page,
                                            pageSize=pagesize, orderby=orderby)
        data = []
        for res in results:
            res["ora_data"] = json.loads(res["ora_data"])
            data.append(res)

        return count, data

    def create(self, create_data):
        create_data["id"] = create_data.get("id") or get_uuid()
        create_data["ora_data"] = format_json_dumps(create_data.get("ora_data", {}))
        return self.resource.create(data=create_data)

    def show(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})

        data = self.resource.get(filters=where_data)
        if data:
            data["ora_data"] = json.loads(data["ora_data"])

        return data

    def query_one(self, where_data):
        data = self.resource.get(filters=where_data)
        if data:
            data["ora_data"] = json.loads(data["ora_data"])

        return data

    def update(self, rid, update_data, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        count, data = self.resource.update(filters=where_data, data=update_data)
        if data:
            data["ora_data"] = json.loads(data["ora_data"])

        return count, data

    def delete(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        return self.resource.delete(filters=where_data)

    def ora_delete(self, rid):
        return self.resource.delete(filters={"id": rid})
