# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import traceback
from lib.logs import logger
from apps.api.conductor.model_format import ModelFormat


class ValueConfigerConductor(object):
    @staticmethod
    def terraform_value(value, resource_value_config):
        if value:
            x_value = resource_value_config.get(value)
            if isinstance(x_value, dict):
                value = x_value.get("value") or value
                value = ModelFormat.format_type(value, type=x_value.get("type"))

        return value

    @staticmethod
    def outer_value(value, resource_value_config):
        if value is None or value == "":
            value = ""
        if not resource_value_config:
            return value

        if value or value == 0 or value is False:
            for x_value, y_value in resource_value_config.items():
                if isinstance(y_value, basestring):
                    if str(y_value) == str(value):
                        value = x_value
                        break
                else:
                    if str(y_value.get("value")) == str(value):
                        value = x_value
                        break

        return value
