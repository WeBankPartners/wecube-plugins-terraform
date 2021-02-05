# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from core import local_exceptions
from lib.json_helper import format_json_dumps
from lib.logs import logger
from apps.api.apibase import ApiBase
from apps.api.configer.provider import ProviderApi


class VpcApi(ApiBase):
    def __init__(self):
        super(VpcApi, self).__init__()
        self.resource_name = "vpc"
        self.resource_workspace = "vpc"
        self._flush_resobj()
        self.resource_keys_config = None

    def create(self, rid, name, cidr, provider_id, region, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param cidr:
        :param provider_id:
        :param region:
        :param extend_info:
        :param kwargs:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        create_data = {"cidr": cidr, "name": name}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=None,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=None, relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
