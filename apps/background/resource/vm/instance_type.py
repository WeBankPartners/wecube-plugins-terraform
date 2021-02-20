# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import datetime
from lib.uuid_util import get_uuid
from core import local_exceptions
from apps.background.resource.resource_base import ResourceBaseObject
from apps.background.models.dbserver import InstanceTypeManager


class InstanceTypeObject(ResourceBaseObject):
    def __init__(self):
        self.resource = InstanceTypeManager()

    def list(self, filters=None, page=None, pagesize=None, orderby=None):
        filters = filters or {}
        filters["is_deleted"] = 0

        count, results = self.resource.list(filters=filters, pageAt=page,
                                            pageSize=pagesize, orderby=orderby)
        data = []
        for res in results:
            res["extend_info"] = json.loads(res["extend_info"])
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

        return data

    def update(self, rid, update_data, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid, "is_deleted": 0})
        update_data["updated_time"] = datetime.datetime.now()
        count, data = self.resource.update(filters=where_data, data=update_data)
        if data:
            data["extend_info"] = json.loads(data["extend_info"])

        return count, data

    def delete(self, rid):
        count, data = self.update(rid, update_data={"is_deleted": 1, "deleted_time": datetime.datetime.now()})
        return count

    def type_resource_id(self, provider_id, name):
        data = self.resource.get(filters={"provider_id": provider_id,
                                          "name": name})
        if not data:
            raise local_exceptions.ValueValidateError("instance type name", "instance type name %s 不存在" % name)
        return data["origin_name"], data

    def convert_resource_id(self, provider_id, name):
        data = self.resource.get(filters={"provider_id": provider_id,
                                          "name": name})
        if data:
            return data["origin_name"], data
        else:
            return name, {"cpu": 0, "memory": 0}

    def convert_resource_name(self, provider, name):
        data = self.resource.get(filters={"provider": provider,
                                          "name": name})
        if data:
            return data["origin_name"], data
        else:
            return name, {"cpu": 0, "memory": 0}

    def ora_delete(self, rid):
        return self.resource.delete(filters={"id": rid})

