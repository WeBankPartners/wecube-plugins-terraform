# _*_ coding:utf-8 _*_

import base64
import binascii
import traceback
import jwt
import local_exceptions
from lib.logs import logger
from wecube_plugins_terraform.settings import JWT_KEY, DEBUG


def b64decode_key(key):
    new_key = key
    max_padding = 3
    while max_padding > 0:
        try:
            return base64.b64decode(new_key)
        except (binascii.Error, TypeError) as e:
            new_key += '='
            max_padding -= 1
            if max_padding <= 0:
                raise e


if not DEBUG:
    jwt_key = b64decode_key(JWT_KEY)
else:
    jwt_key = ''


def jwt_request(request):
    _token = request.META.get("HTTP_AUTHORIZATION", None)
    if _token:
        try:
            token = _token[len("Bearer "):]
            return jwt.decode(token, jwt_key, verify=True)
        except Exception, e:
            logger.info(traceback.format_exc())
            raise local_exceptions.AuthExceptionError("认证失败")
    else:
        raise local_exceptions.AuthExceptionError("认证失败")
