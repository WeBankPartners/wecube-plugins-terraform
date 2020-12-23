# -*- coding:utf-8 -*-

import functools
import inspect
import time


def get_all_class_for_module(module_name):
    classes = []
    for name, obj in inspect.getmembers(module_name):
        if inspect.isclass(obj):
            classes.append(name)
    return classes


def retry(times=3, sleep_time=3):
    def wrap(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            for i in range(0, times):
                try:
                    return f(*args, **kwargs)
                except:
                    time.sleep(sleep_time)
            raise

        return inner

    return wrap
