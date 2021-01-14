# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.background.resource.database.kvstore import RedisObject
from .kvstore import KvStoreApi


class RedisApi(KvStoreApi):
    def __init__(self):
        super(RedisApi, self).__init__()
        self.resource_name = "redis"
        self.resource_workspace = "redis"
        self.resource_object = RedisObject()
