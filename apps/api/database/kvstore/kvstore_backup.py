# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase_backend import ApiBackendBase


class KvBackupApi(ApiBase):
    def __init__(self):
        super(KvBackupApi, self).__init__()
        self.resource_name = "kvstore_backup"
        self.resource_workspace = "kvstore_backup"
        self.relation_resource = "kvstore"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        kvstore_id = create_data.get("kvstore_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _kv_status = define_relations_key("kvstore_id", kvstore_id, resource_property.get("kvstore_id"))

        ext_info = {}
        if kvstore_id and (not _kv_status):
            ext_info["kvstore_id"] = CrsObject("kvstore").object_resource_id(kvstore_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"kvstore_id": create_data.get("kvstore_id")}

        x_create_data = {"backup_period": create_data.get("backup_period"),
                         "backup_time": create_data.get("backup_time")}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = create_data.get("kvstore_id")
        return owner_id, None


class KvBackupBackendApi(ApiBackendBase):
    def __init__(self):
        super(KvBackupBackendApi, self).__init__()
        self.resource_name = "kvstore_backup"
        self.resource_workspace = "kvstore_backup"
        self.relation_resource = "kvstore"
        self._flush_resobj()
        self.resource_keys_config = None
