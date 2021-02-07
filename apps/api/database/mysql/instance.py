# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.convert_keys import validate_type
from apps.common.convert_keys import convert_key_only
from apps.api.configer.provider import ProviderApi
from apps.common.convert_keys import define_relations_key
from apps.background.resource.vm.instance_type import InstanceTypeObject
from apps.api.database.rds.rds import RdsDBApi
from apps.background.resource.resource_base import CrsObject


class MysqlApi(RdsDBApi):
    def __init__(self):
        super(MysqlApi, self).__init__()
        self.resource_name = "mysql"
        self.resource_workspace = "mysql"
        self.relation_resource = "subnet"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
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

    def zone_info(self, provider, zone):
        return ProviderApi().zone_info(provider, zone)

    def _generate_slave_zone(self, provider, first_slave_zone, second_slave_zone):
        create_data = {}
        if first_slave_zone:
            create_data["first_slave_zone"] = self.zone_info(provider, first_slave_zone)
        if second_slave_zone:
            create_data["second_slave_zone"] = self.zone_info(provider, second_slave_zone)

        logger.info("_generate_slave_zone format json: %s" % (format_json_dumps(create_data)))
        return create_data

    def create(self, rid, name, provider_id, version,
               instance_type, subnet_id, port, password,
               user, disk_type, disk_size,
               vpc_id, security_group_id,
               first_slave_zone, second_slave_zone,
               zone, region, extend_info, **kwargs):

        '''

        :param rid:
        :param name:
        :param provider_id:
        :param version:
        :param instance_type:
        :param subnet_id:
        :param port:
        :param password:
        :param user:
        :param disk_type:
        :param disk_size:
        :param vpc_id:
        :param security_group_id:
        :param first_slave_zone:
        :param second_slave_zone:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        password = password or "Terraform.123"

        create_data = {"name": name, "engine": self.resource_name, "zone": zone,
                       "version": version, "instance_type": instance_type,
                       "first_slave_zone": first_slave_zone,
                       "second_slave_zone": second_slave_zone,
                       "password": password, "user": user, "port": port,
                       "disk_type": disk_type, "disk_size": disk_size}

        _r_create_data = {"vpc_id": vpc_id, "subnet_id": subnet_id,
                          "security_group_id": security_group_id}

        origin_type, instance_type_data = InstanceTypeObject().type_resource_id(provider_id, instance_type)
        cpu = instance_type_data.get("cpu")
        memory = instance_type_data.get("memory")

        create_data["instance_type"] = origin_type
        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        create_data.update(self._generate_slave_zone(provider=provider_object["name"],
                                                     first_slave_zone=first_slave_zone,
                                                     second_slave_zone=second_slave_zone))

        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=vpc_id,
                                     relation_id=subnet_id,
                                     create_data=create_data,
                                     extend_info=extend_info,
                                     cpu=cpu, memory=memory,
                                     **kwargs)

        return count, res
