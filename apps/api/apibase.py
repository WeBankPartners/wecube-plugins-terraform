# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.convert_keys import read_output
from apps.common.convert_keys import output_values
from apps.common.convert_keys import output_line
from apps.common.convert_keys import convert_extend_propertys
from apps.background.lib.drivers.terraform_operate import TerraformResource
from apps.api.configer.provider import ProviderApi
from apps.background.resource.configr.history import HistoryObject
from apps.background.resource.configr.resource import ResourceObject
from apps.background.resource.configr.value_config import ValueConfigObject
from apps.background.resource.resource_base import CrsObject


class ApiBase(TerraformResource):
    def __init__(self):
        super(ApiBase, self).__init__()
        self.resource_name = ""
        self.resource_workspace = ""
        self.owner_resource = ""
        self.relation_resource = ""
        self.resource_object = None
        self.resource_keys_config = None

    def _flush_resobj(self):
        self.resource_object = CrsObject(self.resource_name)

    def create_resource_exists(self, rid):
        # todo 接入refresh, 如果数据不存在,则清除, 如果数据存在, 则更新状态
        _exists_data = self.resource_object.ora_show(rid)
        if _exists_data:
            if _exists_data.get("is_deleted"):
                logger.info("create resource check id exists and status is deleted, clear it")
                HistoryObject().create(create_data={"id": rid, "resource": self.resource_name,
                                                    "ora_data": _exists_data})

                self.resource_object.ora_delete(rid)
                return
            else:
                return _exists_data
        else:
            return

    def refresh_remote_state(self, path):
        result = self.refresh(path)
        return result.get("resources")

    def resource_info(self, provider):
        '''

        :param provider:
        :return:
        '''

        # if self.resource_keys_config:
        #     return

        self.resource_keys_config = ResourceObject().query_one(where_data={"provider": provider,
                                                                           "resource_name": self.resource_name})
        if not self.resource_keys_config:
            raise local_exceptions.ResourceConfigError("%s 资源未初始化完成配置" % self.resource_name)

    def values_config(self, provider):
        '''

        :param provider:
        :return:
        '''

        return ValueConfigObject().resource_value_configs(provider, self.resource_name)

    def workspace_controller(self, rid, provider_name, region, provider_json):
        _path = self.create_workpath(rid,
                                     provider=provider_name,
                                     region=region)

        self.write_provider_define(_path, define_json=provider_json)
        self.init_workspace(_path, provider_name)

        return _path

    def resource_filter_controller(self, provider_name, label_name, create_data, extend_info):
        define_json = self._generate_resource(provider_name, label_name=label_name,
                                              data=create_data, extend_info=extend_info)

        output_json = self._generate_output(label_name=label_name)
        define_json.update(output_json)

        return define_json

    def read_output_controller(self, result):
        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        res = self._read_output_result(result)

        if not res.get("resource_id"):
            res["resource_id"] = self._fetch_id(result)

        return res

    def update_db_controller(self, rid, result, output_json):
        resource_id = output_json.get("resource_id")
        _update_data = {"status": "ok", "resource_id": resource_id,
                        "output_json": output_json,
                        "result_json": format_json_dumps(result)}

        return self.update_data(rid, data=_update_data)

    def before_keys_checks(self, provider, create_data):
        '''
        校验依赖的id的合法性
        :param kwargs:
        :return:
        '''

        self.resource_info(provider)
        return {}

    def _generate_output(self, label_name):
        '''
        转换output 输出参数，生成配置
        :param label_name:
        :return:
        '''

        output_configs = self.resource_keys_config["output_property"]
        resource_name = self.resource_keys_config["property"]

        _ext_output = {}
        for key, define in output_configs.items():
            _ext_output.update(output_line(key, define))

        ext_output_config = {}
        for column, ora_column in _ext_output.items():
            ext_output_config[column] = {"value": "${%s.%s.%s}" % (resource_name, label_name, ora_column)}

        return {"output": ext_output_config} if ext_output_config else {}

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

        resource_name = self.resource_keys_config["property"]
        resource_property = self.resource_keys_config["resource_property"]
        resource_extend_info = self.resource_keys_config["extend_info"]

        resource_columns = {}
        for key, value in data.items():
            if resource_values_config.get(key):
                _values_configs = resource_values_config.get(key)
                value = convert_value(value, _values_configs.get(value))

            resource_columns[key] = value

        resource_columns = convert_keys(resource_columns, defines=resource_property)
        _extend_columns = convert_keys(datas=extend_info, defines=resource_property, is_extend=True)
        logger.info("property extend info; %s" % (format_json_dumps(_extend_columns)))
        resource_columns.update(_extend_columns)
        _extend_columns = convert_extend_propertys(datas=extend_info, extend_info=resource_extend_info)
        logger.info("extend info; %s" % (format_json_dumps(_extend_columns)))
        resource_columns.update(_extend_columns)

        _info = {
            "resource": {
                resource_name: {
                    label_name: resource_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def formate_result(self, result):
        '''
        对 result 做处理
        :param result:
        :return:
        '''

        return result

    def save_data(self, rid, provider,
                  provider_id, region, zone,
                  owner_id, relation_id, extend_info,
                  define_json, status, result_json,
                  create_data, **kwargs):

        '''

        :param rid:
        :param provider:
        :param provider_id:
        :param region:
        :param zone:
        :param owner_id:
        :param relation_id:
        :param extend_info:
        :param define_json:
        :param status:
        :param result_json:
        :param kwargs:
        :return:
        '''

        create_data.update(kwargs)
        if owner_id and self.owner_resource:
            owner_id = self.owner_resource + "_" + owner_id
        if relation_id and self.relation_resource:
            relation_id = self.relation_resource + "_" + relation_id

        self.resource_object.create(create_data={"id": rid, "provider": provider,
                                                 "provider_id": provider_id,
                                                 "region": region, "zone": zone,
                                                 "resource_name": self.resource_name,
                                                 "owner_id": owner_id,
                                                 "relation_id": relation_id,
                                                 "propertys": create_data,
                                                 "status": status,
                                                 "extend_info": extend_info,
                                                 "define_json": define_json,
                                                 "result_json": result_json})

    def update_data(self, rid, data):
        '''

        :param rid:
        :param data:
        :return:
        '''
        if data.get("extend_info"):
            if isinstance(data["extend_info"], dict):
                data["extend_info"] = format_json_dumps(data["extend_info"])

        return self.resource_object.update(rid, data)

    def rollback_data(self, rid):
        '''

        :param rid:
        :return:
        '''
        try:
            self.resource_object.ora_delete(rid)
        except:
            logger.info(traceback.format_exc())

    def _fetch_id(self, result):
        '''

        :param result:
        :return:
        '''

        try:
            _data = result.get("resources")[0]
            _instances = _data.get("instances")[0]
            _attributes = _instances.get("attributes")
            return _attributes.get("id")[:62] or "0000000"
        except:
            logger.info(traceback.format_exc())
            raise ValueError("result can not fetch id")

    def _read_output_result(self, result):
        '''
        对于设置了output的属性， 则提取output输出值
        :param result:
        :return:
        '''

        models = self.resource_keys_config["output_property"]
        if models:
            result_output = result.get("outputs")

            ext_result = {}
            for column, res in result_output.items():
                _out_dict = read_output(key=column, define=models.get(column),
                                        result=res.get("value"))
                ext_result.update(_out_dict)

            if "resource_id" in ext_result.keys():
                if len(ext_result["resource_id"]) > 63:
                    ext_result["resource_id"] = ext_result["resource_id"][:62]
                    logger.info("resource id length more than 64, will truncated for resource_id")

            logger.info(format_json_dumps(ext_result))
            return ext_result

        return {}

    def run_create(self, rid, provider_id, region, zone,
                   provider_object, provider_info,
                   owner_id, relation_id,
                   create_data, extend_info, **kwargs):
        '''

        :param rid:
        :param provider_id:
        :param region:
        :param zone:
        :param owner_id:
        :param relation_id:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid

        # provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        # _relations_id_dict = self.before_keys_checks(create_data)
        # create_data.update(_relations_id_dict)

        define_json = self.resource_filter_controller(provider_name=provider_object["name"],
                                                      label_name=label_name,
                                                      create_data=create_data,
                                                      extend_info=extend_info)

        self.save_data(rid, provider=provider_object["name"],
                       provider_id=provider_id,
                       region=region, zone=zone,
                       owner_id=owner_id,
                       relation_id=relation_id,
                       extend_info=extend_info,
                       define_json=define_json,
                       status="applying",
                       create_data=create_data,
                       result_json={}, **kwargs)

        _path = ""
        try:
            _path = self.workspace_controller(rid, provider_object["name"], region, provider_info)
            self.write_define(rid, _path, define_json=define_json)

            result = self.run(_path)
        except Exception, e:
            self.rollback_data(rid)
            if _path:
                self.rollback_workspace(_path)
            raise e

        output_json = self.read_output_controller(result)
        count, res = self.update_db_controller(rid, result, output_json)
        return count, self.result_return_controller(res)

    def result_return_controller(self, result):
        info = {}
        for key in ["id", "provider", "provider_id", "region", "zone",
                    "resource_name", "resource_id", "owner_id", "relation_id",
                    "status", "created_time", "updated_time"]:
            info[key] = result.get(key)

        info.update(result.get("propertys", {}))
        info.update(result.get("extend_info", {}))
        info.update(result.get("output_json", {}))
        return info

    def create(self, **kwargs):
        '''
        main    create resource and save info into db
        :param kwargs:
        :return:
        '''
        raise NotImplementedError()

    def destory(self, rid):
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

        if not self.destory_ensure_file(rid, path=_path):
            self.rewrite_state(_path, state_file=resource_info["result_json"])
            self.write_define(rid, _path, define_json=resource_info["define_json"])

            if not self.ensure_provider_file(_path):
                provider_object, provider_info = ProviderApi().provider_info(resource_info.get("provider_id"),
                                                                             region=resource_info.get("region"))

                self.workspace_controller(rid, provider_name=resource_info["provider"],
                                          region=resource_info["region"], provider_json=provider_info)

        status = self.run_destory(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)
