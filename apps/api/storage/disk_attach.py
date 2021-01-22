# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.configer.provider import ProviderApi
from apps.api.apibase import ApiBase
from apps.background.resource.storage.disk import DiskObject
from apps.background.resource.storage.disk import DiskAttachObject
from apps.background.resource.vm.instance import InstanceObject


class DiskAttachApi(ApiBase):
    def __init__(self):
        super(DiskAttachApi, self).__init__()
        self.resource_name = "disk_attach"
        self.resource_workspace = "disk_attach"
        self.resource_object = DiskAttachObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, instance_id, disk_id):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _instance_status = define_relations_key("instance_id", instance_id, resource_property.get("instance_id"))
        _disk_status = define_relations_key("disk_id", disk_id, resource_property.get("disk_id"))

        ext_info = {}
        if instance_id and (not _instance_status):
            ext_info["instance_id"] = InstanceObject().vm_resource_id(instance_id)
        if disk_id and (not _disk_status):
            ext_info["disk_id"] = DiskObject().disk_resource_id(disk_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, name, disk, instance,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):
        '''

        :param rid:
        :param name:
        :param disk:  disk id
        :param instance:  instance id
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
                                                 "name": name, "disk_id": disk,
                                                 "instance_id": instance, "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def attach(self, rid, name, provider_id,
               disk_id, instance_id,
               zone, region, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param disk_id:
        :param instance_id:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        extend_info = extend_info or {}
        create_data = {}
        label_name = self.resource_name + "_" + rid

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], instance_id, disk_id)

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
                       disk=disk_id, instance=instance_id,
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

        return self.update_data(rid, data=_update_data)

    def detach(self, rid):
        '''

        :param rid:
        :return:
        '''

        resource_info = self.resource_object.show(rid)
        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        if not self.destory_ensure_file(rid, path=_path):
            self.write_define(rid, _path, define_json=resource_info["define_json"])

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="disk detach %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)

