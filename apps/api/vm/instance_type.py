# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
from apps.background.resource.configr.provider import ProviderObject
from apps.background.resource.vm.instance_type import InstanceTypeObject


class InstanceTypeApi(object):
    def __init__(self):
        self.resource_object = InstanceTypeObject()

    def create(self, rid, name, provider, origin_name, cpu, memory, network, type, extend_info):
        '''

        :param rid:
        :param name:
        :param provider_id:
        :param origin_name:
        :param cpu:
        :param memory:
        :param network:
        :param extend_info:
        :return:
        '''

        extend_info = extend_info or {}
        provider_info = ProviderObject().provider_name_object(provider)
        create_data = {"id": rid,
                       "name": name,
                       "type": type,
                       "provider_id": provider_info.get("id"),
                       "provider": provider,
                       "origin_name": origin_name,
                       "cpu": cpu, "memory": memory,
                       "network": network,
                       "extend_info": json.dumps(extend_info),
                       }

        return self.resource_object.create(create_data)

    def update(self, rid, data):
        if "provider_id" in data.keys():
            if not data.get("provider_id"):
                raise ValueError("provider id not permit set null")
            provider_info = ProviderObject().provider_object(provider_id=data.get("provider_id"))
            data["provider"] = provider_info.get("name")

        return self.resource_object.update(rid, data)
