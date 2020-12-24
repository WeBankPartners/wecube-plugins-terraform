# _*_ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback

from django.http import HttpResponse
from django.http import HttpResponseNotAllowed

from core import local_exceptions as exception_common
from core import validation
from core.validation import validate_column_line
from lib.classtools import get_all_class_for_module
from lib.json_helper import format_json_dumps
from lib.logs import logger
from lib.uuid_util import get_uuid

# from .auth import jwt_request

content_type = 'application/json,charset=utf-8'
exception_common_classes = get_all_class_for_module(exception_common)


class BackendResponse(object):
    allow_methods = tuple()
    requestId = ""
    resource = None

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        return self.resource.list(data, orderby=orderby, page=page, pagesize=pagesize)

    def show(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.show(rid, where_and=data)

    def create(self, request, data, **kwargs):
        return self.resource.create(data)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.delete(rid, where_and=data)

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.update(rid, data, where_and=data)

    def on_create(self, request, **kwargs):
        try:
            data = json.loads(request.body)
        except:
            raise exception_common.RequestValidateError("请求参数不为json")

        self.requestId = data.get("requestId") or "req_%s" % get_uuid()
        self._trace_req(request)
        self._validate_column(data)

        self.before_handler(request, data, **kwargs)
        count, result = self.create(request, data, **kwargs)
        return {"count": count, "data": result}

    def build_filters(self, data):
        pagesize = data.pop("pagesize", None)
        page = data.pop("page", 1)
        oder_key = data.pop("oder_key", None)
        oder_as = data.pop("oder_as", 'asc')

        if pagesize:
            pagesize = validation.validate_int("pagesize", pagesize, min=1)
            page = validation.validate_int("page", page, min=1)
            page -= page
            PAGINATION = {'pagesize': pagesize, 'page': page}
        else:
            PAGINATION = {}

        if oder_as not in ['asc', 'desc']:
            raise exception_common.ValueValidateError(param="oder_as", msg=("非法值 %s, 允许值： asc 或 desc"))
        if oder_key:
            validate_column_line(oder_key)
            ORDER = [[oder_key, oder_as]]
        else:
            ORDER = []
        res = {"orderby": ORDER, "data": data}
        res.update(PAGINATION)
        return res

    def on_get(self, request, **kwargs):
        data = request.GET
        data = self.build_filters(data.dict())
        count, res = self.list(request, **data)
        return {"count": count, "data": res}

    def on_id_get(self, request, **kwargs):
        if len(request.META.get("QUERY_STRING", "")) > 2048:
            raise exception_common.DataToolangError(msg="请求URL过长")

        data = request.GET
        res = self.show(request, data.dict(), **kwargs)
        if not res:
            raise exception_common.ResourceNotFoundError()
        return res

    def on_delete(self, request, **kwargs):
        data = request.GET
        res = self.delete(request, data.dict(), **kwargs)
        if not res:
            raise exception_common.ResourceNotFoundError()
        return {"data": res}

    def on_patch(self, request, **kwargs):
        try:
            data = json.loads(request.body)
        except:
            raise exception_common.RequestValidateError("请求参数不为json")

        for cid, value in data.items():
            validate_column_line(cid)

        self.before_handler(request, data, **kwargs)
        count, res = self.update(request, data, **kwargs)
        if not res:
            raise exception_common.ResourceNotFoundError()
        return {"count": count, "data": res}

    def before_handler(self, request, data, **kwargs):
        pass

    def _validate_column(self, data):
        if isinstance(data, list):
            raise exception_common.RequestValidateError("不支持的数据类型")
        elif isinstance(data, dict):
            for cid, value in data.items():
                validate_column_line(cid)
        else:
            raise exception_common.RequestValidateError("未知请求数据类型")

    def _trace_req(self, request):
        try:
            data = request.body if request.method.upper() in ['POST', 'PATCH'] else request.GET
            if isinstance(data, (dict, list)):
                data = format_json_dumps(data)
            logger.info("[%s] [RE] - %s %s %s " % (self.requestId, request.method.upper(), request.path, data))
        except:
            logger.info(traceback.format_exc())

    def format_response(self, data):
        return format_json_dumps({"status": "OK", "message": "OK", "code": 0, "data": data})

    def format_err(self, errcode, errtype, errinfo, return_data=None):
        if isinstance(errinfo, Exception):
            errorMessage = "type: %s, info: %s" % (errtype, errinfo.message)
        else:
            errorMessage = "type: %s, info: %s" % (errtype, errinfo)

        msg = {"status": "ERROR", "message": errorMessage, "code": errcode, "data": None}
        return json.dumps(msg, ensure_ascii=False)

    def request_response(self, request, **kwargs):
        if request.method.upper() == "OPTIONS":
            return HttpResponse(str(self.allow_methods))
        else:
            if request.method.upper() in self.allow_methods:
                res = self._request_response(request, **kwargs)
                res.setdefault("ReqID", self.requestId)
                self.trace_log(request, res)
                return res
            else:
                return HttpResponseNotAllowed(self.allow_methods,
                                              content=self.format_err(405, "HttpMethodsNotAllowed",
                                                                      ",".join(self.allow_methods)),
                                              content_type=content_type)

    def handler_http(self, request, **kwargs):
        raise NotImplementedError()

    def _request_response(self, request, **kwargs):
        try:
            # jwt_request(request)
            res = HttpResponse(content=self.handler_http(request=request, **kwargs),
                               status=200,
                               content_type=content_type)
        except Exception, e:
            logger.info(traceback.format_exc())
            logger.info(e.message)
            res = self.exception_response(e)
        return res

    def trace_log(self, request, res):
        try:
            _traceres = res.content.decode("utf-8")
        except:
            _traceres = res.content

        try:
            logger.info("[%s] [RP] - %s %s %s" % (self.requestId, request.method.upper(),
                                                  request.path, (str(res.status_code) + " data: %s " % _traceres)))
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
        elif e.__class__.__name__ in exception_common_classes:
            errmsg = self.format_err(e.status_code, e.__class__.__name__, e)
            response_res = HttpResponse(status=e.status_code, content=errmsg, content_type=content_type)
        else:
            status_code = 500
            errmsg = self.format_err(status_code, "SericeError", "服务器遇到异常")
            response_res = HttpResponse(status=status_code, content=errmsg, content_type=content_type)
        return response_res


class BackendManager(BackendResponse):
    def handler_http(self, request, **kwargs):
        method = request.method.upper()
        if method == "GET":
            return self.format_response(self.on_get(request, **kwargs))
        elif method == "POST":
            return self.format_response(self.on_create(request, **kwargs))
        else:
            raise exception_common.HttpMethodsNotAllowed()


class BackendIdManager(BackendResponse):
    def handler_http(self, request, **kwargs):
        method = request.method.upper()
        if method == "GET":
            return self.format_response(self.on_id_get(request, **kwargs))
        elif method == "PATCH":
            return self.format_response(self.on_patch(request, **kwargs))
        elif method == "DELETE":
            return self.format_response(self.on_delete(request, **kwargs))
        else:
            raise exception_common.HttpMethodsNotAllowed()
