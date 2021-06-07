# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger


class TypeFormat(object):
    @staticmethod
    def f_dict(value):
        '''

        :param value:
        :return:
        '''

        def str_dict(value):
            try:
                return json.loads(value)
            except:
                if value.startswith("{"):
                    return eval(value)

                raise ValueError()

        if isinstance(value, dict):
            return value
        else:
            try:
                return str_dict(value)
            except:
                logger.info(traceback.format_exc())
                logger.info("key: %s, data: %s may is json, but format error")
                raise ValueError("%s 不是json" % value)

    @staticmethod
    def f_list(value):
        '''

        :param value:
        :return:
        '''
        if not value:
            return []
        def str_list(value):
            try:
                value = value.replace("[", "").replace("]", "")
                return value.split(",")
            except:
                pass

            try:
                return json.loads(value)
            except:
                return eval(value)

        try:
            if isinstance(value, basestring):
                if value.startswith("["):
                    value = str_list(value)
                elif "," in value:
                    value = value.split(",")
                elif ";" in value:
                    value = value.split(";")
                else:
                    _v = " ".join(value.split())
                    value = _v.split()
            elif isinstance(value, list):
                return value
            else:
                raise ValueError()
        except:
            raise ValueError("%s 不是list类型" % value)

        # 移除空值
        result = []
        for x_value in value:
            if x_value:
                result.append(x_value)
        return result

    @staticmethod
    def f_bool(value):
        '''

        :param value:
        :return:
        '''

        if isinstance(value, basestring):
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            else:
                raise ValueError()
        elif isinstance(value, int):
            if value:
                value = True
            else:
                value = False
        else:
            raise ValueError("未知的 bool值： %s" % value)

        return value

    @staticmethod
    def f_int(value):
        '''

        :param value:
        :return:
        '''

        try:
            value = int(value)
        except:
            raise ValueError("%s 不是int" % value)
        return value

    @staticmethod
    def f_float(value):
        '''

        :param value:
        :return:
        '''

        try:
            value = float(value)
        except:
            raise ValueError("%s 不是浮点类型" % value)
        return value

    @staticmethod
    def f_string(value):
        '''

        :param value:
        :return:
        '''

        if isinstance(value, int):
            value = str(value)
        else:
            raise ValueError("%s 不是string" % value)
        return value
