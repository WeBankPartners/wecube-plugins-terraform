# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.apibase import ApiBase
from apps.api.apibase_backend import ApiBackendBase


class CCNApi(ApiBase):
    def __init__(self):
        super(CCNApi, self).__init__()
        self.resource_name = "ccn"
        self.resource_workspace = "ccn"
        self._flush_resobj()
        self.resource_keys_config = None

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {}
        create_data = {
            "name": create_data.get("name")
        }

        return create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None


class CCNBackendApi(ApiBackendBase):
    def __init__(self):
        super(CCNBackendApi, self).__init__()
        self.resource_name = "ccn"
        self.resource_workspace = "ccn"
        self._flush_resobj()
        self.resource_keys_config = None
