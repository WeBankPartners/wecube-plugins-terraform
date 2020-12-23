# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.uuid_util import get_uuid
from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from core import local_exceptions as exception_common
from apps.api.configer.commonkey import CommonKeyObject



class CommonKeyController(BackendController):
    resource = CommonKeyObject()

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        '''

        :param request:
        :param data:
        :param orderby:
        :param page:
        :param pagesize:
        :param kwargs:
        :return:
        '''

        validation.allowed_key(data, ["id", "resource", "key", "enabled"])
        return self.resource.list(filters=data, page=page,
                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        validation.allowed_key(data, ["id", "resource", "key", "property"])
        validation.not_allowed_null(data=data,
                                    keys=["resource", "key", "property"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("resource", data["resource"])
        validation.validate_string("key", data.get("key"))
        validation.validate_string("property", data.get("property"))


    def create(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''
        create_data = {"id": data.get("id") or get_uuid(),
                       "resource": data["resource"],
                       "key": data.get("key"),
                       "property": data.get("property")
                       }

        return self.resource.create(create_data)


class CommonKeyIdController(BackendIdController):
    resource = CommonKeyObject()

    def show(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        return self.resource.show(rid)

    def before_handler(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        validation.allowed_key(data, ["resource", "key", "property", "enabled"])

        validation.validate_string("resource", data["resource"])
        validation.validate_string("key", data.get("key"))
        validation.validate_string("property", data.get("property"))
        validation.validate_bool("enabled", data.get("enabled"))

    def update(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)

        return self.resource.update(rid, data)

    def delete(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''

        rid = kwargs.pop("rid", None)
        return self.resource.delete(rid)


