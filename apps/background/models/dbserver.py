# coding: utf-8

import model
from objects import _BaseManager


class HistoryManager(_BaseManager):
    obj = model.ResourceHistory


class ProvidersManager(_BaseManager):
    obj = model.Providers


class CommonKeyManager(_BaseManager):
    obj = model.CommonKeys


class ConfigManager(_BaseManager):
    obj = model.Config


class ResourceManager(_BaseManager):
    obj = model.Resource


class InstanceTypeManager(_BaseManager):
    obj = model.InstanceType


class InstanceManager(_BaseManager):
    obj = model.Instance


class CrsManager(_BaseManager):
    obj = model.CloudResource
