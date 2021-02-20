# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.background.resource.database.nosql import MongoDBObject
from apps.api.database.nosql.nosql import NosqlApi


class MongodbApi(NosqlApi):
    def __init__(self):
        super(MongodbApi, self).__init__()
        self.resource_name = "mongodb"
        self.resource_workspace = "mongodb"
        self.resource_object = MongoDBObject()
