# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

# from apps.background.resource.database.rds import PostgreSQLObject
from apps.api.database.rds.rds import RdsDBApi
from apps.api.database.rds.rds import RdsDBBackendApi


class PostgreSQLApi(RdsDBApi):
    def __init__(self):
        super(PostgreSQLApi, self).__init__()
        self.resource_name = "postgreSQL"
        self.resource_workspace = "postgreSQL"
        self.relation_resource = "subnet"
        self._flush_resobj()
        self.resource_keys_config = None


class PostgreSQLBackendApi(RdsDBBackendApi):
    def __init__(self):
        super(PostgreSQLBackendApi, self).__init__()
        self.resource_name = "postgreSQL"
        self.resource_workspace = "postgreSQL"
        self.relation_resource = "subnet"
        self._flush_resobj()
        self.resource_keys_config = None
