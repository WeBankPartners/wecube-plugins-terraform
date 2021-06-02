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
from apps.background.lib.drivers.terraform_operate import TerraformResource
from apps.background.resource.configr.history import HistoryObject
from apps.background.resource.configr.resource import ResourceObject
from apps.background.resource.resource_base import CrsObject
from apps.api.conductor.provider import ProviderConductor
from apps.api.conductor.resource import ResourceConductor
from apps.api.conductor.valueConfiger import ValueConductor
from apps.api.conductor.apply_output_conductor import read_output_result
from apps.api.conductor.apply_data_conductor import apply_data_builder
from apps.api.conductor.source_data_conductor import query_data_builder
from apps.api.conductor.source_data_conductor import query_return_builder
# from apps.api.conductor.source_output_conductor import source_object_outer
from apps.api.conductor.source_output_conductor import read_source_output
from apps.api.conductor.source_output_conductor import SourceOuterReader
from apps.api.conductor.source_output_conductor import read_outer_property


class ApiBackendBase(TerraformResource):
    def __init__(self, resource_name=None, resource_workspace=None):
        super(ApiBackendBase, self).__init__()
        self.resource_name = resource_name or ""
        self.resource_workspace = resource_workspace or ""
        self.owner_resource = ""
        self.relation_resource = ""
        self.resource_object = None
        self.resource_keys_config = None

    def _flush_resobj(self):
        self.resource_object = CrsObject(self.resource_name)

    def workspace_controller(self, rid, provider, region, provider_info):
        # 创建workspace目录，写入provider信息并初始化目录
        _path = self.create_workpath(rid, provider=provider, region=region)
        if provider_info:
            self.write_provider_define(_path, define_json=provider_info)

        self.init_workspace(_path, provider)
        return _path

    def get_resource_object(self, provider):
        resource_keys_config = ResourceObject().query_one(where_data={"provider": provider,
                                                                      "resource_type": self.resource_name})
        if not resource_keys_config:
            raise local_exceptions.ResourceConfigError("%s 资源未初始化完成配置" % self.resource_name)

        return resource_keys_config

    def get_values_config(self, provider):
        return ValueConductor().values_config(provider, self.resource_name)

    def get_secret(self, provider, region, secret, provider_data):
        # 获取认证信息
        return ProviderConductor().producer_secret_info(provider=provider, region=region,
                                                        secret=secret, provider_data=provider_data)

    def conductor_apply_data(self, provider, data, label_name, defines, resource_values_config):
        # 生成apply resource信息
        create_data = apply_data_builder(provider=provider, datas=data,
                                         defines=defines["resource_property"],
                                         resource_values_config=resource_values_config,
                                         resource_name=self.resource_name)

        logger.info(format_json_dumps(create_data))
        return ResourceConductor().conductor_apply_data(label_name, create_data,
                                                        ora_resource_name=defines["resource_name"])

    def insert_or_update(self, rid, provider, provider_id, region, zone,
                         resource_id, create_data, extend_info,
                         define_json, status, result_json, output_json,
                         owner_id=None, relation_id=None, **kwargs):

        create_data.update(kwargs)
        if owner_id and self.owner_resource:
            owner_id = self.owner_resource + "_" + owner_id
        if relation_id and self.relation_resource:
            relation_id = self.relation_resource + "_" + relation_id

        create_data = {"id": rid, "provider": provider, "provider_id": provider_id,
                       "region": region, "zone": zone, "resource_name": self.resource_name,
                       "owner_id": owner_id, "relation_id": relation_id,
                       "propertys": create_data, "extend_info": extend_info,
                       "status": status, "define_json": define_json,
                       "resource_id": resource_id, "output_json": output_json,
                       "result_json": format_json_dumps(result_json)}

        _exists_data = self.resource_object.ora_show(rid)
        if _exists_data:
            if _exists_data.get("is_deleted"):
                logger.info("create id exists but status is deleted, backup and update it")
                HistoryObject().create({"id": rid, "resource": self.resource_name, "ora_data": _exists_data})
                create_data.update({"is_deleted": 0, "deleted_time": None})

            create_data.pop("id", None)
            return self.resource_object.ora_update(rid, create_data)
        else:
            return self.resource_object.create(create_data=create_data)

    def rewrite_resource_state(self, rid, provider, region, provider_info, workpath, exists_data):
        # 重写state文件
        logger.info("recovery state ..")
        self.workspace_controller(rid, provider, region, provider_info)
        self.rewrite_state(workpath, state_file=exists_data["result_json"])
        logger.info("rewrite state file complete, continue...")

    def _run_apply_and_read_result(self, rid, provider, region, provider_info, define_json, skip_backup=None):
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
            return self.run(_path, skip_backup=skip_backup)
        except Exception, e:
            if _path:
                self.rollback_workspace(_path)
            raise e

    def source_filter_controller(self, label_name, query_data, resource_object):
        return ResourceConductor().generate_data_source(label_name, query_data, resource_object)

    def import_filter_controller(self, provider_name, label_name, query_data):
        return ResourceConductor().conductor_reset_resource(provider=provider_name,
                                                            resource_name=self.resource_name,
                                                            label_name=label_name,
                                                            resource_data=query_data)

    def _import_resource_(self, rid, provider, region, provider_info, asset_id, resource_id, label_name):
        workpath = self.get_workpath(rid, provider, region)
        try:
            query_data = {"asset_id": resource_id} if resource_id else {}

            self.workspace_controller(rid, provider, region, provider_info)
            define_json, resource_keys_config = self.import_filter_controller(provider_name=provider,
                                                                              label_name="q_" + rid,
                                                                              query_data=query_data

                                                                              )

            import_define_json, _ = ResourceConductor().conductor_import_resource(provider=provider,
                                                                                  resource_name=self.resource_name,
                                                                                  label_name=label_name
                                                                                  )

            import_define_json.update(define_json)
            self.write_define(rid, workpath, define_json=import_define_json)

            dest_source = "%s.%s" % (resource_keys_config["resource_name"], label_name)
            self.run_import(from_source=asset_id, dest_source=dest_source, path=workpath, state=None)

            return False
        except Exception, e:
            logger.info(traceback.format_exc())
            raise e

    def source_run_import(self, rid, provider, region, label_name,
                          provider_info, asset_id, resource_id,
                          skip_rewrite=None):

        workpath = self.get_workpath(rid, provider, region)

        if self.is_need_imort(workpath):
            logger.info("state file not exists, try recovery ..")
            exists_data = self.resource_object.show(rid)
            if exists_data:
                return self.rewrite_resource_state(rid=rid, provider=provider, region=region,
                                                   provider_info=provider_info, workpath=workpath,
                                                   exists_data=exists_data)
        else:
            logger.info("state file exists continue ...")
            return False

        if asset_id and resource_id:
            logger.info("asset id given, try import resource..")
            self._import_resource_(rid, provider, region, provider_info, asset_id, resource_id, label_name)

        logger.info("state file not recovery, continue apply resource ... ")
        return True

    def read_output_controller(self, provider, result, resource_object, resource_values_config):
        logger.info(format_json_dumps(result))
        return read_output_result(provider, result, models=resource_object.get("resource_property"),
                                  resource_values_config=resource_values_config,
                                  resource_name=self.resource_name)

    def run_create(self, rid, region, zone, provider_object, provider_info,
                   asset_id, resource_id, create_data, extend_info,
                   resource_object, resource_values_config, **kwargs):
        '''

        :param rid:
        :param region:
        :param zone:
        :param provider_object:
        :param provider_info:
        :param asset_id:
        :param resource_id:
        :param create_data:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        extend_info = extend_info or {}
        label_name = self.resource_name + "_" + rid

        define_json = self.conductor_apply_data(provider=provider_object["name"],
                                                data=create_data, label_name=label_name,
                                                defines=resource_object,
                                                resource_values_config=resource_values_config)

        self.source_run_import(rid=rid, provider=provider_object["name"], region=region, label_name=label_name,
                               provider_info=provider_info, asset_id=asset_id, resource_id=resource_id)

        output_json = ResourceConductor().apply_output(label_name=label_name, resource_object=resource_object)

        define_json.update(output_json)
        result = self._run_apply_and_read_result(rid, provider=provider_object["name"],
                                                 region=region, provider_info=provider_info,
                                                 define_json=define_json, skip_backup=None)

        output_res = self.read_output_controller(provider=provider_object["name"], result=result,
                                                 resource_object=resource_object,
                                                 resource_values_config=resource_values_config)

        count, res = self.insert_or_update(rid, provider=provider_object["name"],
                                           provider_id=provider_object["id"],
                                           region=region, zone=zone,
                                           extend_info=extend_info,
                                           define_json=define_json,
                                           resource_id=output_res.get("asset_id"),
                                           status="ok", output_json=output_res,
                                           create_data=create_data,
                                           result_json=result, **kwargs)

        output_res["id"] = rid
        return count, output_res

    def apply(self, rid, base_info, base_bodys, create_data, extend_info, asset_id=None, resource_id=None, **kwargs):
        '''

        :param rid:
        :param base_info:  provider, region, zone secret 基础信息
        :param base_bodys: provider， region等object 信息
        :param create_data: 资源apply参数
        :param extend_info: 其他参数
        :param asset_id: 资产id
        :param resource_id:  资源id
        :param kwargs:
        :return:
        '''

        # for object:
        extend_info = extend_info or {}
        secret = base_info.get("secret")

        provider_object = base_bodys.get("provider_data")
        region_object = base_bodys.get("region_info")
        zone_object = base_bodys.get("zone_info")

        provider = provider_object["name"]
        region = region_object["asset_id"]
        zone = zone_object.get("asset_id")

        resource_object = self.get_resource_object(provider=provider)
        resource_values_config = self.get_values_config(provider)

        secret_info = self.get_secret(provider=provider, region=region_object["name"],
                                      secret=secret, provider_data=provider_object)
        provider_info = ProviderConductor().conductor_provider(provider_object, region_object, secret_info)

        count, res = self.run_create(rid=rid, region=region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     asset_id=asset_id, resource_id=resource_id,
                                     create_data=create_data,
                                     resource_object=resource_object,
                                     resource_values_config=resource_values_config,
                                     extend_info=extend_info, **kwargs)

        return count, res

    def create(self, *args, **kwargs):
        return self.apply(*args, **kwargs)

    def destroy_search_object(self, rid):
        resource_info = self.resource_object.show(rid)
        if not resource_info:
            raise ValueError("资源不存在或没被纳管 %s" % rid)
        return resource_info

    def destroy_rewrite(self, rid, path, resource_info):
        if not self.destroy_ensure_file(rid, path=path):
            self.rewrite_state(path, state_file=resource_info["result_json"])
            self.write_define(rid, path, define_json=resource_info["define_json"])
            if not self.ensure_provider_file(path):
                # 缺失认证文件，设置为直接异常
                raise ValueError("缺失provider文件")

    def destroy(self, rid):
        '''

        :param rid:
        :return:
        '''

        resource_info = self.destroy_search_object(rid)
        _path = self.create_workpath(rid, provider=resource_info["provider"], region=resource_info["region"])

        self.destroy_rewrite(rid, _path, resource_info)
        status = self.run_destroy(_path)
        if not status:
            raise local_exceptions.ResourceOperateException(self.resource_name,
                                                            msg="delete %s %s failed" % (self.resource_name, rid))

        return self.resource_object.delete(rid)

    def get_remote_source(self, rid, base_info, base_bodys, query_data, extend_info=None, **kwargs):
        rid = rid or "rand_%s" % (get_uuid())

        extend_info = extend_info or {}
        query_data.update(extend_info)
        secret = base_info.get("secret")

        provider_object = base_bodys.get("provider_data")
        region_object = base_bodys.get("region_info")
        zone_object = base_bodys.get("zone_info")

        provider = provider_object["name"]
        resource_object = self.get_resource_object(provider=provider)
        resource_values_config = self.get_values_config(provider)

        secret_info = self.get_secret(provider=provider, region=region_object["name"],
                                      secret=secret, provider_data=provider_object)
        provider_info = ProviderConductor().conductor_provider(provider_object, region_object, secret_info)

        result = self.run_query(rid=rid, region=region_object["asset_id"],
                                zone=zone_object.get("asset_id"),
                                provider_object=provider_object,
                                provider_info=provider_info,
                                query_data=query_data,
                                resource_object=resource_object,
                                resource_values_config=resource_values_config, **kwargs)

        return result

    def run_query(self, rid, region, zone, provider_object, provider_info,
                  query_data, resource_object, resource_values_config, **kwargs):

        label_name = self.resource_name + "_q_" + rid
        build_query_data = query_data_builder(provider=provider_object["name"], datas=query_data,
                                              defines=resource_object.get("data_source"),
                                              resource_values_config=resource_values_config,
                                              resource_name=self.resource_name)

        define_json = self.source_filter_controller(label_name=label_name,
                                                    query_data=build_query_data,
                                                    resource_object=resource_object)

        result = self._run_apply_and_read_result(rid=label_name, provider=provider_object["name"],
                                                 region=region, provider_info=provider_info,
                                                 define_json=define_json, skip_backup=None)

        output_json = self.read_query_result_controller(provider=provider_object["name"],
                                                        result=result, defines=resource_object,
                                                        resource_values_config=resource_values_config)

        result_list = query_return_builder(data=query_data, defines=resource_object["data_source"], results=output_json)
        return result_list

    def read_query_result_controller(self, provider, result, defines, resource_values_config):
        logger.info(format_json_dumps(result))

        try:
            data_source_argument = SourceOuterReader.format_argument("data_source_argument",
                                                                     defines.get("data_source_argument"))
            output_results = read_source_output(result, data_source_argument)
        except:
            logger.info(traceback.format_exc())
            raise ValueError("query remote source failed, result read faild")

        res = []
        for out_data in output_results:
            x_res = read_outer_property(provider, out_data, defines.get("data_source_output"),
                                        resource_values_config, resouce_name=self.resource_name)
            res.append(x_res)

        logger.info(format_json_dumps(res))
        return res

