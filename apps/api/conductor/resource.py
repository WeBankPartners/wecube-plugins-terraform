# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import traceback
from core import local_exceptions
from lib.logs import logger
from lib.json_helper import format_json_dumps
from .resourceConfiger import ResourceConfiger
from .valueConfiger import ValueConductor


class ResourceConductor(object):
    def __init__(self):
        pass

    def _generate_resource(self, provider, resource_name,
                           label_name, create_data, extend_info):
        '''

        :param provider: name
        :param resource_name:
        :param label_name:
        :param create_data:
        :param extend_info:
        :return:
        '''

        create_data = ValueConductor().conductor_apply_values(provider=provider,
                                                              resource_name=resource_name,
                                                              data=create_data)

        configer = ResourceConfiger()
        resource_columns, resource_keys_config = configer.conductor_apply_property(provider=provider,
                                                                                   resource_name=resource_name,
                                                                                   resource_data=create_data)

        extend_json, _ = configer.conductor_apply_extend(provider=provider,
                                                         resource_name=resource_name,
                                                         extend_info=extend_info)

        resource_columns.update(extend_json)
        property = resource_keys_config["property"]

        _info = {
            "resource": {
                property: {
                    label_name: resource_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info, resource_keys_config

    def conductor_apply_resource(self, provider, resource_name,
                                 label_name, create_data, extend_info):
        '''

        :param provider: name
        :param region:
        :param secret:
        :param create_data:
        :param extend_info:
        :return:
        '''

        define_json, resource_keys_config = self._generate_resource(provider=provider,
                                                                    resource_name=resource_name,
                                                                    label_name=label_name,
                                                                    create_data=create_data,
                                                                    extend_info=extend_info)

        output_json, _ = ResourceConfiger().conductor_apply_output(provider=provider,
                                                                   resource_name=resource_name,
                                                                   label_name=label_name
                                                                   )

        define_json.update(output_json)
        return define_json, resource_keys_config
