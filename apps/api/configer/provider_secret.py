# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
from core import local_exceptions
from lib.logs import logger
from lib.encrypt_helper import encrypt_str
from lib.encrypt_helper import decrypt_str
from apps.background.resource.configr.provider_secret import ProviderSecretObject


class SecretApi(object):
    def decrypt_key(self, str):
        if str:
            if str.startswith("{cipher_a}"):
                str = str[len("{cipher_a}"):]
                str = decrypt_str(str)

        return str

    def secret_info(self, provider, name, region):
        '''

        :param provider:
        :param name:
        :return:
        '''

        data = ProviderSecretObject().query_one(where_data={"provider": provider, "name": name})
        if not data:
            logger.info("provider %s, name %s  is null, return skip ..." % (provider, name))
            return {}
        else:
            define_region = data.get("region", "") or ""
            if define_region:
                if region not in define_region.split(","):
                    raise ValueError("secret : %s define at %s not apply for region: %s" % (name,
                                                                                            define_region, region))

            return self.decrypt_key(data.get("secret_info"))
