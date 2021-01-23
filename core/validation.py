# _*_ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import json

import re

import core.local_exceptions as exception_common
from lib.ip_helper import check_ip

args_type = {
    "int": u"整数",
    "list": u"列表",
    "dict": u"json类型",
    "basestring": u"字符串类型",
    "str": u"字符串类型",
    "bool": u"布尔值",
    "datetime.datetime": u"时间类型",
    "unicode": u"字符串类型",
    "float": u"浮点数类型"
}


def validate_ipaddress(ip):
    status, msg = check_ip(ip)
    if not status:
        raise exception_common.ValueValidateError("ip", msg)


def validate_column_line(column):
    if re.match(r'^[0-9a-zA-Z_]{1,36}$', column):
        return True
    else:
        raise exception_common.RequestValidateError("不合法字段 %s" % column)


def validate_resource_id(rid):
    if re.match(r'^[.0-9a-zA-Z_-]{1,36}$', rid):
        return True
    else:
        raise exception_common.ResourceNotFoundError()


def format_type_to_chinese(type):
    for ixe in args_type.keys():
        if type == eval(ixe):
            return args_type.get(ixe)


def str_to_time(key, date_str):
    try:
        if ":" in date_str:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except:
        raise exception_common.ValueValidateError(param=key, msg=u"非法值 %s，不是合法的时间" % date_str)


def validate_port(port, min=None, max=None, permit_null=False):
    if permit_null:
        if not port and port != 0:
            return 0

    try:
        port = int(port)
    except:
        raise exception_common.ValueValidateError(param="port", msg=u"%s 非法的端口号" % port)

    min = min or 1
    max = max or 65535
    if port < min or port > max:
        raise exception_common.ValueValidateError(param="port", msg=u"%s 非法的端口号" % port)

    return port


def validate_email_address(email_address):
    if re.match(r'^[.0-9a-zA-Z_-]{0,19}@[0-9a-zA-Z]{1,13}\.[comnet]{1,3}$', email_address):
        if email_address.endswith("com") or email_address.endswith("net") or email_address.endswith("cn"):
            return True

    raise exception_common.ValueValidateError(param="email", msg=u"非法值 %s，不是合法的邮件地址" % email_address)


def not_allowed_null(keys, data):
    for key in keys:
        if not data.get(key):
            raise ValueError("参数%s 不能为null" % key)


def allowed_key(keys, data):
    for key in keys:
        if key not in data:
            raise ValueError("不合法的参数%s" % key)


def validate_string(key, value, minlen=None, maxlen=None):
    if value == "" or value is None:
        return
    if not isinstance(value, basestring):
        raise ValueError("%s 不是合法类型string" % key)
    if minlen and len(value) < minlen:
        raise ValueError("%s 长度不能小于 %s" % (key, minlen))
    if maxlen and len(value) > maxlen:
        raise ValueError("%s 长度不能大于 %s" % (key, maxlen))

    return value


def validate_list(key, value, minlen=None, maxlen=None):
    if not value:
        return []
    if not isinstance(value, list):
        raise ValueError("%s 不是合法类型list" % key)
    if minlen and len(value) < minlen:
        raise ValueError("%s 长度不能小于 %s" % (key, minlen))
    if maxlen and len(value) > maxlen:
        raise ValueError("%s 长度不能大于 %s" % (key, maxlen))

    return value


def validate_dict(key, value, minlen=None, maxlen=None):
    if value is None:
        return {}
    try:
        if isinstance(value, basestring):
            value = json.loads(value)
    except:
        raise ValueError("%s 不是json" % key)

    if not isinstance(value, dict):
        raise ValueError("%s 不是合法类型json" % key)

    if minlen and len(value) < minlen:
        raise ValueError("%s 长度不能小于 %s" % (key, minlen))
    if maxlen and len(value) > maxlen:
        raise ValueError("%s 长度不能大于 %s" % (key, maxlen))

    return value


def validate_bool(key, value, default=None):
    if value is None:
        value = value or default
    else:
        if not isinstance(value, bool):
            raise ValueError("%s 不是合法类型bool" % key)

    return value


def validate_number(key, value, min=None, max=None):
    try:
        if isinstance(value, basestring):
            if "." in value:
                value = float(value)
            else:
                value = int(value)
    except:
        raise ValueError("%s 不是合法类型" % key)

    if min and value < min:
        raise ValueError("%s 不能小于 %s" % (key, min))
    if max and value > max:
        raise ValueError("%s 不能大于 %s" % (key, max))

    return value


def validate_int(key, value, min=None, max=None):
    try:
        if not isinstance(value, int):
            value = int(value)
    except:
        raise ValueError("%s 不是合法整数类型" % key)

    if min and value < min:
        raise ValueError("%s 不能小于 %s" % (key, min))
    if max and value > max:
        raise ValueError("%s 不能大于 %s" % (key, max))

    return value
