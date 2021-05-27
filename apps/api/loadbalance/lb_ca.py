# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.apibase import ApiBase
from apps.api.apibase_backend import ApiBackendBase


class LBCAApi(ApiBase):
    def __init__(self):
        super(LBCAApi, self).__init__()
        self.resource_name = "lb_ca"
        self.resource_workspace = "lb_ca"
        self._flush_resobj()
        self.resource_keys_config = None

    def before_keys_checks(self, provider, create_data, is_update=None):
        '''

        :param provider:
        :param lb_id:
        :param listener_id:
        :return:
        '''
        return {}

    def generate_create_data(self, zone, create_data, **kwargs):
        r_create_data = {}

        x_create_data = {}
        for key in ["ca_certificate", "name"]:
            x_create_data[key] = create_data.get(key)
        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None


class LBCABackendApi(ApiBackendBase):
    def __init__(self):
        super(LBCABackendApi, self).__init__()
        self.resource_name = "lb_ca"
        self.resource_workspace = "lb_ca"
        self._flush_resobj()
        self.resource_keys_config = None
