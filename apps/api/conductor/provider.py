# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import traceback
from core import local_exceptions
from lib.logs import logger
from lib.encrypt_helper import encrypt_str
from lib.encrypt_helper import decrypt_str
from wecube_plugins_terraform.settings import TERRAFORM_BASE_PATH
from apps.background.resource.configr.provider import ProviderObject
from apps.api.configer.provider_secret import SecretApi
from apps.api.configer.provider import ProviderApi
from apps.common.validation import validate_column_line
from apps.common.convert_keys import convert_keys
from apps.common.convert_keys import convert_value

if not os.path.exists(TERRAFORM_BASE_PATH):
    os.makedirs(TERRAFORM_BASE_PATH)


class ProviderConductor(object):
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

    def zone_info(self, provider, zone):
        if zone:
            return ProviderApi().zone_info(provider, zone)

        return zone

    def zone_reverse_info(self, provider, zone):
        if zone:
            return ProviderApi().zone_reverse_info(provider, zone)

        return zone

    def format_secret(self, secret):
        '''

        :param secret:
        :return:
        '''
        if not secret:
            return {}

        if "{" in secret and "}" in secret:
            try:
                res = json.loads(secret)
            except:
                logger.info(secret)
                raise ValueError("secret key 不能转换为json")

        elif ";" in secret or "=" in secret:
            res = self._split_to_json(secret)
        else:
            validate_column_line(secret)
            res = secret

        return res

    def _provider_secret(self, provider, region, secret):
        if not secret:
            return secret

        secret = self.format_secret(secret)
        if isinstance(secret, dict):
            logger.info("secret format json, use secret info")
            return secret
        else:
            logger.debug("search secret info")
            info = SecretApi().secret_info(provider, name=secret, region=region)
            # if not info:
            #     raise ValueError("provider %s 提供了未知的认证信息, 请检查")
            return info

    def producer_secret_info(self, provider, region, secret, provider_data):
        '''

        :param provider:
        :param region:
        :param secret:
        :return:
        '''

        secret_info = self._provider_secret(provider, region, secret)
        if not secret_info:
            # 兼容provider旧的认证方式
            secret_info = {}
            logger.info("not search secret info, try use provider define info")
            provider_data["secret_id"] = self.decrypt_key(provider_data.get("secret_id"))
            provider_data["secret_key"] = self.decrypt_key(provider_data.get("secret_key"))

            for key in ["secret_id", "secret_key"]:
                if provider_data.get(key):
                    secret_info[key] = provider_data.get(key)
            
            provider_property = provider_data.get("provider_property", {})
            secret_info = convert_keys(secret_info, defines=provider_property, is_update=True)

        if not secret_info:
            raise ValueError("获取provider 认证信息失败")

        return secret_info

    def _provider_object(self, provider):
        provider_data = ProviderObject().query_one(where_data={"name": provider})
        if not provider_data:
            logger.debug("provider: %s is null, try search id" % provider)
            provider_data = ProviderObject().show(provider)

        if not provider_data:
            raise local_exceptions.ResourceValidateError("provider", "provider %s 未注册" % provider)
        return provider_data

    def find_provider_info(self, provider):
        '''

        :param provider: ID or name
        :return:
        '''

        provider_data = self._provider_object(provider)

        if not provider_data.get("is_init"):
            raise local_exceptions.ResourceConfigError("provider 未初始化，请重新初始化")

        return provider_data

    def conductor_provider_info(self, provider, region, secret):
        '''

        :param provider:  name
        :param region:  name
        :param secret:  name or string dict
        :return:
        '''

        provider_data = self.find_provider_info(provider)

        provider = provider_data.get("name")
        secret_info = self.producer_secret_info(provider, region, secret, provider_data)

        region = ProviderApi().region_info(provider, region)
        provider_info = {"region": region}

        extend_info = provider_data.get("extend_info", {})
        provider_property = provider_data.get("provider_property", {})

        provider_info.update(extend_info)
        provider_columns = convert_keys(provider_info, defines=provider_property, is_update=True)
        provider_columns.update(secret_info)
        

        info = {
            "provider": {
                provider: provider_columns
            }
        }

        return provider_data, info
