# coding=utf8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import time
from lib.logs import logger


def logger_middleware(get_response):
    '''
    :param get_response:
    :return:
    '''

    # One-time configuration and initialization.

    def middleware(request):
        start_time = time.time()
        response = get_response(request)
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE,PATCH"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "content-type,x-auth-token"
        post_data = dict(request.POST)
        if 'password' in dict(request.POST):
            post_data["password"] = "xxxxxxxx"

        logmsg = {'method': request.method,
                  'time': time.time() - start_time,
                  'code': response.status_code,
                  'url': request.path,
                  'GET': dict(request.GET),
                  'POST': post_data
                  }
        if not request.path.startswith('/static') and request.method != 'OPTIONS':
            logger.info('%(method)s  %(code)s  "%(url)s"  GET:%(GET)s  POST:%(POST)s  cost:%(time).4fs' % logmsg)
        return response

    return middleware
