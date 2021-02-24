# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.api.configer.provider import ProviderApi
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import convert_key_only
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject


class MysqlAccountApi(ApiBase):
    def __init__(self):
        super(MysqlAccountApi, self).__init__()
        self.resource_name = "mysql_account"
        self.resource_workspace = "mysql_account"
        self.owner_resource = "mysql"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param mysql_id:
        :return:
        '''

        mysql_id = create_data.get("mysql_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _mysql_status = define_relations_key("mysql_id", mysql_id, resource_property.get("mysql_id"))

        ext_info = {}
        if mysql_id and (not _mysql_status):
            ext_info["mysql_id"] = CrsObject("mysql").object_resource_id(mysql_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"mysql_id": create_data.get("mysql_id")}

        password = create_data.get("password") or "Terraform.123"
        x_create_data = {"password": password,
                         "name": create_data.get("name")}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = create_data.get("mysql_id")
        return owner_id, None


class MysqlPrivilegeApi(ApiBase):
    def __init__(self):
        super(MysqlPrivilegeApi, self).__init__()
        self.resource_name = "mysql_privilege"
        self.resource_workspace = "mysql_privilege"
        self.owner_resource = "mysql"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
        '''

        :param provider:
        :param mysql_id:
        :return:
        '''
        mysql_id = create_data.get("mysql_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _mysql_status = define_relations_key("mysql_id", mysql_id, resource_property.get("mysql_id"))

        ext_info = {}
        if mysql_id and (not _mysql_status):
            ext_info["mysql_id"] = CrsObject("mysql").object_resource_id(mysql_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def format_privilege(self, provider, database, privileges):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        resource_values_config = self.values_config(provider)

        _columns_status = define_relations_key("database_columns", "00000", resource_property.get("database_columns"))

        ext_info = {}
        if _columns_status:
            ext_info["database"] = database
            ext_info["privileges"] = privileges
        else:
            tmp_dict = {"database": database, "privileges": privileges}
            resource_columns = {}
            for key, value in tmp_dict.items():
                if resource_values_config.get(key):
                    _values_configs = resource_values_config.get(key)
                    value = convert_value(value, _values_configs.get(value))

                resource_columns[key] = value

            resource_columns = convert_keys(resource_columns, defines=resource_property, is_update=True)
            database_columns = convert_key_only("database_columns",
                                                define=resource_property.get("database_columns", "database_columns"))

            ext_info = {database_columns: [resource_columns]}

        logger.info("format_privilege add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"mysql_id": create_data.get("mysql_id")}

        database = create_data.get("database")
        privileges = create_data.get("privileges")
        x_create_data = {"username": create_data.get("username")}

        x_create_data.update(self.format_privilege(provider=kwargs.get("provider"),
                                                   database=database,
                                                   privileges=privileges))

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = create_data.get("mysql_id")
        return owner_id, None
