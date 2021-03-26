# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from core import local_exceptions
from lib.json_helper import format_json_dumps
from lib.logs import logger
from apps.api.apibase import ApiBase
from apps.api.apibase_backend import ApiBackendBase


class _Common_(object):
    @staticmethod
    def generate_create_data(zone, create_data, **kwargs):
        create_data = {"cidr": create_data.get("cidr"),
                       "name": create_data.get("name")}
        return create_data, {}


class VpcApi(ApiBase):
    def __init__(self):
        super(VpcApi, self).__init__()
        self.resource_name = "vpc"
        self.resource_workspace = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None

    def generate_create_data(self, zone, create_data, **kwargs):
        return _Common_.generate_create_data(zone, create_data, **kwargs)


class VpcBackendApi(ApiBackendBase):
    def __init__(self):
        super(VpcBackendApi, self).__init__()
        self.resource_name = "vpc"
        self.resource_workspace = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None

    def generate_create_data(self, zone, create_data, **kwargs):
        return _Common_.generate_create_data(zone, create_data, **kwargs)

    def create(self, *args, **kwargs):
        return self.apply(*args, **kwargs)
