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
from apps.background.resource.loadbalance.lb import LBObject
from apps.background.resource.loadbalance.listener import LBListenerObject


class LBListenerApi(ApiBase):
    def __init__(self):
        super(LBListenerApi, self).__init__()
        self.resource_name = "lb_listener"
        self.resource_workspace = "lb_listener"
        self.resource_object = LBListenerObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, lb_id):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _lb_status = define_relations_key("lb_id", lb_id, resource_property.get("lb_id"))

        ext_info = {}
        if lb_id and (not _lb_status):
            ext_info["lb_id"] = LBObject().lb_resource_id(lb_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, name, lb_id, port, protocol,
                  backend_port, health_check, health_check_uri,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param name:
        :param lb_id:
        :param port:
        :param protocol:
        :param backend_port:
        :param health_check:
        :param health_check_uri:
        :param provider:
        :param provider_id:
        :param region:
        :param zone:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :return:
        '''

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "name": name, "status": status,
                                                 "lb_id": lb_id, "port": port,
                                                 "protocol": protocol,
                                                 "backend_port": backend_port,
                                                 "health_check": health_check,
                                                 "health_check_uri": health_check_uri,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

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

        name = name or "%s_%s" % (protocol, port)
        extend_info = extend_info or {}
        create_data = {"name": name, "port": port, "protocol": protocol,
                       "backend_port": backend_port, "health_check": health_check,
                       "health_check_uri": health_check_uri}
        label_name = self.resource_name + "_" + rid

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], lb_id)

        create_data.update(_relations_id_dict)
        define_json = self._generate_resource(provider_object["name"],
                                              label_name=label_name,
                                              data=create_data, extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(provider_info)
        define_json.update(output_json)

        _path = self.create_workpath(rid,
                                     provider=provider_object["name"],
                                     region=region)

        self.save_data(rid, name=name,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       lb_id=lb_id, port=port,
                       protocol=protocol,
                       health_check_uri=health_check_uri,
                       health_check=health_check,
                       backend_port=backend_port,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)

        self.init_workspace(_path, provider_object["name"])
        result = self.run(_path)

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        _update_data = {"status": "ok", "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        if not _update_data.get("resource_id"):
            _update_data["resource_id"] = self._fetch_id(result)

        _, res = self.update_data(rid, data=_update_data)

        return rid, res

    def destory(self, rid):
        '''

        :param rid:
        :return:
        '''
        # todo 校验lb listen是否挂载了后端应用
        resource_info = self.resource_object.show(rid)
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
