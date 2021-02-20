# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
from core import local_exceptions
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.api.configer.provider import ProviderApi
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject


class MysqlDatabaseApi(ApiBase):
    def __init__(self):
        super(MysqlDatabaseApi, self).__init__()
        self.resource_name = "mysql_database"
        self.resource_workspace = "mysql_database"
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

        x_create_data = {"name": create_data.get("name")}
        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = create_data.get("mysql_id")
        return owner_id, None
