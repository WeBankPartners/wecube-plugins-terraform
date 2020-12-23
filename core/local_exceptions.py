# coding=utf8

from __future__ import (absolute_import, division, print_function, unicode_literals)


class AppBaseException(Exception):
    status_code = 404

    def __init__(self, message):
        super(AppBaseException, self).__init__(message)

    def __repr__(self):
        pass


class HttpMethodsNotAllowed(Exception):
    status_code = 405

    def __repr__(self):
        pass


class AuthExceptionError(Exception):
    status_code = 401

    def __repr__(self):
        pass


class AuthFailedError(Exception):
    status_code = 401

    def __init__(self, msg):
        _msg = "认证失败， 原因： %s" % (msg)
        super(AuthFailedError, self).__init__(_msg)


class AllowedForbidden(Exception):
    status_code = 403

    def __init__(self, msg):
        _msg = "拒绝访问， 原因： %s" % (msg)
        super(AllowedForbidden, self).__init__(_msg)


class ResourceNotFoundError(Exception):
    status_code = 404

    def __repr__(self):
        pass


class ResourceConfigError(Exception):
    status_code = 400

    def __init__(self, msg):
        _msg = "资源配置异常， 原因： %s" % (msg)
        super(ResourceConfigError, self).__init__(_msg)


class ResourceNotSearchError(Exception):
    status_code = 400

    def __init__(self, param, msg, return_data):
        self.return_data = return_data
        _msg = "资源 %s %s未找到" % (param, msg)
        super(ResourceNotSearchError, self).__init__(_msg)

class ResourceOpearateNotSuccess(Exception):
    status_code = 400

    def __init__(self, param, msg, return_data):
        self.return_data = return_data
        _msg = "资源 %s %s 操作失败" % (param, msg)
        super(ResourceOpearateNotSuccess, self).__init__(_msg)


class DataToolangError(Exception):
    status_code = 403

    def __init__(self, msg):
        _msg = "请求错误， 原因： %s" % (msg)
        super(DataToolangError, self).__init__(_msg)


class ResourceIsFoundError(Exception):
    status_code = 400

    def __repr__(self):
        pass


class ServerIsBusy(AppBaseException):
    status_code = 400

    def __init__(self, msg=None):
        if msg:
            _msg = "服务器 %s，请稍后再试" % msg
        else:
            _msg = "服务器忙碌中，请稍后再试"
        super(ServerIsBusy, self).__init__(_msg)


class ResoucrAddError(AppBaseException):
    status_code = 400

    def __init__(self, msg=None):
        if not msg:
            msg = "资源添加失败" % msg

        super(ResoucrAddError, self).__init__(msg)


class ObjectIsNotExistedException(AppBaseException):
    status_code = 404


class ObjectExistedException(AppBaseException):
    status_code = 400

    def __init__(self, param, msg):
        _msg = "资源 %s 已存在， 原因： %s" % (param, msg)
        super(ObjectExistedException, self).__init__(_msg)


class ResourceUniqueException(AppBaseException):
    status_code = 400

    def __init__(self, param, value):
        _msg = "参数 %s 校验错误， 原因： %s 必须唯一" % (param, value)
        super(ResourceUniqueException, self).__init__(_msg)


class ResourceOperateException(AppBaseException):
    status_code = 400

    def __init__(self, param, msg):
        _msg = "资源 %s 操作错误， 原因： %s" % (param, msg)
        super(ResourceOperateException, self).__init__(_msg)


class OperateTooFastException(AppBaseException):
    status_code = 400

    def __init__(self, param, msg):
        _msg = "资源 %s 操作过快， 原因： %s" % (param, msg)
        super(OperateTooFastException, self).__init__(_msg)


class ValueValidateError(Exception):
    status_code = 400

    def __init__(self, param, msg):
        _msg = "参数 %s 校验错误， 原因： %s" % (param, msg)
        super(ValueValidateError, self).__init__(_msg)


class ResourceValidateError(Exception):
    status_code = 400

    def __init__(self, param, msg):
        _msg = "资源 %s 校验错误， 原因： %s" % (param, msg)
        super(ResourceValidateError, self).__init__(_msg)


class ResourceNotEnoughError(Exception):
    status_code = 400

    def __init__(self, param, msg):
        _msg = "资源 %s 容量不足， 原因： %s" % (param, msg)
        super(ResourceNotEnoughError, self).__init__(_msg)


class ResourceNotAttachError(Exception):
    status_code = 400

    def __init__(self, param, msg):
        _msg = "资源 %s 挂载异常， 原因： %s" % (param, msg)
        super(ResourceNotAttachError, self).__init__(_msg)


class ResourceNotCompleteError(Exception):
    status_code = 400

    def __init__(self, param, msg, return_data):
        self.return_data = return_data
        _msg = "部分资源 %s 创建未完成， 原因： %s" % (param, msg)
        super(ResourceNotCompleteError, self).__init__(_msg)


class ArgsError(Exception):
    status_code = 400

    def __init__(self, msg):
        _msg = "参数 错误， 原因： %s" % (msg)
        super(ArgsError, self).__init__(_msg)


class RequestValidateError(Exception):
    status_code = 400

    def __init__(self, msg):
        _msg = "请求校验错误， 原因： %s" % (msg)
        super(RequestValidateError, self).__init__(_msg)


class UserAuthError(Exception):
    status_code = 401

    def __init__(self, param, msg):
        _msg = "用户 %s 认证失败， 原因： %s" % (param, msg)
        super(UserAuthError, self).__init__(_msg)
