# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.uuid_util import get_uuid
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.common.convert_keys import validate_type
from apps.common.convert_keys import convert_key_only
from apps.common.convert_keys import define_relations_key
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject
from apps.api.apibase_backend import ApiBackendBase


class Common(object):
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


class LBCertificateApi(Common, ApiBase):
    def __init__(self):
        super(LBCertificateApi, self).__init__()
        self.resource_name = "lb_certificate"
        self.resource_workspace = "lb_certificate"
        self._flush_resobj()
        self.resource_keys_config = None


class LBCertificateBackendApi(Common, ApiBackendBase):
    def __init__(self):
        super(LBCertificateBackendApi, self).__init__()
        self.resource_name = "lb_certificate"
        self.resource_workspace = "lb_certificate"
        self._flush_resobj()
        self.resource_keys_config = None
