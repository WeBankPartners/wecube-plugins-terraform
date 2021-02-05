# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from lib.json_helper import format_json_dumps
from core import local_exceptions
from apps.api.configer.provider import ProviderApi
from apps.api.apibase import ApiBase
from apps.background.resource.resource_base import CrsObject


class CCNApi(ApiBase):
    def __init__(self):
        super(CCNApi, self).__init__()
        self.resource_name = "ccn"
        self.resource_workspace = "ccn"
        self._flush_resobj()
        self.resource_keys_config = None

    def create(self, rid, name, provider_id,
               region, zone, extend_info, **kwargs):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param region:
        :param zone:
        :param extend_info:
        :return:
        '''

        _exists_data = self.create_resource_exists(rid)
        if _exists_data:
            return 1, _exists_data

        extend_info = extend_info or {}
        create_data = {"name": name}

        provider_object, provider_info = ProviderApi().provider_info(provider_id, region)
        _relations_id_dict = self.before_keys_checks(provider_object["name"], create_data)

        create_data.update(_relations_id_dict)

        count, res = self.run_create(rid, provider_id, region, zone=zone,
                                     provider_object=provider_object,
                                     provider_info=provider_info,
                                     owner_id=None,
                                     relation_id=None,
                                     create_data=create_data,
                                     extend_info=extend_info, **kwargs)

        return count, res
