# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from lib.uuid_util import get_uuid
from lib.logs import logger
from lib.encrypt_helper import decrypt_str
from core import validation
from core.controller import BackendController
from core.controller import BackendIdController
from apps.common.validation import validate_column_line
from apps.api.configer.provider_secret import SecretApi
from apps.api.configer.provider_secret import ProviderSecretObject


class ProviderSecretController(BackendController):
    allow_methods = ('GET', "POST")
    resource = ProviderSecretObject()

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        validation.allowed_key(data.keys(), ["id", "name", "display_name", "region", "provider", "enabled"])

        filter_string = None
        for key in ["name", "display_name", "provider", "region"]:
            if data.get(key):
                if filter_string:
                    filter_string += 'and ' + key + " like '%" + data.get(key) + "%' "
                else:
                    filter_string = key + " like '%" + data.get(key) + "%' "
                data.pop(key, None)

        return self.resource.list(filters=data, page=page,
                                  filter_string=filter_string,
                                  pagesize=pagesize, orderby=orderby)

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "display_name", "provider", "server",
                                      "secret_info", "region", "extend_info"])
        validation.not_allowed_null(data=data,
                                    keys=["name", "provider", "secret_info"]
                                    )

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("server", data["server"])
        validation.validate_string("display_name", data.get("display_name"))
        validation.validate_string("provider", data.get("provider"))
        validation.validate_string("secret_info", data.get("secret_info"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_string("region", data.get("region"))

    def is_unique_name(self, provider, name):
        if self.resource.name_object(name=name, provider=provider):
            raise ValueError("provider %s secret %s exists" % (provider, name))

    def create(self, request, data, **kwargs):
        '''

        :param request:
        :param data:
        :param kwargs:
        :return:
        '''
        name = data.get("name")
        validate_column_line(name)

        extend_info = validation.validate_dict("extend_info", data.get("extend_info")) or {}
        secret_info = data.get("secret_info") #validation.validate_dict("secret_info", data.get("secret_info"))


        if not secret_info:
            raise ValueError("secret 认证信息不能为空,数据格式为JSON")

        self.is_unique_name(provider=data.get("provider"), name=data.get("name"))

        create_data = {"id": data.get("id") or get_uuid(),
                       "name": data["name"],
                       "server": data.get("server"),
                       "provider": data.get("provider"),
                       "display_name": data.get("display_name"),
                       "region": data.get("region"),
                       "extend_info": json.dumps(extend_info),
                       "secret_info": secret_info
                       }

        return self.resource.create(create_data)


class ProviderSecretIdController(BackendIdController):
    resource = ProviderSecretObject()

    def decrypt_key(self, str):
        if str:
            if str.startswith("{cipher_a}"):
                str = str[len("{cipher_a}"):]
                str = decrypt_str(str)

        return str

    def show(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        decrypt = 0
        try:
            decrypt = int(data.get("decrypt", "0"))
        except:
            logger.info("decrypt args error")

        res = self.resource.show(rid)
        if decrypt:
            res["secret_info"] = json.loads(self.decrypt_key(res.get("secret_info")))

        return res

    def before_handler(self, request, data, **kwargs):
        validation.allowed_key(data, ["id", "name", "display_name", "provider",
                                      "secret_info", "region", "extend_info"])

        validation.validate_string("id", data.get("id"))
        validation.validate_string("name", data["name"])
        validation.validate_string("display_name", data.get("display_name"))
        validation.validate_string("provider", data.get("provider"))
        validation.validate_string("secret_info", data.get("secret_info"))
        validation.validate_dict("extend_info", data.get("extend_info"))
        validation.validate_string("region", data.get("region"))

    def update(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)

        if data.get("extend_info") is not None:
            extend_info = validation.validate_dict("extend_info", data.get("extend_info"))
            data["extend_info"] = json.dumps(extend_info)

        if data.get("secret_info") is not None:
            provider_property = data.get("secret_info") #validation.validate_dict("secret_info", data.get("secret_info")) or {}
            data["secret_info"] = provider_property

        return self.resource.update(rid, data)

    def delete(self, request, data, **kwargs):
        rid = kwargs.pop("rid", None)
        return self.resource.delete(rid)
