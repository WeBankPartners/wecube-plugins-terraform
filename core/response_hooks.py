# _*_ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import copy
import json
import traceback
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from wecube_plugins_terraform.settings import DEBUG
from core import local_exceptions as exception_common
from core.validation import validate_column_line
from lib.classtools import get_all_class_for_module
from lib.json_helper import format_json_dumps
from lib.logs import logger
from lib.uuid_util import get_uuid
from .auth import jwt_request

content_type = 'application/json,charset=utf-8'
exception_common_classes = get_all_class_for_module(exception_common)


def format_string(data):
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = format_json_dumps(value)
        else:
            result[key] = str(value)

    return result


class ResponseController(object):
    name = None
    allow_methods = tuple()
    requestId = ""
    requestUser = "Unknown"
    resource = None

    def run_post(self, request, data, **kwargs):
        if not isinstance(data, list):
            raise exception_common.RequestValidateError("inputs 不支持的请求数据类型")

        return self.on_create(request, data, **kwargs)

    def on_create(self, request, datas, **kwargs):
        response_data = {"resultCode": "0", "resultMessage": "success", "results": {"outputs": []}}
        outputs = []
        for data in datas:
            self.before_handler(request, data, **kwargs)

        for data in datas:
            _res = {"errorCode": "0", "errorMessage": ""}
            _res["callbackParameter"] = data.pop("callbackParameter", "")
            try:
                res = self.main_response(request, data, **kwargs)
                if not res:
                    res = self.response_templete(data)

                if isinstance(res, list):
                    _t = []
                    for _result in res:
                        _res.update(_result)
                        _tmp = copy.deepcopy(_res)
                        _t.append(_tmp)

                    outputs += _t
                else:
                    _res.update(res)
                    outputs.append(format_string(_res))
            except Exception, e:
                _res["errorCode"] = "1"
                _res["errorMessage"] = e.__class__.__name__
                response_data["resultCode"] = "1"
                if e.__class__.__name__ in ['UnicodeDecodeError', 'ValueError', 'TypeError', "KeyError",
                                            'ResourceNotCompleteError', "ResourceNotSearchError",
                                            'AllowedForbidden', 'RequestDataTooBig', 'DataToolangError',
                                            'ResourceNotFoundError', 'AuthFailedError', 'TerrformExecError']:
                    response_data["resultMessage"] = "type: %s, info: %s" % (e.__class__.__name__, e.message)
                elif e.__class__.__name__ in exception_common_classes:
                    response_data["resultMessage"] = "type: %s, info: %s" % (e.__class__.__name__, e.message)
                else:
                    response_data["resultMessage"] = "type: %s" % (e.__class__.__name__)
                logger.info(traceback.format_exc())
                _res.update(self.response_templete(data))
                outputs.append(format_string(_res))

        response_data["results"]["outputs"] = outputs
        return response_data

    def response_templete(self, data):
        return {}

    def before_handler(self, request, data, **kwargs):
        pass

    def main_response(self, request, data, **kwargs):
        return self.resource.create(data)

    def _validate_column(self, data):
        if isinstance(data, list):
            raise exception_common.RequestValidateError("不支持的数据类型")
        elif isinstance(data, dict):
            for cid, value in data.items():
                validate_column_line(cid)
        else:
            raise exception_common.RequestValidateError("未知请求数据类型")

    def handler_http(self, request, **kwargs):
        data = request.body
        try:
            data = json.loads(data)
        except:
            raise exception_common.RequestValidateError("请求参数不为json")

        self.requestId = data.get("requestId") or "req_%s" % get_uuid()
        self._trace_req(request)
        self._validate_column(data)

        try:
            data = data["inputs"]
        except:
            logger.info(traceback.format_exc())
            raise exception_common.RequestValidateError("非法的请求数据格式")

        result = self.run_post(request, data, **kwargs)
        return format_json_dumps(result)

    def auth_method(self, request):
        method = request.method.upper()
        if method in self.allow_methods:
            return True
        else:
            return False

    def format_err(self, errcode, errtype, errinfo, return_data=None):
        if isinstance(errinfo, Exception):
            errorMessage = "type: %s, info: %s" % (errtype, errinfo.message)
        else:
            errorMessage = "type: %s, info: %s" % (errtype, errinfo)

        msg = {"resultCode": "1",
               "resultMessage": errorMessage,
               "results": {"outputs": []}
               }

        return json.dumps(msg, ensure_ascii=False)

    def _trace_req(self, request):
        try:
            data = request.body if request.method.upper() in ['POST', 'PATCH'] else request.GET
            if isinstance(data, (dict, list)):
                data = format_json_dumps(data)
            logger.info("[%s] [RE] [%s]- %s %s %s " % (self.requestId, self.requestUser,
                                                       request.method.upper(), request.path, data))
        except:
            logger.info(traceback.format_exc())

    def trace_log(self, request, msg):
        try:
            if isinstance(msg, (dict, list)):
                msg = format_json_dumps(msg)

            logger.info("[%s] [RP] [%s]- %s %s %s" % (self.requestId, self.requestUser,
                                                      request.method.upper(), request.path, msg))
        except:
            logger.info(traceback.format_exc())

    def exception_response(self, e):
        if e.__class__.__name__ in ['UnicodeDecodeError']:
            status_code = 400
            errmsg = self.format_err(400, "DataError", "字符错误， 原因：请使用UTF-8编码")
            response_res = HttpResponse(status=status_code, content=errmsg, content_type=content_type)
        elif e.__class__.__name__ in ['ValueError', 'TypeError', "KeyError"]:
            status_code = 400
            errmsg = self.format_err(400, "ValueError", "字符错误， 原因：%s" % e.message)
            response_res = HttpResponse(status=status_code, content=errmsg, content_type=content_type)
        elif e.__class__.__name__ in ['AuthFailedError']:
            status_code = 401
            errmsg = self.format_err(401, "UserAuthError", e)
            response_res = HttpResponse(status=status_code, content=errmsg, content_type=content_type)
        elif e.__class__.__name__ in ['AllowedForbidden']:
            status_code = 403
            errmsg = self.format_err(403, "AllowedForbidden", e)
            response_res = HttpResponse(status=status_code, content=errmsg, content_type=content_type)
        elif e.__class__.__name__ in exception_common_classes:
            errmsg = self.format_err(e.status_code, e.__class__.__name__, e)
            response_res = HttpResponse(status=e.status_code, content=errmsg, content_type=content_type)
        else:
            status_code = 500
            errmsg = self.format_err(status_code, "SericeError", "服务器遇到异常")
            response_res = HttpResponse(status=status_code, content=errmsg, content_type=content_type)
        return response_res

    def request_response(self, request, **kwargs):
        method = request.method
        if method == "OPTIONS":
            return HttpResponse(str(self.allow_methods))
        else:
            if request.method.upper() == "POST":
                res = self._request_response(request, **kwargs)
                res.setdefault("ReqID", self.requestId)

                try:
                    _traceres = res.content.decode("utf-8")
                except:
                    _traceres = res.content

                self.trace_log(request, msg=(str(res.status_code) + " data: %s " % _traceres))
                return res
            else:
                return HttpResponseNotAllowed(["POST"],
                                              content=self.format_err(405, "HttpMethodsNotAllowed", "POST"),
                                              content_type=content_type)

    def _is_platform(self, jwt_info):
        if jwt_info.get("sub") != "SYS_PLATFORM":
            raise exception_common.AllowedForbidden("AllowedForbidden")
        if "SUB_SYSTEM" not in jwt_info.get("authority"):
            raise exception_common.AllowedForbidden("AllowedForbidden")

    def _request_response(self, request, **kwargs):
        try:
            if not DEBUG:
                jwt_info = jwt_request(request)
                self._is_platform(jwt_info)
                self.requestUser = jwt_info.get("sub")

            res = HttpResponse(content=self.handler_http(request=request, **kwargs),
                               status=200,
                               content_type=content_type)
        except Exception, e:
            logger.info(traceback.format_exc())
            logger.info(e.message)
            res = self.exception_response(e)
        return res
