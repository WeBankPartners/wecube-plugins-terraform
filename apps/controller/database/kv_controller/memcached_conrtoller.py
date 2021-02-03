# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
from core import local_exceptions
from lib.uuid_util import get_uuid
from apps.api.database.kvstore.memcached import MemcachedApi
from apps.api.database.kvstore.memcached import MemcachedBackupApi
from .kvstore_controller import KvStoreController
from .kvstore_controller import KvStoreIdController
from .kvstore_controller import KvStoreAddController
from .kvstore_controller import KvStoreDeleteController
from .kvstore_backup_controller import KvBackupController
from .kvstore_backup_controller import KvBackupIdController
from .kvstore_backup_controller import KvBackupAddController
from .kvstore_backup_controller import KvBackupDeleteController


class MemcachedController(KvStoreController):
    allow_methods = ('GET', 'POST')
    resource = MemcachedApi()


class MemcachedIdController(KvStoreIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = MemcachedApi()


class MemcachedAddController(KvStoreAddController):
    allow_methods = ("POST",)
    resource = MemcachedApi()


class MemcachedDeleteController(KvStoreDeleteController):
    name = "Memcached"
    resource_describe = "Memcached"
    allow_methods = ("POST",)
    resource = MemcachedApi()


class MemBackupController(KvBackupController):
    allow_methods = ('GET', 'POST')
    resource = MemcachedBackupApi()

    def keyname(self):
        return "memcached_id"


class MemBackupIdController(KvBackupIdController):
    allow_methods = ('GET', 'DELETE',)
    resource = MemcachedBackupApi()


class MemBackupAddController(KvBackupAddController):
    allow_methods = ("POST",)
    resource = MemcachedBackupApi()

    def keyname(self):
        return "memcached_id"


class MemBackupDeleteController(KvBackupDeleteController):
    name = "MemBackup"
    resource_describe = "MemBackup"
    allow_methods = ("POST",)
    resource = MemcachedBackupApi()
