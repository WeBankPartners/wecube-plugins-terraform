# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.background.resource.database.kvstore import MemcachedObject
from .kvstore import KvStoreApi


class MemcachedApi(KvStoreApi):
    def __init__(self):
        super(MemcachedApi, self).__init__()
        self.resource_name = "memcached"
        self.resource_workspace = "memcached"
        self.resource_object = MemcachedObject()
