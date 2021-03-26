# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import validate_type
from apps.common.convert_keys import convert_extend_propertys
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.background.resource.vm.instance_type import InstanceTypeObject
from apps.background.resource.resource_base import CrsObject
from apps.api.conductor.provider import ProviderConductor
from apps.api.apibase_backend import ApiBackendBase


class Common(object):

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        vpc_id = create_data.get("vpc_id")
        subnet_id = create_data.get("subnet_id")
        sg_id = create_data.get("security_group_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _subnet_status = define_relations_key("subnet_id", subnet_id, resource_property.get("subnet_id"))
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _sg_status = define_relations_key("security_group_id", sg_id, resource_property.get("security_group_id"))

        ext_info = {}
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = CrsObject("subnet").object_resource_id(subnet_id)
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = CrsObject("vpc").object_resource_id(vpc_id)
        if sg_id and (not _sg_status):
            sg_property = resource_property.get("security_group_id")
            if isinstance(sg_property, dict):
                if sg_property.get("type", "string") == "list":
                    sg_list = validate_type(sg_id, "list")
                    _sg_resource_ids = []
                    for _sg in sg_list:
                        _sg_resource_ids.append(CrsObject("security_group").object_resource_id(_sg))
                else:
                    _sg_resource_ids = CrsObject("security_group").object_resource_id(sg_id)

                ext_info["security_group_id"] = _sg_resource_ids
            else:
                ext_info["security_group_id"] = CrsObject("security_group").object_resource_id(sg_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"vpc_id": create_data.get("vpc_id"),
                         "subnet_id": create_data.get("subnet_id"),
                         "security_group_id": create_data.get("security_group_id")}

        password = create_data.get("password")
        x_create_data = {"name": create_data.get("name"),
                         "engine": self.resource_name, "zone": zone,
                         "version": create_data.get("version"),
                         "port": create_data.get("port"),
                         "instance_type": create_data.get("instance_type")
                         }

        if password:
            x_create_data["password"] = password

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        return None, None


class KvStoreApi(Common, ApiBase):
    def __init__(self):
        super(KvStoreApi, self).__init__()
        self.resource_name = "kvstore"
        self.resource_workspace = "kvstore"
        self._flush_resobj()
        self.resource_keys_config = None

    def create(self, rid, provider, region, zone, secret,
               create_data, extend_info, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param zone:
        :param secret:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        zone = ProviderConductor().zone_info(provider=provider_object["name"], zone=zone)
        x_create_data, r_create_data = self.generate_create_data(zone, create_data,
                                                                 provider=provider_object["name"])

        origin_type, instance_type_data = InstanceTypeObject().convert_resource_id(provider_object.get("id"),
                                                                                   create_data.get("instance_type"))

        x_create_data["instance_type"] = origin_type
        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

        x_create_data.update(_relations_id_dict)

        owner_id, relation_id = self.generate_owner_data(create_data)
        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=owner_id, relation_id=relation_id,
                                     create_data=x_create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res


class KvStoreBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(KvStoreBackendApi, self).__init__()
        self.resource_name = "kvstore"
        self.resource_workspace = "kvstore"
        self._flush_resobj()
        self.resource_keys_config = None

    def apply(self, rid, provider, region, zone, secret,
              create_data, extend_info,
              asset_id=None, resource_id=None,
              **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param secret:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        extend_info = extend_info or {}
        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        zone = ProviderConductor().zone_info(provider=provider_object["name"], zone=zone)
        x_create_data, r_create_data = self.generate_create_data(zone, create_data,
                                                                 provider=provider_object["name"])

        origin_type, instance_type_data = InstanceTypeObject().convert_resource_id(provider_object.get("id"),
                                                                                   create_data.get("instance_type"))

        x_create_data["instance_type"] = origin_type
        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

        x_create_data.update(_relations_id_dict)

        owner_id, relation_id = self.generate_owner_data(create_data)
        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     asset_id=asset_id, resource_id=resource_id,
                                     owner_id=owner_id, relation_id=relation_id,
                                     create_data=x_create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
