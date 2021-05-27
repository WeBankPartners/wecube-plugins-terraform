# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.apibase import ApiBase
from apps.api.apibase_backend_v2 import ApiBackendBase


class VpcApi(ApiBase):
    def __init__(self):
        super(VpcApi, self).__init__()
        self.resource_name = "vpc"
        self.resource_workspace = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None

    def generate_create_data(self, zone, create_data, **kwargs):
        create_data = {"cidr": create_data.get("cidr"),
                       "name": create_data.get("name")}
        return create_data, {}


class VpcBackendApi(ApiBackendBase):
    def __init__(self):
        super(VpcBackendApi, self).__init__()
        self.resource_name = "vpc"
        self.resource_workspace = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None
