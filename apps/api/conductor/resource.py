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
        property = resource_keys_config["resource_name"]

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

    def conductor_apply_data(self, label_name, create_data, ora_resource_name):
        '''

        :param provider: name
        :param region:
        :param secret:
        :param create_data:
        :param extend_info:
        :return:
        '''

        _info = {
            "resource": {
                ora_resource_name: {
                    label_name: create_data
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def conductor_apply_output(self, provider, resource_name, label_name):
        '''

        :param provider: name
        :param region:
        :param secret:
        :param create_data:
        :param extend_info:
        :return:
        '''

        output_json, _ = ResourceConfiger().conductor_apply_output(provider=provider,
                                                                   resource_name=resource_name,
                                                                   label_name=label_name
                                                                   )

        return output_json

    def apply_output(self, label_name, resource_object):
        return ResourceConfiger().apply_output(label_name=label_name, resource_object=resource_object)

    def _generate_import_resource(self, provider, resource_name, label_name):
        '''
        # import resource define: {
             "resource": {
                 "route_table": {
                     "example": {
                     }
                 }
             }
         }
        :param provider:
        :param resource_name:
        :param label_name:
        :return:
        '''

        configer = ResourceConfiger()
        resource_columns, resource_keys_config = configer.conductor_import_property(provider=provider,
                                                                                    resource_name=resource_name)

        property = resource_keys_config["resource_name"]

        _info = {
            "resource": {
                property: {
                    label_name: resource_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info, resource_keys_config

    def conductor_import_resource(self, provider, resource_name, label_name):
        '''

        :param provider: name
        :param region:
        :param secret:
        :param create_data:
        :param extend_info:
        :return:
        '''

        define_json, resource_keys_config = self._generate_import_resource(provider=provider,
                                                                           resource_name=resource_name,
                                                                           label_name=label_name
                                                                           )

        return define_json, resource_keys_config

    def fetch_resource_propertys(self, resource_name, label_name, define_json):
        _t = define_json["resource"][resource_name]
        origin_columns = _t[label_name]
        return origin_columns

    def _generate_upgrade_resource(self, provider, resource_name,
                                   label_name, update_data,
                                   extend_info, origin_data):
        '''

        :param provider: name
        :param resource_name:
        :param label_name:
        :param update_data:

        :param extend_info:
        :return:
        '''

        update_data = ValueConductor().conductor_apply_values(provider=provider,
                                                              resource_name=resource_name,
                                                              data=update_data)

        configer = ResourceConfiger()
        resource_columns, resource_keys_config = configer.conductor_upgrade_property(provider=provider,
                                                                                     resource_name=resource_name,
                                                                                     resource_data=update_data,
                                                                                     )

        extend_json, _ = configer.conductor_upgrade_extend(provider=provider,
                                                           resource_name=resource_name,
                                                           extend_info=extend_info,
                                                           )

        resource_columns.update(extend_json)
        property = resource_keys_config["resource_name"]

        origin_columns = self.fetch_resource_propertys(resource_name, label_name, origin_data)
        origin_columns.update(resource_columns)

        _info = {
            "resource": {
                property: {
                    label_name: origin_columns
                }
            }
        }

        logger.info(format_json_dumps(_info))
        return _info, resource_keys_config

    def conductor_upgrade_resource(self, provider, resource_name,
                                   label_name, update_data,
                                   extend_info, origin_data):
        '''

        :param provider:
        :param resource_name:
        :param label_name:
        :param update_data:
        :param extend_info:
        :param origin_data:
        :return:
        '''

        update_json, resource_keys_config = self._generate_upgrade_resource(provider=provider,
                                                                            resource_name=resource_name,
                                                                            label_name=label_name,
                                                                            update_data=update_data,
                                                                            extend_info=extend_info,
                                                                            origin_data=origin_data)

        origin_data.update(update_json)
        return origin_data, resource_keys_config

    def _generate_data_source(self, provider, resource_name, label_name, resource_data):
        '''

        :param provider:
        :param resource_name:
        :param label_name:
        :param resource_data:
        :return:
        '''

        resource_data = ValueConductor().conductor_apply_values(provider=provider,
                                                                resource_name=resource_name,
                                                                data=resource_data)

        configer = ResourceConfiger()
        configer.pre_check_source_property(provider=provider,
                                           resource_name=resource_name,
                                           resource_data=resource_data)

        resource_columns, resource_keys_config = configer.conductor_source_property(provider=provider,
                                                                                    resource_name=resource_name,
                                                                                    resource_data=resource_data)

        property = resource_keys_config.get("data_source_name") or resource_keys_config["resource_name"]

        _info = {
            "data": {
                property: {
                    label_name: resource_columns
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info, resource_keys_config

    def generate_data_source(self, label_name, query_data, resource_object):
        '''

        :param provider:
        :param resource_name:
        :param label_name:
        :param resource_data:
        :return:
        '''

        property = resource_object.get("data_source_name") or resource_object["resource_name"]

        _info = {
            "data": {
                property: {
                    label_name: query_data
                }
            }
        }
        logger.info(format_json_dumps(_info))
        return _info

    def conductor_reset_resource(self, provider, resource_name, label_name, resource_data):
        '''

        :param provider: name
        :param region:
        :param secret:
        :param create_data:
        :param extend_info:
        :return:
        '''

        define_json, resource_keys_config = self._generate_data_source(provider=provider,
                                                                       resource_name=resource_name,
                                                                       label_name=label_name,
                                                                       resource_data=resource_data)

        output_json, _ = ResourceConfiger().conductor_data_output(provider=provider,
                                                                  resource_name=resource_name,
                                                                  label_name=label_name
                                                                  )

        # define_json.update(output_json)
        return define_json, resource_keys_config

    def conductor_reset_filter(self, provider, resource_name):
        configer = ResourceConfiger()
        resource_columns, _ = configer.conductor_reset_property(provider=provider,
                                                                resource_name=resource_name)
        return resource_columns

    def conductor_reset_equivalence(self, provider, resource_name):
        configer = ResourceConfiger()
        resource_columns, _ = configer.conductor_reset_equivalence(provider=provider,
                                                                   resource_name=resource_name)
        return resource_columns
