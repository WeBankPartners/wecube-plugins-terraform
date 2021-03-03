# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from .kvstore import KvStoreApi
from .kvstore_backup import KvBackupApi
from apps.background.resource.resource_base import CrsObject


class MemcachedApi(KvStoreApi):
    def __init__(self):
        super(MemcachedApi, self).__init__()
        self.resource_name = "memcached"
        self.resource_workspace = "memcached"
        self._flush_resobj()


class MemcachedBackupApi(KvBackupApi):
    def __init__(self):
        super(MemcachedBackupApi, self).__init__()
        self.resource_name = "memcached_backup"
        self.resource_workspace = "memcached_backup"
        self._flush_resobj()

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        kvstore_id = create_data.get("kvstore_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _kv_status = define_relations_key("memcached_id", kvstore_id, resource_property.get("memcached_id"))

        ext_info = {}
        if kvstore_id and (not _kv_status):
            ext_info["memcached_id"] = CrsObject("memcached").object_resource_id(kvstore_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info
