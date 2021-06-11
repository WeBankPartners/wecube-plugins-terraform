# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.network.ip_group import IpGroupBackendApi
from apps.controller.backend_controller import BackendAddController
from apps.controller.backend_controller import BackendDeleteController
from apps.controller.backend_controller import BackendSourceController


class IpGroupAddController(BackendAddController):
    allow_methods = ("POST",)
    resource = IpGroupBackendApi()


class IpGroupDeleteController(BackendDeleteController):
    name = "IpGroup"
    resource_describe = "IpGroup"
    allow_methods = ("POST",)
    resource = IpGroupBackendApi()


class IpGroupSourceController(BackendSourceController):
    name = "IpGroup"
    resource_describe = "IpGroup"
    allow_methods = ("POST",)
    resource = IpGroupBackendApi()
