# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import time
# import copy
import traceback
from lib.logs import logger
from lib.uuid_util import get_uuid
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import read_output
from apps.background.lib.drivers.terraform_operate import TerraformResource
from apps.api.configer.provider import ProviderApi
from apps.background.resource.configr.history import HistoryObject
from apps.background.resource.configr.resource import ResourceObject
from apps.background.resource.configr.value_config import ValueConfigObject
from apps.background.resource.vm.instance_type import InstanceTypeObject
from apps.background.resource.resource_base import CrsObject
from apps.api.conductor.region import RegionConductor
from apps.api.conductor.provider import ProviderConductor
from apps.api.conductor.resource import ResourceConductor
from apps.api.conductor.valueReverse import ValueResetConductor


def eval_variable(line, column, to_column):
    def find_num(data):
        count = 0
        data = data[len("$line"):]
        for i in data:
            try:
                count += 1
                int(i)
                count -= 1
                break
            except:
                continue

        if count == 0 or count == len(data):
            return None, None
        else:
            try:
                return data[:count], int(data[count:])
            except:
                raise ValueError("$line define error, use: [split + num], example: $line#2")

    if column == "$line":
        return {to_column: line}
    elif column.startswith("$line"):
        s_split, point = find_num(column)
        if s_split:
            tmp = line.split(s_split)
            t_value = tmp[point]
            return {to_column: t_value}
        else:
            return {to_column: line}
    else:
        logger.info("unknown define %s ,skip ..." % line)
        return {to_column: ""}


def fetch_property(instance_define, define_columns):
    if isinstance(instance_define, basestring):
        res = {}
        for key, value in define_columns.items():
            if key.startswith("$"):
                res.update(eval_variable(instance_define, key, value))
            else:
                res[value] = ""
        return res

    x_Origin_line = instance_define.pop("x_Origin_line", None)
    if x_Origin_line:
        for key, value in define_columns.items():
            if key.startswith("$"):
                instance_define.update(eval_variable(x_Origin_line, key, value))
            else:
                instance_define[value] = ""
        return instance_define

    res = {}
    for key, value in define_columns.items():
        if "." in key:
            _keys = key.split(".")
            tmp = instance_define
            for x_key in _keys:
                try:
                    x_key = int(x_key)
                    tmp = tmp[x_key]
                except:
                    tmp = tmp.get(x_key)

            res[value] = tmp
        else:
            res[value] = instance_define.get(key)

    return res


def skip_null_data(datas):
    result = []
    for out_data in datas:
        if isinstance(out_data, basestring):
            result.append(out_data)
            # continue
        elif isinstance(out_data, list):
            result.append(out_data)
        elif isinstance(out_data, dict):
            count = 0
            for _, x_value in out_data.items():
                if not x_value:
                    count += 1
            if count == len(out_data):
                logger.info("out data columns is null, skip ...")
                continue
            else:
                result.append(out_data)
        else:
            logger.info("result data type is not string, dict/list, skip....")

    return result


def fetch_columns(datas, columns):
    if len(columns) == 0:
        c_data = []
        for data in datas:
            if isinstance(data, list):
                c_data += data
            else:
                c_data.append(data)

        c_data = skip_null_data(c_data)
        return c_data
    column = columns.pop(0)
    if isinstance(datas, list):
        x_data = []
        for data in datas:
            if data.get(column):
                x_data.append(data.get(column))
        datas = x_data
        return fetch_columns(datas, columns)
    elif isinstance(datas, dict):
        datas = datas.get(column)
        return fetch_columns(datas, columns)
    else:
        logger.info("data is not dict/list, no columns %s filter, skip.." % column)
        return datas


def format_argument(key, data):
    if not data:
        return ""
    if isinstance(data, dict):
        return data
    elif isinstance(data, basestring):
        data = data.strip()
        if data.startswith("{"):
            try:
                data = json.loads(data)
            except:
                try:
                    data = eval(data)
                except:
                    logger.info(traceback.format_exc())
                    logger.info("key: %s, data: %s may is json, but format error")
                    raise ValueError("data: %s is not json " % (data))

        return data
    else:
        raise ValueError("key: %s 应为json或string" % key)


