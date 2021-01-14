# _*_ coding:utf-8 _*_


from __future__ import (absolute_import, division, print_function, unicode_literals)

from .backend_response import BackendManager as _BackendManager_
from .backend_response import BackendIdManager as _BackendIdManager_
from .response_hooks import ResponseController as _ResponseController_


class BaseController(_ResponseController_):
    name = None
    resource = None
    allow_methods = ('POST',)

    def __call__(self, request, **kwargs):
        return self.request_response(request=request, **kwargs)


class BackendController(_BackendManager_):
    name = None
    resource = None
    allow_methods = ('GET', 'POST')

    def __call__(self, request, **kwargs):
        return self.request_response(request=request, **kwargs)


class BackendIdController(_BackendIdManager_):
    name = None
    resource = None
    allow_methods = ('GET', 'PATCH', 'DELETE')

    def __call__(self, request, **kwargs):
        return self.request_response(request=request, **kwargs)
