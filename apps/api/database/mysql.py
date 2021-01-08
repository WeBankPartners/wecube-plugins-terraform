# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.background.resource.database.rds import MysqlObject
from .rds import RdsDBApi


class MysqlApi(RdsDBApi):
    def __init__(self):
        super(MysqlApi, self).__init__()
        self.resource_name = "mysql"
        self.resource_workspace = "mysql"
        self.resource_object = MysqlObject()

