# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.background.resource.resource_base import CrsObject


class LBListenerApi(ApiBase):
    def __init__(self):
        super(LBListenerApi, self).__init__()
        self.resource_name = "lb_listener"
        self.resource_workspace = "lb_listener"
        self.owner_resource = "lb"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data):
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

    def create(self, rid, name, provider_id,
               lb_id, port, protocol, backend_port,
               health_check, health_check_uri,
               zone, region, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param lb_id:
        :param port:
        :param protocol:
        :param backend_port:
        :param health_check:
        :param health_check_uri:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        name = name or "%s_%s" % (protocol, port)
        extend_info = extend_info or {}
        create_data = {"name": name, "port": port, "protocol": protocol,
                       "backend_port": backend_port, "health_check": health_check,
                       "health_check_uri": health_check_uri}

        _r_create_data = {"lb_id": lb_id}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], _r_create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=lb_id,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res

    def destory(self, rid):
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

        if not self.destory_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)
