# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.apibase import ApiBase
from apps.api.apibase_backend import ApiBackendBase


class LBCertificateApi(ApiBase):
    def __init__(self):
        super(LBCertificateApi, self).__init__()
        self.resource_name = "lb_certificate"
        self.resource_workspace = "lb_certificate"
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
        for key in ["name", "private_key", "public_key"]:
            x_create_data[key] = create_data.get(key)
        return x_create_data, r_create_data

    def generate_owner_data(self, create_data, **kwargs):
        owner_id = None
        return owner_id, None


class LBCertificateBackendApi(ApiBackendBase):
    def __init__(self):
        super(LBCertificateBackendApi, self).__init__()
        self.resource_name = "lb_certificate"
        self.resource_workspace = "lb_certificate"
        self._flush_resobj()
        self.resource_keys_config = None
