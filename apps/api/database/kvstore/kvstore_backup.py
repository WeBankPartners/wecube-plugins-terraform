# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi
from apps.background.resource.database.kvstore import KVStoreObject
from apps.background.resource.database.kvstore import KVStoreBackupObject


class KvBackupApi(ApiBase):
    def __init__(self):
        super(KvBackupApi, self).__init__()
        self.resource_name = "kvstore_backup"
        self.resource_workspace = "kvstore_backup"
        self.resource_object = KVStoreBackupObject()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, kvstore_id):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _kv_status = define_relations_key("kvstore_id", kvstore_id, resource_property.get("kvstore_id"))

        ext_info = {}
        if kvstore_id and (not _kv_status):
            ext_info["kvstore_id"] = KVStoreObject().object_resource_id(kvstore_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def save_data(self, rid, kvstore_id, backup_time, backup_period,
                  provider, provider_id, region, zone,
                  extend_info, define_json,
                  status, result_json):

        backup_period = ",".join(backup_period) if isinstance(backup_period, list) else str(backup_period)

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "region": region, "zone": zone,
                                                 "kvstore_id": kvstore_id,
                                                 "backup_time": backup_time,
                                                 "backup_period": backup_period,
                                                 "status": status,
                                                 "provider_id": provider_id,
                                                 "extend_info": json.dumps(extend_info),
                                                 "define_json": json.dumps(define_json),
                                                 "result_json": json.dumps(result_json)})

    def create(self, rid, provider_id,
               kvstore_id, backup_time, backup_period,
               zone, region, extend_info, **kwargs):
        '''

        :param rid:
        :param provider_id:
        :param kvstore_id:
        :param backup_time:
        :param backup_period:
        :param zone:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return _exists_data

        extend_info = extend_info or {}
        create_data = {"backup_time": backup_time, "backup_period": backup_period}

        label_name = self.resource_name + "_" + rid

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], kvstore_id)

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

        self.save_data(rid, kvstore_id=kvstore_id,
                       backup_time=backup_time,
                       backup_period=backup_period,
                       provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying", result_json={})

        self.write_define(rid, _path, define_json=define_json)
        self.init_workspace(_path, provider_object["name"])

        try:
            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            raise e

        result = self.formate_result(result)
        logger.info(format_json_dumps(result))
        resource_id = self._fetch_id(result)

        _update_data = {"status": "ok",
                        "resource_id": resource_id,
                        "result_json": format_json_dumps(result)}
        _update_data.update(self._read_output_result(result))

        return self.update_data(rid, data=_update_data)

    def destory(self, rid, force_delete=False):
        '''

        :param rid:
        :param force_delete:
        :return:
        '''

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

        return self.resource_object.delete(rid, update_data={"status": "deleted"})
