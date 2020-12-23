# coding: utf-8

import datetime
import json

import os

from apps.background.lib.commander.terraform import TerraformDriver
from apps.background.models.dbserver import ProvidersManager
from core import local_exceptions
from lib.command import command
from lib.logs import logger
from lib.uuid_util import get_uuid
from wecube_plugins_terraform.settings import BASE_DIR
from wecube_plugins_terraform.settings import TERRAFORM_BASE_PATH
from wecube_plugins_terraform.settings import TERRFORM_BIN_PATH

if not os.path.exists(TERRAFORM_BASE_PATH):
    os.makedirs(TERRAFORM_BASE_PATH)


class ProviderApi(object):
    def init_provider(self, provider):
        provider_path = os.path.join(TERRAFORM_BASE_PATH, provider)
        if not os.path.exists(provider_path):
            os.makedirs(provider_path)

        return TerraformDriver(terraform_path=TERRFORM_BIN_PATH,
                               workdir=provider_path).init(provider_path)

    def _generate_info(self, provider, data):
        extend_info = data.get("extend_info", {})
        if isinstance(extend_info, basestring):
            extend_info = json.loads(extend_info)

        property = json.loads(data.get("provider_property", {}))
        if isinstance(property, basestring):
            property = json.loads(property)

        provider_info = {}
        region = data.get("region")
        secret_id = data.get("secret_id")
        secret_key = data.get("secret_key")
        if region:
            _region = property.get("region", "region")
            provider_info[_region] = region

        if secret_id:
            _secret_id = property.get("secret_id", "secret_id")
            provider_info[_secret_id] = secret_id

        if secret_key:
            _secret_key = property.get("secret_key", "secret_key")
            provider_info[_secret_key] = secret_key

        provider_info.update(extend_info)

        provider_data = {
            "provider": {
                provider: provider_info
            }
        }

        return provider_data

    def provider_info(self, provider, region=None, zone=None):
        where_data = {"name": provider}
        if region:
            where_data["region"] = region
        if zone:
            where_data["zone"] = zone

        data = ProviderObject().query_one(where_data=where_data)
        if not data:
            raise local_exceptions.ResourceNotFoundError("provider %s 不存在" % provider)

        if not data.get("is_init"):
            raise local_exceptions.ResourceConfigError("provider 未初始化，请重新初始化")

        return self._generate_info(provider, data)

    def create_provider_workspace(self, provider):
        provider_path = os.path.join(TERRAFORM_BASE_PATH, provider)
        provider_version = os.path.join(provider_path, "versions.tf")

        if not os.path.exists(provider_path):
            os.makedirs(provider_path)

        if not os.path.exists(provider_version):
            _version_path = os.path.join(BASE_DIR, "plugins/%s/versions.tf" %provider)
            if os.path.exists(_version_path):
                command(cmd="cp %s %s" % (_version_path, provider_path))
            else:
                logger.info("file: %s not found" % _version_path)

        return True


class ProviderObject(object):
    def __init__(self):
        self.resource = ProvidersManager()

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
        filters = where_data.update({"id": rid})
        return self.resource.get(filters=filters)

    def query_one(self, where_data):
        return self.resource.get(filters=where_data)

    def update(self, rid, update_data, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        update_data["update_time"] = datetime.datetime.now()
        return self.resource.update(filters=where_data, data=update_data)

    def delete(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        return self.resource.delete(filters=where_data)
