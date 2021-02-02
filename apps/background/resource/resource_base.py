# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)


class ResourceBaseObject(object):
    resource = None

    def ora_show(self, rid, where_data=None):
        where_data = where_data or {}
        where_data.update({"id": rid})
        return self.resource.get(filters=where_data)

    def ora_delete(self, rid):
        return self.resource.delete(filters={"id": rid})
