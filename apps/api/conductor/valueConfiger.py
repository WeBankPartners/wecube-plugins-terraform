# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import traceback
from core import local_exceptions
from lib.logs import logger
from apps.common.convert_keys import convert_value
from apps.background.resource.configr.value_config import ValueConfigObject


class ValueConductor(object):
    def values_config(self, provider, resource_name):
        '''

        :param provider:
        :param resource_name:
        :return:
        '''

        return ValueConfigObject().resource_value_configs(provider, resource_name)

    def conductor_apply_values(self, provider, resource_name, data):
        '''
        todo 特殊值/约定规则值处理
        :param provider:
        :param resource_name:
        :param data:
        :return:
        '''

        resource_values_config = self.values_config(provider, resource_name)

        resource_columns = {}
        logger.debug("start revert value ....")
        for key, value in data.items():
            if resource_values_config.get(key):
                _values_configs = resource_values_config.get(key)
                value = convert_value(value, _values_configs.get(value))
            else:
                logger.debug("key: %s value config is null, skip..." % key)

            resource_columns[key] = value

        return resource_columns
