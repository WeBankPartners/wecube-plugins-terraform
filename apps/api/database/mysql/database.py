# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
from core import local_exceptions
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.api.configer.provider import ProviderApi
from apps.common.convert_keys import define_relations_key
from apps.background.resource.database.rds import MysqlObject
from apps.background.resource.database.rds import MysqlDatabaseObject
from apps.api.apibase import ApiBase


class MysqlDatabaseApi(ApiBase):
    def __init__(self):
        super(MysqlDatabaseApi, self).__init__()
        self.resource_name = "mysql_database"
        self.resource_workspace = "mysql_database"
        self.resource_object = MysqlDatabaseObject()
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

    def save_data(self, rid, mysql_id, name,
                  provider, region, extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param mysql_id:
        :param name:
        :param password:
        :param provider:
        :param region:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region,
                                                 "rds_id": mysql_id,
                                                 "name": name,
                                                 "status": status,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def check_database(self, mysql_id, database):
        _exists_data = MysqlDatabaseObject().query_one(where_data={"name": database, "rds_id": mysql_id})
        if _exists_data:
            raise local_exceptions.ResourceValidateError("database name", "database %s already exists" % database)

    def create(self, rid, name, provider_id, mysql_id,
               zone, region, extend_info, **kwargs):

        '''

        :param rid:
        :param name:
        :param provider_id:
        :param mysql_id:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid
        create_data = {"name": name}

        self.check_database(mysql_id, name)
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

        self.save_data(rid, region=region,
                       name=name, mysql_id=mysql_id,
                       provider=provider_object["name"],
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data = {"status": "ok", "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        if not _update_data.get("resource_id"):
            _update_data["resource_id"] = self._fetch_id(result)

        self.update_data(rid, data=_update_data)
        return rid
