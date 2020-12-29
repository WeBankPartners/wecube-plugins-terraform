# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import datetime
from lib.uuid_util import get_uuid
from apps.background.models.dbserver import SecGroupManager
from apps.background.models.dbserver import SecGroupRuleManager


class _SecBaseObject(object):
    def __init__(self):
        self.resource = None

    def list(self, filters=None, page=None, pagesize=None, orderby=None):
        filters = filters or {}
        filters["is_deleted"] = 0

        count, results = self.resource.list(filters=filters, pageAt=page,
                                            pageSize=pagesize, orderby=orderby)
        data = []
        for res in results:
            res["extend_info"] = json.loads(res["extend_info"])
            res["define_json"] = json.loads(res["define_json"])
            res["result_json"] = json.loads(res["result_json"])
            data.append(res)

        return count, data

    def create(self, create_data):
        create_data["id"] = create_data.get("id") or get_uuid()
        create_data["created_time"] = datetime.datetime.now()
        create_data["updated_time"] = create_data["created_time"]
        return self.resource.create(data=create_data)

    def show(self, rid, where_data=None):
        where_data = where_data or {}
        filters = where_data.update({"id": rid, "is_deleted": 0})
        data = self.resource.get(filters=filters)
        if data:
            data["extend_info"] = json.loads(data["extend_info"])
            data["define_json"] = json.loads(data["define_json"])
            data["result_json"] = json.loads(data["result_json"])

        return data

    def update(self, rid, update_data, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid, "is_deleted": 0})
        update_data["updated_time"] = datetime.datetime.now()
        count, data = self.resource.update(filters=where_data, data=update_data)
        if data:
            data["extend_info"] = json.loads(data["extend_info"])
            data["define_json"] = json.loads(data["define_json"])
            data["result_json"] = json.loads(data["result_json"])

        return data

    def delete(self, rid):
        count, data = self.update(rid, update_data={"is_deleted": 1})
        return count

class SecGroupObject(_SecBaseObject):
    def __init__(self):
        super(SecGroupObject, self).__init__()
        self.resource = SecGroupManager()


class SecGroupRuleObject(_SecBaseObject):
    def __init__(self):
        super(SecGroupRuleObject, self).__init__()
        self.resource = SecGroupRuleManager()

