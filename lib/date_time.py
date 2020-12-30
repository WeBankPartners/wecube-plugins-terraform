# coding=utf8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import time
import datetime


def get_datetime_str():
    return time.strftime("%Y-%m-%d %X")


def get_date_ymd_str():
    return time.strftime("%Y-%m-%d")


def get_datetime_point_str():
    return time.strftime("%Y%m%d_%H%M%S")


def datetime_to_str(the_datetime):
    return the_datetime.strftime("%Y-%m-%d %H:%M:%S")


def time_add(datepoint, day=0, hour=0, mins=0, sec=0):
    if ":" in datepoint:
        return datetime.datetime.strptime(
            datepoint,
            '%Y-%m-%d %H:%M:%S') + datetime.timedelta(
            days=day,
            hours=hour,
            minutes=mins,
            seconds=sec)
    else:
        return datetime.datetime.strptime(datepoint,
                                          '%Y-%m-%d') + datetime.timedelta(days=day,
                                                                           hours=hour,
                                                                           minutes=mins,
                                                                           seconds=sec)


def time_reduce(datepoint, day=0, hour=0, mins=0, sec=0):
    if ":" in datepoint:
        return datetime.datetime.strptime(
            datepoint,
            '%Y-%m-%d %H:%M:%S') - datetime.timedelta(
            days=day,
            hours=hour,
            minutes=mins,
            seconds=sec)
    else:
        return datetime.datetime.strptime(datepoint,
                                          '%Y-%m-%d') - datetime.timedelta(days=day,
                                                                           hours=hour,
                                                                           minutes=mins,
                                                                           seconds=sec)


def time_add_ymd(datepoint, day=0, hour=0, mins=0, sec=0):
    t = time_add(datepoint, day, hour, mins, sec)
    return t.strftime("%Y-%m-%d")


def time_reduce_ymd(datepoint, day=0, hour=0, mins=0, sec=0):
    t = time_reduce(datepoint, day, hour, mins, sec)
    return t.strftime("%Y-%m-%d")


def datetime_to_timestamp(the_datetime, is_float=False):
    ms = time.mktime(the_datetime.timetuple())
    if not is_float:
        ms = int(ms)
    return ms


def timestamp_to_date_str(ts):
    '''
    timestamp 转日期字符串
    :param ts:
    :return:
    '''
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def is_time_str(date_str):
    try:
        if ":" in date_str:
            datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        else:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except:
        return False


def str_to_time(date_str):
    if ":" in date_str:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')


# if __name__ == '__main__':
#     print time_add_ymd(datepoint=get_date_ymd_str(), day=4)

if __name__ == '__main__':
    # import iso8601
    s = get_datetime_str()
    print(s)
    print(time_add(s, day=1))
    # print datetime.datetime.strptime('2012-11-01 04:16:13', '%Y-%m-%d %H:%M:%S')
    # print datetime.datetime.fromisoformat("2020-05-12T08:00:00.000+0800")
