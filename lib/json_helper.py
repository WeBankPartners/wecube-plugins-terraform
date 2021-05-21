# coding=utf8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from datetime import date, datetime


def __default(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    else:
        raise TypeError('%r is not JSON serializable' % obj)


def format_dict_data(data):
    return json.loads(data, default=__default)


def format_json_dumps(data, ensure_ascii=False, indent=None):
    return json.dumps(data, default=__default, ensure_ascii=ensure_ascii, indent=indent)


def format_to_json(data):
    if isinstance(data, dict):
        res = json.dumps(data, default=__default)
        return json.loads(res)
    else:
        return json.loads(data)
