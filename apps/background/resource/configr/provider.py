# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import datetime
from core import local_exceptions
from lib.uuid_util import get_uuid
from lib.encrypt_helper import encrypt_str
from lib.encrypt_helper import decrypt_str
from apps.background.models.dbserver import ProvidersManager


class ProviderObject(object):
    def __init__(self):
        self.resource = ProvidersManager()

    def list(self, filters=None, page=None, pagesize=None, orderby=None):
        filters = filters or {}
        filters["is_deleted"] = 0

        count, results = self.resource.list(filters=filters, pageAt=page,
                                            pageSize=pagesize, orderby=orderby)
        data = []
        for res in results:
            res["extend_info"] = json.loads(res["extend_info"])
            res["provider_property"] = json.loads(res["provider_property"])
            data.append(res)

        return count, data

    def create(self, create_data):
        if create_data.get("secret_id"):
            _key = create_data.get("secret_id")
            if not _key.startswith("{cipher_a}"):
                create_data["secret_id"] = "{cipher_a}" + encrypt_str(create_data.get("secret_id"))
        
        if create_data.get("secret_key"):
            _key = create_data.get("secret_key")
            if not _key.startswith("{cipher_a}"):
                create_data["secret_key"] = "{cipher_a}" + encrypt_str(create_data.get("secret_key"))
                
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
            data["provider_property"] = json.loads(data["provider_property"])

        return data

    def query_one(self, where_data):
        where_data = where_data or {}
        where_data.update({"is_deleted": 0})
        data = self.resource.get(filters=where_data)
        if data:
            data["extend_info"] = json.loads(data["extend_info"])
            data["provider_property"] = json.loads(data["provider_property"])

        return data

    def update(self, rid, update_data, where_data=None):
        if update_data.get("secret_id"):
            _key = update_data.get("secret_id")
            if not _key.startswith("{cipher_a}"):
                update_data["secret_id"] = "{cipher_a}" + encrypt_str(update_data.get("secret_id"))

        if update_data.get("secret_key"):
            _key = update_data.get("secret_key")
            if not _key.startswith("{cipher_a}"):
                update_data["secret_key"] = "{cipher_a}" + encrypt_str(update_data.get("secret_key"))
                
        where_data = where_data or {}
        where_data.update({"id": rid, "is_deleted": 0})
        update_data["updated_time"] = datetime.datetime.now()
        count, data = self.resource.update(filters=where_data, data=update_data)
        if data:
            data["extend_info"] = json.loads(data["extend_info"])
            data["provider_property"] = json.loads(data["provider_property"])

        return count, data

    def delete(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        return self.resource.delete(filters=where_data)

    def provider_object(self, provider_id):
        data = self.show(rid=provider_id)
        if not data:
            raise local_exceptions.ResourceValidateError("provider", "provider %s 未注册" % provider_id)
        return data

    def provider_name_object(self, provider):
        if not provider:
            raise local_exceptions.ResourceValidateError("provider", "provider 不允许为空")

        data = self.query_one(where_data={"name": provider})
        if not data:
            raise local_exceptions.ResourceValidateError("provider", "provider %s 未注册" % provider)
        return data

    def ora_delete(self, rid):
        return self.resource.delete(filters={"id": rid})

