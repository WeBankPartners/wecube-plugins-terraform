# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.apibase import ApiBase
from apps.api.apibase_backend import ApiBackendBase


class IpGroupBackendApi(ApiBackendBase):
    def __init__(self):
        super(IpGroupBackendApi, self).__init__()
        self.resource_name = "ipaddress_group"
        self.resource_workspace = "ipaddress_group"
        self._flush_resobj()
        self.resource_keys_config = None
