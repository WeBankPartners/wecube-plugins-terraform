# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.logs import logger
from lib.json_helper import format_json_dumps
from apps.common.reverse import Reverse


class ReverseProperty(object):
    @classmethod
    def reverse_key(cls, key, define):
        '''

        :param key:
        :param define:
        {
        "type": "string",
        "convert": "access_key",
        "allow_null": 1,
        "default": ""
        }
        :return:
        '''

        if isinstance(define, basestring):
            if define == '-':
                return {}
            newkey = define or key
        else:
            newkey = key
            if define.get("convert"):
                newkey = define.get("convert") or key

        if newkey:
            return {newkey: key}
        else:
            logger.info("key %s define is null, skip" % key)
            return {}

    @classmethod
    def reverse_key_equivalence(cls, key, define):
        '''

        :param key:
        :param define:
        {
        "type": "string",
        "convert": "access_key",
        "allow_null": 1,
        "default": ""
        }
        :return:
        '''

        if isinstance(define, basestring):
            if define == '-':
                return {}
        else:
            if define.get("equivalence"):
                return {key: define.get("equivalence")}

        return {}

    @classmethod
    def reverse_keys(cls, defines):
        info = {}
        for key, value in defines.items():
            info.update(cls.reverse_key(key, value))

        return info

    @classmethod
    def reverse_equivalence(cls, defines):
        info = {}
        for key, value in defines.items():
            info.update(cls.reverse_key_equivalence(key, value))

        return info

    @classmethod
    def reverse_output_line(cls, key, define):
        if isinstance(define, basestring):
            if define == "-":
                return {}
            newkey = define
        elif isinstance(define, dict):
            newkey = define.get("value") or key
        else:
            raise ValueError("output define error")

        return {newkey: key}

    @classmethod
    def reverse_output_lines(cls, defines):
        info = {}
        for key, value in defines.items():
            info.update(cls.reverse_output_line(key, value))

        return info

    @classmethod
    def reverse_extend_key(cls, key, define):
        '''

        :param key:
        :param define:
        {
        "type": "string",
        "convert": "access_key",
        "allow_null": 1,
        "default": ""
        }
        :return:
        '''

        newkey = key
        if isinstance(define, (basestring, int, float, bool)):
            if define == '-':
                return {}
            # newkey = define or key
        elif isinstance(define, dict):
            newkey = key
            if define.get("convert"):
                newkey = define.get("convert") or key

        if newkey:
            return {newkey: key}
        else:
            logger.info("extend key %s define is null, skip" % key)
            return {}

    @classmethod
    def reverse_extend_equivalence(cls, key, define):
        '''

        :param key:
        :param define:
        {
        "type": "string",
        "convert": "access_key",
        "allow_null": 1,
        "default": ""
        }
        :return:
        '''

        if isinstance(define, (basestring, int, float, bool)):
            if define == '-':
                return {}
        elif isinstance(define, dict):
            if define.get("equivalence"):
                return {key: define.get("equivalence")}

        return {}

    @classmethod
    def reverse_extend_keys(cls, defines):
        info = {}
        for key, value in defines.items():
            info.update(cls.reverse_extend_key(key, value))

        return info

    @classmethod
    def reverse_extend_key_equivalence(cls, defines):
        info = {}
        for key, value in defines.items():
            info.update(cls.reverse_extend_equivalence(key, value))

        return info

    @classmethod
    def format_keys(cls, defines):
        result = {}
        for key, define in defines.items():
            result.update(cls.reverse_key(key, define))

        return result

    @classmethod
    def format_value(cls, value, defines):
        if not defines:
            return value

        if isinstance(defines, (basestring, bool, int, float)):
            return defines

        for key, define in defines.items():
            if isinstance(define, (basestring, bool, int, float)):
                if value == define:
                    return key
            elif isinstance(define, dict):
                t = define.get("value", value)
                if isinstance(t, (bool, int, float, basestring)):
                    if t == value:
                        return key
                elif isinstance(t, dict):
                    t = json.dumps(t)
                    logger.info("warn: %s config is json, not apply now" % key)
                else:
                    logger.info("warn: %s config is invalidate, not apply" % key)

        return value
