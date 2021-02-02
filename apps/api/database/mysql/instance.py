# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.convert_keys import validate_type
from apps.common.convert_keys import convert_key_only
from apps.api.configer.provider import ProviderApi
from apps.background.resource.network.security_group import SecGroupObject
from apps.background.resource.network.vpc import VpcObject
from apps.background.resource.network.subnet import SubnetObject
from apps.common.convert_keys import define_relations_key
from apps.background.resource.database.rds import MysqlObject
from apps.background.resource.vm.instance_type import InstanceTypeObject
from apps.api.database.rds import RdsDBApi


class MysqlApi(RdsDBApi):
    def __init__(self):
        super(MysqlApi, self).__init__()
        self.resource_name = "mysql"
        self.resource_workspace = "mysql"
        self.resource_object = MysqlObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, vpc_id, subnet_id, sg_id):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _subnet_status = define_relations_key("subnet_id", subnet_id, resource_property.get("subnet_id"))
        _vpc_status = define_relations_key("vpc_id", vpc_id, resource_property.get("vpc_id"))
        _sg_status = define_relations_key("security_group_id", sg_id, resource_property.get("security_group_id"))

        ext_info = {}
        if subnet_id and (not _subnet_status):
            ext_info["subnet_id"] = SubnetObject().subnet_resource_id(subnet_id)
        if vpc_id and (not _vpc_status):
            ext_info["vpc_id"] = VpcObject().vpc_resource_id(vpc_id)
        if sg_id and (not _sg_status):
            sg_property = resource_property.get("security_group_id")
            if isinstance(sg_property, dict):
                if sg_property.get("type", "string") == "list":
                    sg_list = validate_type(sg_id, "list")
                    _sg_resource_ids = []
                    for _sg in sg_list:
                        _sg_resource_ids.append(SecGroupObject().resource_id(_sg))
                else:
                    _sg_resource_ids = SecGroupObject().resource_id(sg_id)

                ext_info["security_group_id"] = _sg_resource_ids
            else:
                ext_info["security_group_id"] = SecGroupObject().resource_id(sg_id)

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
            return _exists_data

        extend_info = extend_info or {}
        password = password or "Terraform.123"
        label_name = self.resource_name + "_" + rid
        create_data = {"name": name, "engine": self.resource_name, "zone": zone,
                       "version": version, "instance_type": instance_type,
                       "first_slave_zone": first_slave_zone,
                       "second_slave_zone": second_slave_zone,
                       "password": password, "user": user, "port": port,
                       "disk_type": disk_type, "disk_size": disk_size}

        origin_type, instance_type_data = InstanceTypeObject().type_resource_id(provider_id, instance_type)
        cpu = instance_type_data.get("cpu")
        memory = instance_type_data.get("memory")

        create_data["instance_type"] = origin_type
        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], vpc_id,
                                                     subnet_id, security_group_id)

        create_data.update(self._generate_slave_zone(provider=provider_object["name"],
                                                     first_slave_zone=first_slave_zone,
                                                     second_slave_zone=second_slave_zone))
        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"],
                                              label_name=label_name,
                                              data=create_data, extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       subnet_id=subnet_id, version=version,
                       instance_type=instance_type,
                       port=port, password=password,
                       user=user, disk_type=disk_type,
                       disk_size=disk_size,
                       cpu=cpu, memory=memory,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)

        self.init_workspace(_path, provider_object["name"])

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data = {"status": "ok", "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        if not _update_data.get("resource_id"):
            _update_data["resource_id"] = self._fetch_id(result)

        _, result = self.update_data(rid, data=_update_data)

        return rid, result
