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
from apps.background.resource.database.rds import MysqlObject
from apps.background.resource.database.rds import MysqlAccountObject
from apps.background.resource.database.rds import MysqlPrivilegeObject
from apps.api.apibase import ApiBase


class MysqlAccountApi(ApiBase):
    def __init__(self):
        super(MysqlAccountApi, self).__init__()
        self.resource_name = "mysql_account"
        self.resource_workspace = "mysql_account"
        self.resource_object = MysqlAccountObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, mysql_id):
        '''

        :param provider:
        :param mysql_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _mysql_status = define_relations_key("mysql_id", mysql_id, resource_property.get("mysql_id"))

        ext_info = {}
        if mysql_id and (not _mysql_status):
            ext_info["mysql_id"] = MysqlObject().object_resource_id(mysql_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, mysql_id, username, password,
                  provider, region, extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param mysql_id:
        :param username:
        :param password:
        :param provider:
        :param region:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

        password = base64.b64encode(password) if password else password
        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region,
                                                 "rds_id": mysql_id,
                                                 "name": username,
                                                 "password": password,
                                                 "status": status,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, name, provider_id,
               mysql_id, password,
               zone, region, extend_info, **kwargs):

        '''

        :param rid:
        :param name:
        :param provider_id:
        :param mysql_id:
        :param password:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return _exists_data

        password = password or "Terraform.123"
        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid
        create_data = {"name": name, "password": password}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], mysql_id)

        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"],
                                              label_name=label_name,
                                              data=create_data,
                                              extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, region=region, mysql_id=mysql_id,
                       username=name, password=password,
                       provider=provider_object["name"],
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


class MysqlPrivilegeApi(ApiBase):
    def __init__(self):
        super(MysqlPrivilegeApi, self).__init__()
        self.resource_name = "mysql_privilege"
        self.resource_workspace = "mysql_privilege"
        self.resource_object = MysqlPrivilegeObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, mysql_id):
        '''

        :param provider:
        :param mysql_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _mysql_status = define_relations_key("mysql_id", mysql_id, resource_property.get("mysql_id"))

        ext_info = {}
        if mysql_id and (not _mysql_status):
            ext_info["mysql_id"] = MysqlObject().object_resource_id(mysql_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, mysql_id,
                  username, database, privileges,
                  provider, region, extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param mysql_id:
        :param username:
        :param password:
        :param provider:
        :param region:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

        if isinstance(privileges, dict):
            privileges = json.dumps(privileges)
        else:
            privileges = str(privileges)

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region,
                                                 "rds_id": mysql_id,
                                                 "account_name": username,
                                                 "database": database,
                                                 "privileges": privileges,
                                                 "status": status,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

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

    def create(self, rid, username, provider_id,
               mysql_id, database, privileges,
               zone, region, extend_info, **kwargs):

        '''

        :param rid:
        :param username:
        :param provider_id:
        :param mysql_id:
        :param database:
        :param privileges:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid
        create_data = {"username": username}

        MysqlAccountObject().query_account(username=username, where_data={"rds_id": mysql_id})
        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], mysql_id)

        create_data.update(self.format_privilege(provider=provider_object["name"],
                                                 database=database,
                                                 privileges=privileges))

        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"],
                                              label_name=label_name,
                                              data=create_data,
                                              extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, region=region, mysql_id=mysql_id,
                       username=username, database=database,
                       privileges=privileges,
                       provider=provider_object["name"],
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
