# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BackendIdController
from core.controller import BaseController
from lib.uuid_util import get_uuid
from apps.api.database.kvstore.kvstore import KvStoreApi
from apps.api.database.kvstore.kvstore import KvStoreBackendApi
from apps.controller.source_controller import BaseSourceController


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "extend_info", "subnet_id",
                                      "password", "port", "version", "instance_type",
                                      "vpc_id", "security_group_id", "engine",
                                      "charge_type"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "zone", "name",
                                          "version", "subnet_id", "instance_type"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "region", "zone",
                                               "provider", "secret", "subnet_id",
                                               "password", "port", "version",
                                               "instance_type", "charge_type",
                                               "vpc_id", "engine"],
                                      lists=["security_group_id"],
                                      dicts=["extend_info"])

    @classmethod
    def create(cls, resource, data, **kwargs):
        rid = data.pop("id", None) or get_uuid()
        secret = data.pop("secret", None)
        region = data.pop("region", None)
        zone = data.pop("zone", None)
        provider = data.pop("provider", None)
        name = data.pop("name", None)
        subnet_id = data.pop("subnet_id", None)
        port = data.pop("port", None)
        password = data.pop("password", None)
        version = data.pop("version", None)
        instance_type = data.pop("instance_type", None)
        engine = data.pop("engine", None)
        vpc_id = data.pop("vpc_id", None)
        charge_type = data.pop("charge_type", None)

        security_group_id = validation.validate_list("security_group_id", data.pop("security_group_id", None))

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        asset_id = data.pop("asset_id", None)
        resource_id = data.pop("resource_id", None)

        d = dict(version=version, port=port,
                 password=password, engine=engine,
                 instance_type=instance_type,
                 vpc_id=vpc_id,
                 security_group_id=security_group_id,
                 subnet_id=subnet_id,
                 charge_type= charge_type)

        create_data = {"name": name}
        create_data.update(d)
        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    asset_id=asset_id,
                                    resource_id=resource_id,
                                    create_data=create_data,
                                    extend_info=data)

        # _password = base64.b64decode(result.get("password")) if result.get("password") else None
        res = {"id": rid, "ipaddress": result.get("ipaddress"),
               "port": result.get("port"),
               "resource_id": str(result.get("resource_id"))[:64]}

        return res, result


class KvStoreController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = KvStoreApi()

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        '''

        :param request:
        :param data:
        :param orderby:
        :param page:
        :param pagesize:
        :param kwargs:
        :return:
        '''

        validation.allowed_key(data, ["id", "provider", "region", "zone", "provider_id",
                                      'resource_id', "name", "enabled",
                                      "subnet_id", "instance_type", "version",
                                      "ipaddress", "port", 'engine'])

        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return 1, res


class KvStoreIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = KvStoreApi()

    def show(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        return self.resource.resource_object.show(rid)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        force_delete = data.get("force_delete", False)
        return self.resource.destroy(rid)


class KvStoreAddController(BaseController):
    allow_methods = ("POST",)
    resource = KvStoreBackendApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class KvStoreDeleteController(BaseController):
    name = "KvStore"
    resource_describe = "KvStore"
    allow_methods = ("POST",)
    resource = KvStoreBackendApi()

    def before_handler(self, request, data, **kwargs):
        validation.not_allowed_null(data=data,
                                    keys=["id"]
                                    )

        validation.validate_string("id", data.get("id"))

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        rid = data.pop("id", None)
        force_delete = data.get("force_delete", False)
        result = self.resource.destroy(rid)
        return {"result": result}


class KvStoreSourceController(BaseSourceController):
    resource_describe = "KvStore"
    allow_methods = ("POST",)
    resource = KvStoreBackendApi()


class KvStoreSGSourceController(BaseSourceController):
    resource_describe = "KvStore"
    allow_methods = ("POST",)
    resource = KvStoreBackendApi()

    def fetch_source(self, rid, provider, region, zone, secret, resource_id, **kwargs):
        return self.resource.sg_kv_relationship(rid=rid, provider=provider,
                                                region=region, zone=zone,
                                                secret=secret,
                                                resource_id=resource_id)
