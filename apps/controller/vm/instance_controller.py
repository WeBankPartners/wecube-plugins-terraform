# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import validation
from core import local_exceptions
from core.controller import BackendController
from core.controller import BaseController
from core.controller import BackendIdController
from lib.uuid_util import get_uuid
from apps.api.vm.instance import InstanceApi
from apps.api.vm.instance import InstanceBackendApi
from apps.controller.source_controller import BaseSourceController


class ResBase(object):
    @classmethod
    def allow_key(cls, data):
        validation.allowed_key(data, ["id", "provider", "secret", "region", "zone",
                                      "name", "extend_info", "subnet_id",
                                      "hostname", "image", "instance_type",
                                      "disk_type", "disk_size", "password", "power_action",
                                      "security_group_id", "vpc_id", "data_disks",
                                      "charge_type"])

    @classmethod
    def allow_upgrade_key(cls, data):
        if not data:
            raise ValueError("没有需要更新的配置")

        validation.allowed_key(data, ["name", "instance_type", "image",
                                      "extend_info", "security_group_id"])

    @classmethod
    def not_null(cls, data):
        validation.not_allowed_null(data=data,
                                    keys=["region", "provider", "name",
                                           "subnet_id", "image",
                                          "instance_type"]
                                    )

    @classmethod
    def validate_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["id", "name", "region", "zone",
                                               "provider", "secret", "subnet_id",
                                               "hostname", "image", "instance_type",
                                               "disk_type", "password", "power_action",
                                               "security_group_id", "vpc_id",
                                               "charge_type"],
                                      ints=["disk_size"],
                                      dicts=["extend_info", "data_disks"])

    @classmethod
    def validate_upgrade_keys(cls, data):
        validation.validate_collector(data=data,
                                      strings=["name", "instance_type",
                                               "image", "security_group_id"],
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
        hostname = data.pop("hostname", None)
        image = data.pop("image", None)
        disk_type = data.pop("disk_type")
        disk_size = data.pop("disk_size", 40)
        instance_type = data.pop("instance_type", None)
        password = data.pop("password", None)
        vpc_id = data.pop("vpc_id", None)
        charge_type = data.pop("charge_type", None)
        security_group_id = data.pop("security_group_id", None)
        data_disks = validation.validate_dict("data_disks", data.pop("data_disks", None))

        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))
        data.update(extend_info)

        asset_id = data.pop("asset_id", None)
        resource_id = data.pop("resource_id", None)
        action = data.pop("power_action", None)

        d = dict(hostname=hostname, image=image,
                 instance_type=instance_type,
                 password=password, vpc_id=vpc_id,
                 security_group_id=security_group_id,
                 data_disks=data_disks,
                 disk_type=disk_type,
                 disk_size=disk_size,
                 subnet_id=subnet_id,
                 charge_type=charge_type)

        create_data = {"name": name}
        create_data.update(d)
        if action:
            create_data["power_action"] = action

        _, result = resource.create(rid=rid, provider=provider,
                                    region=region, zone=zone,
                                    secret=secret,
                                    asset_id=asset_id,
                                    resource_id=resource_id,
                                    create_data=create_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64],
               "ipaddress": result.get("ipaddress"),
               "cpu": result.get("cpu"),
               "memory": result.get("memory")}
        return res, result

    @classmethod
    def update(cls, resource, data, **kwargs):
        rid = kwargs.pop("rid", None)
        name = data.pop("name", None)
        instance_type = data.pop("instance_type")
        image = data.pop("image")
        security_group_id = data.pop("security_group_id", None)
        extend_info = validation.validate_dict("extend_info", data.pop("extend_info", None))

        update_data = {}
        if name:
            update_data["name"] = name
        if instance_type:
            update_data["instance_type"] = instance_type
        if security_group_id:
            update_data["security_group_id"] = security_group_id
        if image:
            update_data["image"] = image

        data.update(extend_info)
        _, result = resource.update(rid=rid, provider=None,
                                    region=None, zone=None,
                                    update_data=update_data,
                                    extend_info=data)

        res = {"id": rid, "resource_id": str(result.get("resource_id"))[:64],
               "ipaddress": result.get("ipaddress"),
               "cpu": result.get("cpu"),
               "memory": result.get("memory")}

        return res, result


class InstanceController(BackendController):
    allow_methods = ('GET', 'POST')
    resource = InstanceApi()

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

        validation.allowed_key(data, ["id", "provider", "region", 'resource_id',
                                      "provider_id", "name", "enabled",
                                      "hostname", "instance_type", "image",
                                      "cpu", "memory", "ipaddress",
                                      "disk_type", "disk_size", "power_state"])

        return self.resource.resource_object.list(filters=data, page=page,
                                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_key(data)
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return 1, res


class InstanceIdController(BackendIdController):
    allow_methods = ('GET', 'DELETE', 'PATCH')
    resource = InstanceApi()

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
        return self.resource.destroy(rid, force_delete=force_delete)

    def before_handler(self, request, data, **kwargs):
        ResBase.allow_upgrade_key(data)
        ResBase.validate_upgrade_keys(data)

    def create(self, request, data, **kwargs):
        res, _ = ResBase.update(resource=self.resource, data=data)
        return 1, res


class InstanceActionController(BackendIdController):
    allow_methods = ('PATCH',)
    resource = InstanceApi()

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["action"])
        validation.not_allowed_null(data=data,
                                    keys=["action"]
                                    )

        validation.validate_string("action", data["action"])

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        action = data.get("action", None)
        if action.lower() == "start":
            return self.resource.start(rid)
        elif action.lower() == "stop":
            return self.resource.stop(rid)
        else:
            raise local_exceptions.ValueValidateError("action", "VM 开关机操作，请使用合法值 start/stop")


class InstanceAddController(BaseController):
    allow_methods = ("POST",)
    resource = InstanceBackendApi()

    def before_handler(self, request, data, **kwargs):
        ResBase.not_null(data)
        ResBase.validate_keys(data)

    def response_templete(self, data):
        return {}

    def main_response(self, request, data, **kwargs):
        res, _ = ResBase.create(resource=self.resource, data=data)
        return res


class InstanceDeleteController(BaseController):
    name = "Instance"
    resource_describe = "Instance"
    allow_methods = ("POST",)
    resource = InstanceBackendApi()

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


class InstanceSourceController(BaseSourceController):
    name = "Instance"
    resource_describe = "Instance"
    allow_methods = ("POST",)
    resource = InstanceBackendApi()


class InstanceSGSourceController(BaseSourceController):
    name = "Instance"
    resource_describe = "Instance"
    allow_methods = ("POST",)
    resource = InstanceBackendApi()

    def fetch_source(self, rid, provider, region, zone, secret, resource_id):
        return self.resource.sg_vm_relationship(rid=rid, provider=provider,
                                                region=region, zone=zone,
                                                secret=secret,
                                                resource_id=resource_id)
