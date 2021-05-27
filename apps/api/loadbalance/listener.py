# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase_backend import ApiBackendBase


class LBListenerApi(ApiBase):
    def __init__(self):
        super(LBListenerApi, self).__init__()
        self.resource_name = "lb_listener"
        self.resource_workspace = "lb_listener"
        self.owner_resource = "lb"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        lb_id = create_data.get("lb_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _lb_status = define_relations_key("lb_id", lb_id, resource_property.get("lb_id"))

        ext_info = {}
        if lb_id and (not _lb_status):
            ext_info["lb_id"] = CrsObject(self.owner_resource).object_resource_id(lb_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"lb_id": create_data.get("lb_id")}

        name = create_data.get("name")
        protocol = create_data.get("protocol")
        port = create_data.get("port")
        name = name or "%s_%s" % (protocol, port)

        x_create_data = {"name": name, "port": port, "protocol": protocol,
                         "backend_port": create_data.get("backend_port"),
                         "health_check": create_data.get("health_check"),
                         "health_check_uri": create_data.get("health_check_uri")}

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = create_data.get("lb_id")
        return owner_id, None

    def destroy(self, rid):
        '''

        :param rid:
        :return:
        '''
        # todo 校验lb listen是否挂载了后端应用
        resource_info = self.resource_object.show(rid)
        if not resource_info:
            return 0
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        if not self.destroy_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        status = self.run_destroy(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)


class LBListenerBackendApi(ApiBackendBase):
    def __init__(self):
        super(LBListenerBackendApi, self).__init__()
        self.resource_name = "lb_listener"
        self.resource_workspace = "lb_listener"
        self.owner_resource = "lb"
        self._flush_resobj()
        self.resource_keys_config = None
