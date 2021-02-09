# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import traceback
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
from apps.api.configer.provider_secret import SecretApi
from apps.api.configer.provider import ProviderApi
from apps.common.validation import validate_column_line
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value

if not os.path.exists(TERRAFORM_BASE_PATH):
    os.makedirs(TERRAFORM_BASE_PATH)


class Provider(object):
    def decrypt_key(self, str):
        if str:
            if str.startswith("{cipher_a}"):
                str = str[len("{cipher_a}"):]
                str = decrypt_str(str)

        return str

    def _split_to_json(self, secret):
        try:
            res = {}
            secret = secret.replace(" ", '')
            _cols = secret.split(";")
            for col in _cols:
                tmp = col.split("=")
                res[tmp[0]] = tmp[1]

            return res
        except:
            logger.info(traceback.format_exc())
            raise ValueError("格式错误, 无法解析的格式, 正确格式为:  key1=value1; key2=value2 ...")

    def format_secret(self, secret):
        '''

        :param secret:
        :return:
        '''

        if "{" in secret and "}" in secret:
            try:
                res = json.loads(secret)
            except:
                logger.info(secret)
                raise ValueError("secret key 不能转换为json")

        elif ";" in secret:
            res = self._split_to_json(secret)
        else:
            validate_column_line(secret)
            res = secret

        return res

    def provider_secret(self, provider, region, secret):
        secret = self.format_secret(secret)
        if isinstance(secret, dict):
            return secret
        else:
            info = SecretApi().secret_info(provider, name=secret, region=region)
            # if not info:
            #     raise ValueError("provider %s 提供了未知的认证信息, 请检查")
            return info

    def product_provider_info(self, provider, region, secret):
        '''

        :param provider:  name
        :param region:  name
        :param secret:  name or string dict
        :return:
        '''

        provider_data = ProviderObject().provider_name_object(provider)

        provider_data["secret_id"] = self.decrypt_key(provider_data.get("secret_id"))
        provider_data["secret_key"] = self.decrypt_key(provider_data.get("secret_key"))

        if not provider_data.get("is_init"):
            raise local_exceptions.ResourceConfigError("provider 未初始化，请重新初始化")

        secret_info = self.provider_secret(provider, region, secret)
        if not secret_info:
            # 兼容provider旧的认证方式
            for key in ["secret_id", "secret_key"]:
                if provider_data.get(key):
                    secret_info[key] = provider_data.get(key)

        if not secret_info:
            raise ValueError("获取provider 认证信息失败")

        provider_info = {"region": region}

        extend_info = provider_data.get("extend_info", {})
        provider_property = provider_data.get("provider_property", {})

        provider_info.update(secret_info)
        provider_info.update(extend_info)
        provider_columns = convert_keys(provider_info, defines=provider_property)

        info = {
            "provider": {
                provider: provider_columns
            }
        }

        return info

