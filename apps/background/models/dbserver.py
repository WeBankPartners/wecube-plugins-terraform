# coding: utf-8

import model
from objects import _BaseManager


class ProvidersManager(_BaseManager):
    obj = model.Providers


class CommonKeyManager(_BaseManager):
    obj = model.CommonKeys


class ConfigManager(_BaseManager):
    obj = model.Config


class ResourceManager(_BaseManager):
    obj = model.Resource


class VpcManager(_BaseManager):
    obj = model.Vpc


class SubnetManager(_BaseManager):
    obj = model.Subnet


class RouteTableManager(_BaseManager):
    obj = model.RouteTable


class RouteEntryManager(_BaseManager):
    obj = model.RouteEntry


class SecGroupManager(_BaseManager):
    obj = model.SecGroup


class SecGroupRuleManager(_BaseManager):
    obj = model.SecGroupRule


class NatGatewayManager(_BaseManager):
    obj = model.NatGateway


class EipManager(_BaseManager):
    obj = model.Eip


class EipAssociation(_BaseManager):
    obj = model.EipAssociation


class LBManager(_BaseManager):
    obj = model.LoadBalance


class LBListenerManager(_BaseManager):
    obj = model.LBListener


class DiskManager(_BaseManager):
    obj = model.Disk


class DiskAttachManager(_BaseManager):
    obj = model.DiskAttach


class InstanceTypeManager(_BaseManager):
    obj = model.InstanceType


class InstanceManager(_BaseManager):
    obj = model.Instance


class ConnectNetManager(_BaseManager):
    obj = model.ConnectNetwork


class ConnectNetAttachManager(_BaseManager):
    obj = model.ConnectNetworkAttach
