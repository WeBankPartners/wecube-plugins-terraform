# _ coding:utf-8 _*_
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import subprocess
import traceback
from lib.logs import logger


def command(cmd, workdir=None):
    environ_vars = os.environ.copy()
    logger.info("[EXEC CMD]: %s" % cmd)
    try:
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   close_fds=True,
                                   executable='/bin/bash',
                                   cwd=workdir,
                                   env=environ_vars)
        out, err = process.communicate()
        ret_code = process.returncode
        logger.info("[RESULT CMD]: %s  %s %s" % (ret_code, out, err))
        return ret_code, out, err
    except Exception, e:
        logger.info(traceback.format_exc())
        logger.info("%s: %s" % (e.__class__.__name__, e.message))
        return 1, "", "%s: %s" % (e.__class__.__name__, e.message)
