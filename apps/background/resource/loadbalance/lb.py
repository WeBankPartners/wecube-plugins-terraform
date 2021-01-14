# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import datetime
from lib.logs import logger
from lib.uuid_util import get_uuid
from core import local_exceptions
from apps.background.models.dbserver import LBManager


class LBObject(object):
    def __init__(self):
        self.resource = LBManager()

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
        where_data.update({"id": rid, "is_deleted": 0})
        data = self.resource.get(filters=where_data)
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

        return count, data

    def delete(self, rid):
        count, data = self.update(rid, update_data={"is_deleted": 1, "deleted_time": datetime.datetime.now()})
        return count

    def lb_resource_id(self, rid):
        data = self.show(rid)
        if not data:
            raise local_exceptions.ValueValidateError("lb", "lb %s 不存在" % rid)
        return data["resource_id"]
