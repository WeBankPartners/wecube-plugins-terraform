# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import traceback
from core import local_exceptions
from lib.logs import logger
from apps.common.convert_keys import convert_value
from apps.common.reverse import Reverse
from apps.common.reverse_convert_keys import ReverseProperty
from apps.background.resource.configr.value_config import ValueConfigObject
from .provider import ProviderConductor
from .region import RegionConductor


class ValueResetConductor(object):
    def values_config(self, provider, resource_name):
        '''

        :param provider:
        :param resource_name:
        :return:
        '''

        return ValueConfigObject().resource_value_configs(provider, resource_name)

    def reset_values(self, provider, resource_name, data):
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
                # value = convert_value(value, _values_configs.get(value))
                x_value = ReverseProperty.format_value(value, _values_configs.get(value))

                if x_value != value:
                    value = x_value
                else:
                    for m_key, m_value in _values_configs.items():
                        if m_value == value:
                            value = m_key
            else:
                logger.debug("key: %s value config is null, skip..." % key)

            resource_columns[key] = value

        if "zone" in data.keys():
            zone = ProviderConductor().zone_reverse_info(provider, zone=data["zone"])
            zone = RegionConductor().zone_reverse_info(provider, zone=zone)
            logger.info("find zone %s" % zone)
            resource_columns["zone"] = zone
            resource_columns["x_ora_zone"] = zone

        if "peer_region" in data.keys():
            peer_region = ProviderConductor().region_reverse_info(provider, region=data["peer_region"])
            peer_region = RegionConductor().region_reverse_info(provider, region=peer_region)
            logger.info("find region %s" % peer_region)
            resource_columns["peer_region"] = peer_region

        if "region" in data.keys():
            peer_region = ProviderConductor().region_reverse_info(provider, region=data["region"])
            peer_region = RegionConductor().region_reverse_info(provider, region=peer_region)
            logger.info("find region %s" % peer_region)
            resource_columns["region"] = peer_region

        return resource_columns
