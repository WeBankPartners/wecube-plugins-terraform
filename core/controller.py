# _*_ coding:utf-8 _*_


from __future__ import (absolute_import, division, print_function, unicode_literals)

from .backend_response import BackendManager, BackendIdManager
from .response_hooks import ResponseController


class BaseController(ResponseController):
    name = None
    resource = None
    allow_methods = ('POST',)

    def __call__(self, request, **kwargs):
        return self.request_response(request=request, **kwargs)


class BackendController(BackendManager):
    name = None
    resource = None
    allow_methods = ('GET', 'POST')

    def __call__(self, request, **kwargs):
        return self.request_response(request=request, **kwargs)


class BackendIdController(BackendIdManager):
    name = None
    resource = None
    allow_methods = ('GET', 'PATCH', 'DELETE')

    def __call__(self, request, **kwargs):
        return self.request_response(request=request, **kwargs)
