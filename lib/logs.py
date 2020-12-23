# coding=utf8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import logging
import logging.config
import logging.handlers
import threading
from wecube_plugins_terraform.settings import DEBUG
from wecube_plugins_terraform.settings import LOG_BACKUP
from wecube_plugins_terraform.settings import LOG_BASE_PATH
from wecube_plugins_terraform.settings import LOG_LEVEL
from wecube_plugins_terraform.settings import LOG_MAX_SIZE
from wecube_plugins_terraform.settings import LOG_NAME

levelmap = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

if not os.path.exists(LOG_BASE_PATH):
    os.makedirs(LOG_BASE_PATH)


def singleton(cls):
    instances = {}
    lock = threading.Lock()

    def _singleton(*args, **kwargs):
        with lock:
            fullkey = str((cls.__name__, tuple(args), tuple(kwargs.items())))
            if fullkey not in instances:
                instances[fullkey] = cls(*args, **kwargs)
        return instances[fullkey]

    return _singleton


@singleton
def logsetup(logname=None):
    filename = os.path.join(LOG_BASE_PATH, logname)
    handler = logging.handlers.RotatingFileHandler(filename=filename, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP)
    logging.getLogger(logname).setLevel(levelmap.get(LOG_LEVEL, logging.INFO))
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s-L%(lineno)d] - %(message)s")
    handler.setFormatter(formatter)
    logging.getLogger(logname).addHandler(handler)

    if DEBUG:
        console = logging.StreamHandler()
        handler.setFormatter(formatter)
        logging.getLogger("").addHandler(console)


def get_logger(logname=None):
    logname = logname or LOG_NAME
    logsetup(logname)
    return logging.getLogger(logname)


logger = get_logger()
