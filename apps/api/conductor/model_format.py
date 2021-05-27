# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.uuid_util import get_uuid
from apps.api.conductor.type_format import TypeFormat
from apps.background.resource.resource_base import CrsObject
from apps.background.resource.configr.region import RegionObject
from apps.background.resource.configr.region import ZoneObject
from apps.background.resource.vm.instance_type import InstanceTypeObject


class ModelFormat(object):
    @classmethod
    def format_type(cls, value, type):
        '''
        校验数据类型， 并转换
        :param value:
        :param type:
        :return:
        '''

        if (type == "string") and (not isinstance(value, basestring)):
            value = TypeFormat.f_string(value)
        elif (type == "int") and not isinstance(value, int):
            value = TypeFormat.f_int(value)
        elif (type == "float") and (not isinstance(value, float)):
            value = TypeFormat.f_float(value)
        elif (type == "json") and (not isinstance(value, dict)):
            value = TypeFormat.f_dict(value)
        elif (type == "list") and (not isinstance(value, list)):
            value = TypeFormat.f_list(value)
        elif (type == "bool") and (not isinstance(value, bool)):
            value = TypeFormat.f_bool(value)
        else:
            pass

        return value

    @classmethod
    def not_null(cls, key, value):
        '''

        :param key:
        :param value:
        :return:
        '''

        if not value and not isinstance(value, (int, bool, float)):
            raise ValueError("key: %s 不允许为空" % key)

    @classmethod
    def fill_default(cls, value, default):
        '''

        :param value:
        :param default:
        :return:
        '''
        if not value and not isinstance(value, (int, bool, float)):
            value = value or default

        return value

    @classmethod
    def format_apply_value(cls, key, value, define):
        '''

        :param key:
        :param value:
        :param define:
        :return:
        '''

        value = cls.fill_default(value, define.get("default"))
        allow_null = define.get("allow_null", 1)
        if not int(allow_null):
            cls.not_null(key, value)

        return value

    @classmethod
    def format_query_value(cls, key, value, define):
        '''

        :param key:
        :param value:
        :param define:
        :return:
        '''

        allow_null = define.get("allow_null", 1)
        if not int(allow_null):
            cls.not_null(key, value)

        return value

    @classmethod
    def convert_value(cls, value, define):
        '''

        :param key:
        :param value:
        :param define:
            string or json
            example: cidr replace cidr_block
            define:  cidr_block
            or: {"value": "cidr_block", "type": "string"}
        :return:
        '''

        if (value is None) or (define is None):
            return value
        if isinstance(define, (basestring, bool, int)):
            value = define or value
        elif isinstance(define, dict):
            value = define.get("value", value) or value
            value = cls.format_type(value, define.get("type", "string"))
        else:
            raise ValueError("转换配置错误， 类型错误")

        return value

    @classmethod
    def convert_apply_value(cls, value, define):
        if not value or not define:
            return value
        if isinstance(value, (basestring, int, bool, float)):
            value = cls.convert_value(value, define.get(value))
        elif isinstance(value, list):
            res = []
            for x_value in value:
                t = cls.convert_value(x_value, define.get(value))
                res.append(t)

            value = res
        else:
            pass

        return value

    @classmethod
    def convert_output_value(cls, value, define):
        # todo output update  转换output输出参数
        if not value:
            return value
        if isinstance(value, (basestring, int, bool, float)):
            value = cls.convert_value(value, define.get(value))
        elif isinstance(value, list):
            res = []
            for x_value in value:
                t = cls.convert_value(x_value, define.get(value))
                res.append(t)

            value = res
        else:
            pass

        return value

    @classmethod
    def _hint_resource_id_(cls, value, define):
        '''

        :param value:
        :param define:
        :return:
        '''

        # for define $resource, filter any resource
        if "." in define:
            resource_name = define.split(".")[1]
        else:
            resource_name = ""

        logger.info("_hint_resource_, filter resource %s" % resource_name)
        if isinstance(value, basestring):
            t_data = CrsObject(resource_name).show(rid=value)
            value = t_data.get("resource_id") or value
        elif isinstance(value, list):
            c, t_data = CrsObject(resource_name).list(filter_in={"id": value})
            if resource_name and len(value) < c:
                raise ValueError("资源存在重复注册，请检查")

            convertd = []
            for x in t_data:
                convertd.append(x.get("id"))
                value.append(x.get("resource_id"))

            logger.info("_hint_resource_, convert resource id: %s" % (bytes(convertd)))
            value = list(set(value) - set(convertd))
        else:
            raise ValueError("不正确的资源id： %s" % value)

        return value

    @classmethod
    def _hint_resource_id_outer_(cls, value, define):
        '''

        :param value:
        :param define:
        :return:
        '''

        # for define $resource, filter any resource
        if "." in define:
            resource_name = define.split(".")[1]
        else:
            resource_name = ""

        logger.info("_hint_resource_id_outer_, filter resource %s" % resource_name)
        if isinstance(value, basestring):
            value = CrsObject(resource_name).asset_object_id(value)
        elif isinstance(value, list):
            c, t_data = CrsObject(resource_name).list(filter_in={"resource_id": value})

            convertd = []
            for x in t_data:
                convertd.append(x.get("resource_id"))
                value.append(x.get("id"))

            logger.info("_hint_resource_id_outer_, convert resource id: %s" % (bytes(convertd)))
            value = list(set(value) - set(convertd))
        else:
            pass
            # raise ValueError("不正确的资源id： %s" % value)

        return value

    @classmethod
    def _hint_zone_id_(cls, value):
        '''

        :param value:
        :param define:
        :return:
        '''

        # for define zone
        if isinstance(value, basestring):
            t_data = ZoneObject().zone_object(value)
            value = t_data.get("asset_id") or value
        elif isinstance(value, list):
            c, t_data = ZoneObject().list(filter_in={"id": value})
            if len(value) != c:
                raise ValueError("zone id 列表存在未注册zone")

            convertd = []
            for x in t_data:
                convertd.append(x.get("id"))
                value.append(x.get("asset_id"))

            logger.info("_hint_resource_, convert resource id: %s" % (bytes(convertd)))
            value = list(set(value) - set(convertd))
        else:
            raise ValueError("不正确的 zone id： %s" % value)

        return value


    @classmethod
    def _hint_zone_id_outer_(cls, value):
        '''

        :param value:
        :param define:
        :return:
        '''

        # for define zone
        if isinstance(value, basestring):
            t_data = ZoneObject().zone_asset(value)
            value = t_data.get("id") or value
        elif isinstance(value, list):
            c, t_data = ZoneObject().list(filter_in={"asset_id": value})

            convertd = []
            for x in t_data:
                convertd.append(x.get("asset_id"))
                value.append(x.get("id"))

            logger.info("_hint_zone_id_outer_, convert resource id: %s" % (bytes(convertd)))
            value = list(set(value) - set(convertd))
        else:
            raise ValueError("不正确的 zone id： %s" % value)

        return value

    @classmethod
    def _hint_region_id_(cls, value):
        '''

        :param value:
        :param define:
        :return:
        '''

        # for define zone
        if isinstance(value, basestring):
            t_data = RegionObject().region_object(value)
            value = t_data.get("asset_id") or value
        elif isinstance(value, list):
            c, t_data = RegionObject().list(filter_in={"id": value})
            if len(value) != c:
                raise ValueError("region id 列表存在未注册region")

            convertd = []
            for x in t_data:
                convertd.append(x.get("id"))
                value.append(x.get("asset_id"))

            logger.info("_hint_resource_, convert resource id: %s" % (bytes(convertd)))
            value = list(set(value) - set(convertd))
        else:
            raise ValueError("不正确的 region id： %s" % value)

        return value

    @classmethod
    def _hint_region_id_outer_(cls, value):
        '''

        :param value:
        :param define:
        :return:
        '''

        # for define zone
        if isinstance(value, basestring):
            t_data = RegionObject().region_asset(value)
            value = t_data.get("id") or value
        elif isinstance(value, list):
            c, t_data = RegionObject().list(filter_in={"asset_id": value})

            convertd = []
            for x in t_data:
                convertd.append(x.get("asset_id"))
                value.append(x.get("id"))

            logger.info("_hint_region_id_outer_, convert resource id: %s" % (bytes(convertd)))
            value = list(set(value) - set(convertd))
        else:
            raise ValueError("不正确的 region id： %s" % value)

        return value


    @classmethod
    def _hint_instance_type_(cls, provider, value):
        '''

        :param value:
        :param define:
        :return:
        '''

        # for define instance type
        if isinstance(value, basestring):
            t_data, _ = InstanceTypeObject().convert_resource_name(provider, value)
            value = t_data or value
        elif isinstance(value, list):
            c, t_data = InstanceTypeObject().list(filters={"provider": provider}, filter_in={"name": value})

            convertd = []
            for x in t_data:
                convertd.append(x.get("name"))
                value.append(x.get("origin_name"))

            logger.info("_hint_resource_, convert resource: %s" % (bytes(convertd)))
            value = list(set(value) - set(convertd))
        else:
            raise ValueError("不正确的 instance type： %s" % value)

        return value

    @classmethod
    def _hint_instance_type_outer_(cls, provider, value):
        '''
         #todo instance type 转换信息新增 cpu 内存等信息
        :param value:
        :param define:
        :return:
        '''

        # for define instance type
        add_infos = {}
        if isinstance(value, (basestring, int)):
            value, add_infos = InstanceTypeObject().convert_asset(provider, value)
        elif isinstance(value, list):
            #for list add info is {}, e: list may not used
            c, t_data = InstanceTypeObject().list(filters={"provider": provider}, filter_in={"origin_name": value})

            convertd = []
            for x in t_data:
                convertd.append(x.get("origin_name"))
                value.append(x.get("name"))

            logger.info("_hint_instance_type_outer_, convert resource: %s" % (bytes(convertd)))
            value = list(set(value) - set(convertd))
        else:
            raise ValueError("不正确的 instance type： %s" % value)

        return value, add_infos

    @classmethod
    def hint_apply_infos(cls, provider, value, define):
        '''
        hint info， 用于转换cmdb信息定义
        :param value:
        :param define:
        :return:
        '''

        if define.get("hint"):
            define = define.get("hint")
        else:
            return value

        if define.startswith("$resource"):
            value = cls._hint_resource_id_(value, define)
        elif define == "$zone":
            value = cls._hint_zone_id_(value)
        elif define == "$region":
            value = cls._hint_region_id_(value)
        elif define == "$instance.type":
            value = cls._hint_instance_type_(provider, value)
        else:
            logger.info("define %s not define now, skip it ..." % (define))
        return value

    @classmethod
    def hint_outer_infos(cls, provider, value, define):
        '''
        hint info， 用于转换cmdb信息定义

        :param value:
        :param define:
        :return:
        '''

        add_infos = {}
        if define.get("hint"):
            define = define.get("hint")
        else:
            return value, add_infos

        logger.debug("outer revert value ...")
        if define.startswith("$resource"):
            value = cls._hint_resource_id_outer_(value, define)
        elif define == "$zone":
            value = cls._hint_zone_id_outer_(value)
        elif define == "$region":
            value = cls._hint_region_id_outer_(value)
        elif define == "$instance.type":
            value, add_infos = cls._hint_instance_type_outer_(provider, value)
        else:
            logger.info("define %s not define now, skip it ..." % (define))
        return value, add_infos
