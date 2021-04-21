# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import datetime
from lib.encrypt_helper import encrypt_str
from lib.encrypt_helper import decrypt_str
from lib.uuid_util import get_uuid
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.background.models.dbserver import CrsManager


class ResourceBaseObject(object):
    resource = None

    def ora_show(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        return self.resource.get(filters=where_data)

    def ora_delete(self, rid):
        return self.resource.delete(filters={"id": rid})


class CrsObject(object):
    def __init__(self, resource_name=None):
        self.resource = CrsManager()
        self.resource_name = resource_name

    def query_one(self, where_data=None):
        where_data = where_data or {}

        if self.resource_name:
            where_data["resource_name"] = self.resource_name

        data = self.resource.get(filters=where_data)
        if data:
            data["propertys"] = json.loads(data["propertys"])
            data["output_json"] = json.loads(data["output_json"])
            data["extend_info"] = json.loads(data["extend_info"])
            data["define_json"] = json.loads(data["define_json"])
            data["result_json"] = json.loads(data["result_json"])

        return data

    def list(self, filters=None, page=None, pagesize=None, orderby=None):
        filters = filters or {}
        filters["is_deleted"] = 0

        if self.resource_name:
            filters["resource_name"] = self.resource_name

        count, results = self.resource.list(filters=filters, pageAt=page,
                                            pageSize=pagesize, orderby=orderby)
        data = []
        for res in results:
            res["propertys"] = json.loads(res["propertys"])
            res["output_json"] = json.loads(res["output_json"])
            res["extend_info"] = json.loads(res["extend_info"])
            res["define_json"] = json.loads(res["define_json"])
            res["result_json"] = json.loads(res["result_json"])
            data.append(res)

        return count, data

    def create(self, create_data):
        if self.resource_name:
            create_data["resource_name"] = self.resource_name

        propertys = create_data.get("propertys", {})
        if propertys.get("password"):
            password = propertys.get("password")
            if not password.startswith("{cipher_a}"):
                propertys["password"] = "{cipher_a}" + encrypt_str(password)

        create_data["propertys"] = propertys
        _after_data = {}
        for key, value in create_data.items():
            if isinstance(value, dict):
                value = format_json_dumps(value)

            _after_data[key] = value

        _after_data["id"] = create_data.get("id") or get_uuid()
        _after_data["created_time"] = datetime.datetime.now()
        _after_data["updated_time"] = _after_data["created_time"]
        return self.resource.create(data=_after_data)

    def show(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid, "is_deleted": 0})

        if self.resource_name:
            where_data["resource_name"] = self.resource_name

        data = self.resource.get(filters=where_data)
        if data:
            data["propertys"] = json.loads(data["propertys"])
            data["output_json"] = json.loads(data["output_json"])
            data["extend_info"] = json.loads(data["extend_info"])
            data["define_json"] = json.loads(data["define_json"])
            data["result_json"] = json.loads(data["result_json"])

        return data

    def update(self, rid, update_data, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid, "is_deleted": 0})

        if self.resource_name:
            where_data["resource_name"] = self.resource_name

        propertys = update_data.get("propertys", {})
        if propertys.get("password"):
            password = propertys.get("password")
            if not password.startswith("{cipher_a}"):
                propertys["password"] = "{cipher_a}" + encrypt_str(password)

            update_data["propertys"] = propertys

        _after_data = {}
        for key, value in update_data.items():
            if isinstance(value, dict):
                value = format_json_dumps(value)

            _after_data[key] = value

        _after_data["updated_time"] = datetime.datetime.now()
        count, data = self.resource.update(filters=where_data, data=_after_data)
        if data:
            data["propertys"] = json.loads(data["propertys"])
            data["output_json"] = json.loads(data["output_json"])
            data["extend_info"] = json.loads(data["extend_info"])
            data["define_json"] = json.loads(data["define_json"])
            data["result_json"] = json.loads(data["result_json"])

        return count, data

    def ora_update(self, rid, update_data, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})

        if self.resource_name:
            where_data["resource_name"] = self.resource_name

        propertys = update_data.get("propertys", {})
        if propertys.get("password"):
            password = propertys.get("password")
            if not password.startswith("{cipher_a}"):
                propertys["password"] = "{cipher_a}" + encrypt_str(password)

            update_data["propertys"] = propertys

        _after_data = {}
        for key, value in update_data.items():
            if isinstance(value, dict):
                value = format_json_dumps(value)

            _after_data[key] = value

        _after_data["updated_time"] = datetime.datetime.now()
        count, data = self.resource.update(filters=where_data, data=_after_data)
        if data:
            data["propertys"] = json.loads(data["propertys"])
            data["output_json"] = json.loads(data["output_json"])
            data["extend_info"] = json.loads(data["extend_info"])
            data["define_json"] = json.loads(data["define_json"])
            data["result_json"] = json.loads(data["result_json"])

        return count, data

    def delete(self, rid, update_data=None):
        update_data = update_data or {}
        update_data["is_deleted"] = 1
        update_data["deleted_time"] = datetime.datetime.now()
        count, data = self.update(rid, update_data=update_data)
        return count

    def object_resource_id(self, rid):
        data = self.show(rid)
        if not data:
            raise local_exceptions.ValueValidateError(self.resource_name, "资源 %s 不存在" % rid)
        return data["resource_id"]

    def object_asset_id(self, rid):
        data = self.show(rid)
        if data:
            return data["resource_id"]
        else:
            logger.info("search id: %s, asset id: null, may it's asset id, return" % rid)

        return rid

    def ora_show(self, rid, where_data=None):
        where_data = where_data or {}
        if self.resource_name:
            where_data["resource_name"] = self.resource_name

        where_data.update({"id": rid})
        return self.resource.get(filters=where_data)

    def ora_delete(self, rid):
        where_data = {"id": rid}
        if self.resource_name:
            where_data["resource_name"] = self.resource_name

        return self.resource.delete(filters=where_data)