class ApiBackendBase(TerraformResource):
    def __init__(self):
        super(ApiBackendBase, self).__init__()
        self.resource_name = ""
        self.resource_workspace = ""
        self.owner_resource = ""
        self.relation_resource = ""
        self.resource_object = None
        self.resource_keys_config = None

    def _flush_resobj(self):
        self.resource_object = CrsObject(self.resource_name)

    def resource_info(self, provider):
        '''

        :param provider:
        :return:
        '''

        self.resource_keys_config = ResourceObject().query_one(where_data={"provider": provider,
                                                                           "resource_type": self.resource_name})
        if not self.resource_keys_config:
            raise local_exceptions.ResourceConfigError("%s 资源未初始化完成配置" % self.resource_name)

        return self.resource_keys_config

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

        if provider_json:
            self.write_provider_define(_path, define_json=provider_json)
        self.init_workspace(_path, provider_name)

        return _path

    def resource_filter_controller(self, provider_name, label_name, create_data, extend_info):
        '''

        :param provider_name:
        :param label_name:
        :param create_data:
        :param extend_info:
        :return:
        '''

        define_json, _ = ResourceConductor().conductor_apply_resource(provider=provider_name,
                                                                      resource_name=self.resource_name,
                                                                      label_name=label_name,
                                                                      create_data=create_data,
                                                                      extend_info=extend_info)
        return define_json

    def read_output_controller(self, result):
        result = self.formate_result(result)
        logger.info(format_json_dumps(result))

        res = self._read_output_result(result)

        if not res.get("resource_id"):
            res["resource_id"] = self._fetch_id(result)

        return res

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''
        校验依赖的id的合法性
        :param kwargs:
        :return:
        '''

        self.resource_info(provider)
        return {}

    def formate_result(self, result):
        '''
        对 result 做处理
        :param result:
        :return:
        '''

        return result

    def insert_or_update(self, rid, provider,
                         provider_id, region, zone,
                         owner_id, relation_id, extend_info,
                         define_json, status, result_json,
                         create_data, resource_id,
                         output_json, **kwargs):

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

        create_data = {"id": rid, "provider": provider,
                       "provider_id": provider_id,
                       "region": region, "zone": zone,
                       "resource_name": self.resource_name,
                       "owner_id": owner_id,
                       "relation_id": relation_id,
                       "propertys": create_data,
                       "status": status,
                       "extend_info": extend_info,
                       "define_json": define_json,
                       "resource_id": resource_id,
                       "output_json": output_json,
                       "result_json": format_json_dumps(result_json)}

        _exists_data = self.resource_object.ora_show(rid)
        if _exists_data:
            if _exists_data.get("is_deleted"):
                logger.info("create resource check id exists and status is deleted, backup and update it")
                HistoryObject().create(create_data={"id": rid, "resource": self.resource_name,
                                                    "ora_data": _exists_data})

                create_data.update({"is_deleted": 0, "deleted_time": None})

            return self.resource_object.ora_update(rid, create_data)
        else:
            count, _ = self.resource_object.create(create_data=create_data)
            time.sleep(0.01)
            res = self.resource_object.show(rid)
            return count, res

    def rollback_data(self, rid):
        '''

        :param rid:
        :return:
        '''
        try:
            # self.resource_object.ora_delete(rid)
            logger.info("apply resource error, but not rollback data...")
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
            return _attributes.get("id") or "0000000"
        except:
            logger.info(traceback.format_exc())
            raise ValueError("result can not fetch id")

    def _read_output_result(self, result):
        '''
        对于设置了output的属性， 则提取output输出值
        :param result:
        :return:
        '''

        models = self.resource_keys_config["resource_output"]
        if models:
            result_output = result.get("outputs")

            ext_result = {}
            for column, res in result_output.items():
                _out_dict = read_output(key=column, define=models.get(column),
                                        result=res.get("value"))
                ext_result.update(_out_dict)

            if "resource_id" in ext_result.keys():
                if len(ext_result["resource_id"]) > 512:
                    ext_result["resource_id"] = ext_result["resource_id"][:512]
                    logger.info("resource id length more than 512, will truncated for resource_id")

            logger.info(format_json_dumps(ext_result))
            return ext_result

        return {}

    def _run_create_and_read_result(self, rid, provider, region, provider_info, define_json, skip_backup=None):
        '''

        :param rid:
        :param provider:
        :param region:
        :param provider_info:
        :param define_json:
        :return:
        '''

        _path = ""
        try:
            _path = self.workspace_controller(rid, provider, region, provider_info)
            self.write_define(rid, _path, define_json=define_json)

            result = self.run(_path, skip_backup=skip_backup)
            return result
        except Exception, e:
            self.rollback_data(rid)
            if _path:
                self.rollback_workspace(_path)
            raise e

    def source_run_import(self, rid, provider, region, label_name,
                          provider_info, asset_id, resource_id,
                          skip_rewrite=None):

        workpath = self.get_workpath(rid, provider, region)
        import_status = self.is_need_imort(workpath)
        if import_status:
            logger.info("state file not exists, try recovery ..")
            exists_data = self.resource_object.show(rid)
            if exists_data:
                logger.info("info found, recovery state ..")
                self.workspace_controller(rid, provider, region, provider_info)
                self.rewrite_state(workpath, state_file=exists_data["result_json"])
                logger.info("rewrite state file, continue...")
                # import_status = False
                return False
        else:
            logger.info("state file exists continue ...")
            return False

        if asset_id and resource_id:
            logger.info("asset id given, try import resource..")
            try:
                query_data = {}
                if resource_id:
                    query_data = {"resource_id": resource_id}

                self.workspace_controller(rid, provider, region, provider_info)
                define_json, resource_keys_config = self.source_filter_controller(provider_name=provider,
                                                                                  label_name="q_" + rid,
                                                                                  query_data=query_data
                                                                                  )

                import_define_json, _ = ResourceConductor().conductor_import_resource(provider=provider,
                                                                                      resource_name=self.resource_name,
                                                                                      label_name=label_name
                                                                                      )

                import_define_json.update(define_json)
                self.write_define(rid, workpath, define_json=import_define_json)

                _cloud_resource_name = resource_keys_config["resource_name"]
                dest_source = "%s.%s" % (_cloud_resource_name, label_name)
                self.run_import(from_source=asset_id, dest_source=dest_source, path=workpath, state=None)

                return False
            except Exception, e:
                # self.rollback_data(rid)
                # if workpath:
                #     self.rollback_workspace(workpath)
                logger.info(traceback.format_exc())
                # logger.info("resource import failed. continue ... ")
                raise e

        logger.info("state file not recovery, continue apply resource ... ")
        return True

    def run_create(self, rid, region, zone,
                   provider_object, provider_info,
                   asset_id, resource_id,
                   owner_id, relation_id,
                   create_data, extend_info, **kwargs):
        '''

        :param rid:
        :param region:
        :param zone:
        :param owner_id:
        :param relation_id:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        # todo asset exists import resource
        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid

        flush_status = self.source_run_import(rid=rid, provider=provider_object["name"],
                                              region=region, label_name=label_name,
                                              provider_info=provider_info,
                                              asset_id=asset_id, resource_id=resource_id)

        define_json = self.resource_filter_controller(provider_name=provider_object["name"],
                                                      label_name=label_name,
                                                      create_data=create_data,
                                                      extend_info=extend_info)

        result = self._run_create_and_read_result(rid, provider=provider_object["name"],
                                                  region=region, provider_info=provider_info,
                                                  define_json=define_json, skip_backup=None)

        output_json = self.read_output_controller(result)

        count, res = self.insert_or_update(rid, provider=provider_object["name"],
                                           provider_id=provider_object["id"],
                                           region=region, zone=zone,
                                           owner_id=owner_id,
                                           relation_id=relation_id,
                                           extend_info=extend_info,
                                           define_json=define_json,
                                           resource_id=output_json.get("resource_id"),
                                           status="ok", output_json=output_json,
                                           create_data=create_data,
                                           result_json=result, **kwargs)

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

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {}
        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        return None, None

    def region_object(self, provider, region):
        if region:
            return RegionConductor().region_info(provider=provider, region=region)

    def zone_object(self, provider, zone):
        if zone:
            return RegionConductor().zone_info(provider=provider, zone=zone)

    def apply(self, rid, provider, region, zone, secret,
              create_data, extend_info,
              asset_id=None, resource_id=None,
              **kwargs):
        '''
        #todo 如果有记录则直接使用apply, 无记录/文件 刷新state import
        :param rid:
        :param provider:
        :param region:
        :param secret:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        # _exists_data = self.create_resource_exists(rid)
        # if _exists_data:
        #     return 1, _exists_data

        region = self.region_object(provider, region)
        zone = self.zone_object(provider, zone)

        extend_info = extend_info or {}
        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        zone = ProviderConductor().zone_info(provider=provider_object["name"], zone=zone)
        x_create_data, r_create_data = self.generate_create_data(zone, create_data,
                                                                 provider=provider_object["name"])

        _relations_id_dict = self.before_keys_checks(provider_object["name"], r_create_data)

        x_create_data.update(_relations_id_dict)

        owner_id, relation_id = self.generate_owner_data(create_data)
        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     asset_id=asset_id, resource_id=resource_id,
                                     owner_id=owner_id, relation_id=relation_id,
                                     create_data=x_create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res

    def create(self, *args, **kwargs):
        return self.apply(*args, **kwargs)

    def destroy(self, rid):
        '''

        :param rid:
        :return:
        '''

        resource_info = self.resource_object.show(rid)
        if not resource_info:
            # return 0
            raise ValueError("资源不存在或没被纳管 %s" % rid)

        _path = self.create_workpath(rid,
                                     provider=resource_info["provider"],
                                     region=resource_info["region"])

        if not self.destroy_ensure_file(rid, path=_path):
            self.rewrite_state(_path, state_file=resource_info["result_json"])
            self.write_define(rid, _path, define_json=resource_info["define_json"])

            if not self.ensure_provider_file(_path):
                provider_object, provider_info = ProviderApi().provider_info(resource_info.get("provider_id"),
                                                                             region=resource_info.get("region"))

                self.workspace_controller(rid, provider_name=resource_info["provider"],
                                          region=resource_info["region"], provider_json=provider_info)

        status = self.run_destroy(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)

    def source_filter_controller(self, provider_name, label_name, query_data):
        '''

        :param provider_name:
        :param label_name:
        :param query_data:
        :return:
        '''

        define_json, resource_keys_config = ResourceConductor().conductor_reset_resource(provider=provider_name,
                                                                                         resource_name=self.resource_name,
                                                                                         label_name=label_name,
                                                                                         resource_data=query_data)
        return define_json, resource_keys_config

    def read_data_output_controller(self, result):
        result_output = result.get("outputs")

        ext_result = {}
        for column, res in result_output.items():
            _out_dict = read_output(key=column, define=column,
                                    result=res.get("value"))
            ext_result.update(_out_dict)

        logger.info(format_json_dumps(ext_result))
        return ext_result

    def outer_equivalence(self, datas, defines):
        result = {}
        if not defines:
            return result
        for key, destkey in defines.items():
            x_data = datas.get(key)
            if isinstance(x_data, basestring):
                crs_data = CrsObject().query_one(where_data={"resource_id": x_data})
                x_resource = ""
                if crs_data:
                    x_resource = crs_data.get("id")

                result[destkey] = x_resource
            elif isinstance(x_data, list):
                c_resource = []
                for c_data in x_data:
                    crs_data = CrsObject().query_one(where_data={"resource_id": c_data})

                    if crs_data:
                        x_resource = crs_data.get("id")
                        c_resource.append(x_resource)

                result[destkey] = c_resource
            else:
                logger.info("equivalence support type string ot list, %s skip..." % (str(x_data)))

        return result

    def read_query_result_controller(self, provider, result, data_source_argument):
        # if not data_source_argument:
        # raise ValueError("data_source_argument not config")
        data_source_argument = data_source_argument or ''
        data_source_argument = format_argument("data_source_argument", data_source_argument)

        logger.info(format_json_dumps(result))
        try:
            instance_define = []
            _data = result.get("resources")[0]
            _instances = _data.get("instances")[0]
            _attributes = _instances.get("attributes")

            if data_source_argument:
                if isinstance(data_source_argument, basestring):
                    outlines = data_source_argument.split(".")
                    instance_define = fetch_columns(datas=_attributes, columns=outlines)
                elif isinstance(data_source_argument, dict):
                    # 多个字段提取定义 {"engree": {"property": "type", "attributes": "engress"}}
                    for s_key, s_value in data_source_argument.items():
                        if isinstance(s_value, basestring):
                            outlines = s_value.split(".")
                            instance_define += fetch_columns(datas=_attributes, columns=outlines)
                        elif isinstance(s_value, dict):
                            col_value = s_value.get("attributes", "")
                            outlines = col_value.split(".")
                            col_defines = fetch_columns(datas=_attributes, columns=outlines)
                            if s_value.get("property"):
                                x_tmp = []
                                for t_data in col_defines:
                                    add_columns = {s_value.get("property"): s_key}
                                    if isinstance(t_data, dict):
                                        t_data.update(add_columns)
                                    elif isinstance(t_data, basestring):
                                        add_columns["x_Origin_line"] = t_data
                                        t_data = add_columns
                                    x_tmp.append(t_data)

                                col_defines = x_tmp
                            instance_define += col_defines
                        else:
                            raise ValueError("data source argument 配置异常应为 string或json：key-value "
                                             "或 key - {'property': 'xxx', 'attributes': ''}")
            else:
                outlines = []
                instance_define = fetch_columns(datas=_attributes, columns=outlines)
        except:
            logger.info(traceback.format_exc())
            raise ValueError("query remote source failed, result read faild")

        resourceconduct = ResourceConductor()
        define_columns = resourceconduct.conductor_reset_filter(provider, self.resource_name)

        res = []
        for out_data in instance_define:
            x_res = fetch_property(out_data, define_columns)
            equivalence_define = resourceconduct.conductor_reset_equivalence(provider, self.resource_name)

            e_res = self.outer_equivalence(datas=x_res, defines=equivalence_define)
            x_res.update(e_res)
            res.append(x_res)

        # output_json = self.read_data_output_controller(result)

        # res.update(output_json)
        logger.info(format_json_dumps(res))
        return res

    def reverse_asset_ids(self):
        return []

    def reverse_asset_object(self, provider, data):
        '''
        转换资产id
        :param provider:
        :param data:
        :return:
        '''

        for key in self.reverse_asset_ids():
            x_data = data.get(key)
            if x_data:
                if isinstance(x_data, basestring):
                    data[key] = CrsObject().asset_object_id(data.get(key))
                elif isinstance(x_data, list):
                    tmp = []
                    for x_asset in x_data:
                        t = CrsObject().asset_object_id(data.get(x_asset))
                        tmp.append(t)
                    data[key] = tmp
                else:
                    logger.info("reverse asset object support string or list only, skip..")

        return data

    def run_query(self, rid, region, zone,
                  provider_object, provider_info,
                  query_data, **kwargs):
        '''

        :param rid:
        :param region:
        :param zone:
        :param owner_id:
        :param relation_id:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        # extend_info = extend_info or {}
        label_name = self.resource_name + "_q_" + rid

        define_json, resource_keys_config = self.source_filter_controller(provider_name=provider_object["name"],
                                                                          label_name=label_name,
                                                                          query_data=query_data
                                                                          )

        result = self._run_create_and_read_result(rid, provider=provider_object["name"],
                                                  region=region, provider_info=provider_info,
                                                  define_json=define_json)

        data_source_argument = resource_keys_config.get("data_source_argument")
        output_json = self.read_query_result_controller(provider_object["name"], result,
                                                        data_source_argument)

        result_list = []
        for out_data in output_json:
            x_json = ValueResetConductor().reset_values(provider=provider_object["name"],
                                                        resource_name=self.resource_name,
                                                        data=out_data)

            x_json = self.reverse_asset_object(provider=provider_object["name"], data=x_json)
            # x_json.update(query_data)

            if x_json.get("instance_type"):
                instance_type, resource_info = InstanceTypeObject().convert_asset(provider=provider_object["name"],
                                                                                  asset_name=x_json.get(
                                                                                      "instance_type"))
                x_json["instance_type"] = instance_type
                resource_info.update(x_json)
                result_list.append(resource_info)

            else:
                result_list.append(x_json)

        return result_list

    def before_source_asset(self, provider, query_data):
        return query_data

    def get_remote_source(self, rid, provider, region, zone, secret,
                          resource_id, **kwargs):

        rid = rid or resource_id or "rand_%s" % (get_uuid())

        region = self.region_object(provider, region)

        query_data = {}
        if resource_id:
            query_data = {"resource_id": resource_id}

        if zone:
            zone = RegionConductor().zone_asset(provider, zone)
            query_data["zone"] = zone

        query_data.update(kwargs)
        query_data = self.before_source_asset(provider, query_data)

        provider_object, provider_info = ProviderConductor().conductor_provider_info(provider, region, secret)

        result = self.run_query(rid=rid, region=region, zone=zone,
                                provider_object=provider_object,
                                provider_info=provider_info,
                                query_data=query_data, **kwargs)

        res = []

        if resource_id:
            for x_result in result:
                x_result["resource_id"] = resource_id
                res.append(x_result)
        else:
            res = result

        return res
