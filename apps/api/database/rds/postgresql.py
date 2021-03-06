# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.background.resource.database.rds import PostgreSQLObject
from apps.api.database.rds import RdsDBApi


class PostgreSQLApi(RdsDBApi):
    def __init__(self):
        super(PostgreSQLApi, self).__init__()
        self.resource_name = "postgreSQL"
        self.resource_workspace = "postgreSQL"
        self.resource_object = PostgreSQLObject()

