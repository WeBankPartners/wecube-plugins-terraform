# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from .kvstore import KvStoreApi
from .kvstore_backup import KvBackupApi
from apps.background.resource.resource_base import CrsObject


class RedisApi(KvStoreApi):
    def __init__(self):
        super(RedisApi, self).__init__()
        self.resource_name = "redis"
        self.resource_workspace = "redis"
        self._flush_resobj()


class RedisBackupApi(KvBackupApi):
    def __init__(self):
        super(RedisBackupApi, self).__init__()
        self.resource_name = "redis_backup"
        self.resource_workspace = "redis_backup"
        self._flush_resobj()

    def before_keys_checks(self, provider, kvstore_id, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _kv_status = define_relations_key("redis_id", kvstore_id, resource_property.get("redis_id"))

        ext_info = {}
        if kvstore_id and (not _kv_status):
            ext_info["redis_id"] = CrsObject("redis").object_resource_id(kvstore_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info
