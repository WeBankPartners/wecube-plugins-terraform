# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import datetime
from lib.uuid_util import get_uuid
from core import local_exceptions
from apps.background.models.dbserver import CCNManager
from apps.background.models.dbserver import CCNAttachManager
from apps.background.models.dbserver import CCNBandwidthManager


class _ConnectNetBase(object):
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


class CCNObject(_ConnectNetBase):
    def __init__(self):
        super(CCNObject, self).__init__()
        self.resource = CCNManager()

    def resource_id(self, rid, where_data=None):
        ccn = self.show(rid, where_data)
        if not ccn:
            raise local_exceptions.ValueValidateError("ccn", "ccn %s 不存在 或 不在同一区域" % rid)
        return ccn["resource_id"]


class CCNAttachObject(_ConnectNetBase):
    def __init__(self):
        super(CCNAttachObject, self).__init__()
        self.resource = CCNAttachManager()


class CCNBandwidthObject(_ConnectNetBase):
    def __init__(self):
        super(CCNBandwidthObject, self).__init__()
        self.resource = CCNBandwidthManager()
