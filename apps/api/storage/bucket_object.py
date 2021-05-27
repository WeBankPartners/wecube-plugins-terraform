# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import define_relations_key
from apps.common.convert_keys import convert_extend_propertys
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase_backend import ApiBackendBase


class BucketObjectApi(ApiBase):
    def __init__(self):
        super(BucketObjectApi, self).__init__()
        self.resource_name = "bucket_object"
        self.resource_workspace = "bucket_object"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param vpc_id:
        :return:
        '''

        bucket_id = create_data.get("bucket_id")

        self.resource_info(provider)
        resource_property = self.resource_keys_config["resource_property"]
        _bucket_status = define_relations_key("bucket_id", bucket_id, resource_property.get("bucket_id"))

        ext_info = {}
        if bucket_id and (not _bucket_status):
            ext_info["bucket_id"] = CrsObject("object_storage").object_resource_id(bucket_id)

        logger.info("before_keys_checks add info: %s" % (format_json_dumps(ext_info)))
        return ext_info

    def _generate_resource(self, provider, label_name, data, extend_info):
        '''
        转换resource 资源属性， 生成配置
        :param provider:
        :param label_name: 资源的标签名称
        :param data:
        :param extend_info:
        :return:
        '''

        self.resource_info(provider)
        resource_values_config = self.values_config(provider)

        resource_name = self.resource_keys_config["resource_type"]
        resource_property = self.resource_keys_config["resource_property"]
        resource_extend_info = self.resource_keys_config["extend_info"]

        resource_columns = {}
        for key, value in data.items():
            if resource_values_config.get(key):
                _values_configs = resource_values_config.get(key)
                value = convert_value(value, _values_configs.get(value))

            resource_columns[key] = value

        resource_columns = convert_keys(resource_columns, defines=resource_property)
        _extend_columns = convert_extend_propertys(datas=extend_info, extend_info=resource_extend_info)
        resource_columns.update(_extend_columns)

        _info = {
            "resource": {
                resource_name: {
                    label_name: resource_columns
                }
            }
        }

        if "content" in data.keys():
            logger.info("%s include content may too long, not print in log, please check it in file" % label_name)
        else:
            logger.info(format_json_dumps(_info))
        return _info

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {"bucket_id": create_data.get("bucket_id")}

        content = create_data.get("content")
        source = create_data.get("source")
        x_create_data = {"key": create_data.get("key")}
        if content:
            x_create_data["context"] = content
        if source:
            x_create_data["source"] = source

        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None

    def destroy(self, rid):
        '''

        :param rid:
        :return:
        '''

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


class BucketObjectBackendApi(ApiBackendBase):
    def __init__(self):
        super(BucketObjectBackendApi, self).__init__()
        self.resource_name = "bucket_object"
        self.resource_workspace = "bucket_object"
        self._flush_resobj()
        self.resource_keys_config = None
