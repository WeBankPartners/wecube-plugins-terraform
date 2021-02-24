# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.background.resource.database.rds import MariaDBObject
from apps.api.database.rds.rds import RdsDBApi


class MariaDBApi(RdsDBApi):
    def __init__(self):
        super(MariaDBApi, self).__init__()
        self.resource_name = "mariadb"
        self.resource_workspace = "mariadb"
        self.resource_object = MariaDBObject()
