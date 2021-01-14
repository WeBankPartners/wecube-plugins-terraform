# coding: utf-8

import datetime
from lib.uuid_util import get_uuid
from apps.background.models.dbserver import CommonKeyManager


class CommonKeyObject(object):
    def __init__(self):
        self.resource = CommonKeyManager()

    def list(self, filters=None, page=None, pagesize=None, orderby=None):
        return self.resource.list(filters=filters, pageAt=page,
                                  pageSize=pagesize, orderby=orderby)

    def create(self, create_data):
        create_data["id"] = create_data.get("id") or get_uuid()
        create_data["created_time"] = datetime.datetime.now()
        create_data["updated_time"] = create_data["created_time"]
        return self.resource.create(data=create_data)

    def show(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        return self.resource.get(filters=where_data)

    def query_one(self, where_data):
        return self.resource.get(filters=where_data)

    def update(self, rid, update_data, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        update_data["updated_time"] = datetime.datetime.now()
        return self.resource.update(filters=where_data, data=update_data)

    def delete(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        return self.resource.delete(filters=where_data)
