# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
from core import local_exceptions
from lib.uuid_util import get_uuid
from apps.api.database.kvstore.redis import RedisApi
from apps.api.database.kvstore.redis import RedisBackupApi
from .kvstore_controller import KvStoreController
from .kvstore_controller import KvStoreIdController
from .kvstore_controller import KvStoreAddController
from .kvstore_controller import KvStoreDeleteController
from .kvstore_backup_controller import KvBackupController
from .kvstore_backup_controller import KvBackupIdController
from .kvstore_backup_controller import KvBackupAddController
from .kvstore_backup_controller import KvBackupDeleteController


class RedisController(KvStoreController):
    allow_methods = ('GET', 'POST')
    resource = RedisApi()


class RedisIdController(KvStoreIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = RedisApi()


class RedisAddController(KvStoreAddController):
    allow_methods = ("POST",)
    resource = RedisApi()


class RedisDeleteController(KvStoreDeleteController):
    name = "Redis"
    resource_describe = "Redis"
    allow_methods = ("POST",)
    resource = RedisApi()


class RedisBackupController(KvBackupController):
    allow_methods = ('GET', 'POST')
    resource = RedisBackupApi()

    def keyname(self):
        return "redis_id"


class RedisBackupIdController(KvBackupIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = RedisBackupApi()


class RedisBackupAddController(KvBackupAddController):
    allow_methods = ("POST",)
    resource = RedisBackupApi()

    def keyname(self):
        return "redis_id"


class RedisBackupDeleteController(KvBackupDeleteController):
    name = "RedisBackup"
    resource_describe = "RedisBackup"
    allow_methods = ("POST",)
    resource = RedisBackupApi()
