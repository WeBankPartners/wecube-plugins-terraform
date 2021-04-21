# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
from core import local_exceptions
from lib.command import command
from lib.logs import logger
from lib.encrypt_helper import encrypt_str
from lib.encrypt_helper import decrypt_str
from wecube_plugins_terraform.settings import BASE_DIR
from wecube_plugins_terraform.settings import TERRAFORM_BASE_PATH
from wecube_plugins_terraform.settings import TERRFORM_BIN_PATH
from apps.background.lib.commander.terraform import TerraformDriver
from apps.background.resource.configr.provider import ProviderObject
from apps.background.resource.configr.value_config import ValueConfigObject
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value
from apps.common.reverse_convert_keys import ReverseProperty

if not os.path.exists(TERRAFORM_BASE_PATH):
    os.makedirs(TERRAFORM_BASE_PATH)


class ProviderApi(object):
    def region_info(self, provider, region):
        '''
        转换region 信息
        :param provider: provider name
        :param region:
        :return:
        '''

        data = ValueConfigObject().query_one(where_data={"provider": provider,
                                                         "resource": "region"})
        # if not data:
        #     raise local_exceptions.RequestValidateError("config region 未进行定义")

        _config = data.get("value_config") or {}
        return convert_value(region, _config.get(region))

    def zone_info(self, provider, zone):
        '''

        :param provider:  provider name
        :param region:
        :return:
        '''
        data = ValueConfigObject().query_one(where_data={"provider": provider,
                                                         "resource": "zone"})
        # if not data:
        #     raise local_exceptions.RequestValidateError("zone 未进行定义")

        _config = data.get("value_config") or {}
        return convert_value(zone, _config.get(zone))

    def region_reverse_info(self, provider, region):
        '''

        :param provider:  provider name
        :param region:
        :return:
        '''
        data = ValueConfigObject().query_one(where_data={"provider": provider,
                                                         "resource": "region"})
        if not data:
            return region

        _config = data["value_config"]

        return ReverseProperty.format_value(region, _config)

    def zone_reverse_info(self, provider, zone):
        '''

        :param provider:  provider name
        :param region:
        :return:
        '''
        data = ValueConfigObject().query_one(where_data={"provider": provider,
                                                         "resource": "zone"})
        if not data:
            return zone

        _config = data["value_config"]

        return ReverseProperty.format_value(zone, _config)

        # return convert_value(zone, _config.get(zone))

    def init_provider(self, provider):
        '''

        :param provider: provider name
        :return:
        '''
        provider_path = os.path.join(TERRAFORM_BASE_PATH, provider)
        if not os.path.exists(provider_path):
            os.makedirs(provider_path)

        return TerraformDriver(terraform_path=TERRFORM_BIN_PATH,
                               workdir=provider_path).init(provider_path)

    def _generate_info(self, provider, region, data):
        '''

        :param provider: provider name
        :param region:
        :param data:  other columns
        :return:
        '''

        extend_info = data.get("extend_info", {})
        provider_property = data.get("provider_property", {})

        region = self.region_info(provider, region)

        provider_info = {"region": region}
        for key in ["secret_id", "secret_key"]:
            if data.get(key):
                provider_info[key] = data.get(key)

        provider_info.update(extend_info)
        provider_columns = convert_keys(provider_info, defines=provider_property)

        provider_data = {
            "provider": {
                provider: provider_columns
            }
        }

        return provider_data

    def decrypt_key(self, str):
        if str:
            if str.startswith("{cipher_a}"):
                str = str[len("{cipher_a}"):]
                str = decrypt_str(str)

        return str

    def provider_info(self, provider_id, region, provider_data=None):
        '''

        :param provider_id:  provider id
        :param region:
        :param provider_data:  provider object
        :return:
        '''
        if not provider_data:
            provider_data = ProviderObject().provider_object(provider_id)
            provider_data["secret_id"] = self.decrypt_key(provider_data.get("secret_id"))
            provider_data["secret_key"] = self.decrypt_key(provider_data.get("secret_key"))

        if not provider_data.get("is_init"):
            raise local_exceptions.ResourceConfigError("provider 未初始化，请重新初始化")

        return provider_data, self._generate_info(provider_data["name"], region, provider_data)

    def create_provider_workspace(self, provider):
        '''

        :param provider: provider name
        :return:
        '''
        provider_path = os.path.join(TERRAFORM_BASE_PATH, provider)
        provider_version = os.path.join(provider_path, "versions.tf")

        if not os.path.exists(provider_path):
            os.makedirs(provider_path)

        if not os.path.exists(provider_version):
            _version_path = os.path.join(BASE_DIR, "plugins/%s/versions.tf" % provider)
            if os.path.exists(_version_path):
                command(cmd="cp %s %s" % (_version_path, provider_path))
            else:
                logger.info("file: %s not found" % _version_path)

        return True
