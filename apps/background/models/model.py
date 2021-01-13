# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
from sqlalchemy import Column, DateTime, Index, String, text, Text
from sqlalchemy import Integer
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


Base.to_dict = to_dict


class Providers(Base):
    __tablename__ = "cloud_providers"

    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False)
    display_name = Column(String(64), nullable=False)
    plugin_source = Column(String(64))
    secret_id = Column(String(256), nullable=False)
    secret_key = Column(String(256), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    extend_info = Column(String(512))
    provider_property = Column(String(512))
    is_init = Column(TINYINT(1), server_default=text("'0'"))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.is_init = data.get("is_init")
        self.region = data.get("region")
        self.zone = data.get("zone")
        self.name = data.get("name")
        self.display_name = data.get("display_name")
        self.provider_property = data.get("provider_property") or '{}'
        self.secret_id = data.get("secret_id")
        self.secret_key = data.get("secret_key")
        self.plugin_source = data.get("plugin_source")
        self.updated_time = data.get("updated_time")


class Resource(Base):
    __tablename__ = "resource"

    id = Column(String(36), primary_key=True)
    provider = Column(String(32), nullable=False)
    property = Column(String(64), nullable=False)
    resource_name = Column(String(64), nullable=False)
    extend_info = Column(String(1024))
    resource_property = Column(String(2048), nullable=False)
    output_property = Column(String(1024), nullable=False)
    is_locked = Column(TINYINT(1), server_default=text("'0'"))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.is_locked = data.get("is_locked")
        self.property = data.get("property")
        self.provider = data.get("provider")
        self.resource_name = data.get("resource_name")
        self.extend_info = data.get("extend_info") or '{}'
        self.resource_property = data.get("resource_property") or '{}'
        self.output_property = data.get("outout_property") or '{}'
        self.updated_time = data.get("updated_time")


class CommonKeys(Base):
    __tablename__ = "common_keys"

    id = Column(String(36), primary_key=True)
    resource = Column(String(64), nullable=False)
    property = Column(String(64))
    key = Column(String(64), nullable=False)
    is_locked = Column(TINYINT(1), server_default=text("'0'"))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.is_locked = data.get("is_locked")
        self.key = data.get("key")
        self.resource = data.get("resource")
        self.property = data.get("property")
        self.updated_time = data.get("updated_time")


class Config(Base):
    __tablename__ = "config"

    id = Column(String(36), primary_key=True)
    provider = Column(String(32), nullable=False)
    resource = Column(String(64))
    property = Column(String(64))
    value_config = Column(String(2048))
    is_locked = Column(TINYINT(1), server_default=text("'0'"))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.is_locked = data.get("is_locked")
        self.value_config = data.get("value_config") or '{}'
        self.provider = data.get("provider")
        self.resource = data.get("resource")
        self.property = data.get("property")
        self.updated_time = data.get("updated_time")


class Vpc(Base):
    __tablename__ = "vpc"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    cider = Column(String(128))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.cider = data.get("cider")
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json")
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.region = data.get("region")
        self.zone = data.get("zone")
        self.status = data.get("status")
        self.result_json = data.get("result_json") or '{}'
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.updated_time = data.get("updated_time")


class Subnet(Base):
    __tablename__ = "subnet"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    vpc = Column(String(64))
    cider = Column(String(128))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.cider = data.get("cider")
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.region = data.get("region")
        self.zone = data.get("zone")
        self.status = data.get("status")
        self.result_json = data.get("result_json") or '{}'
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.updated_time = data.get("updated_time")
        self.vpc = data.get("vpc")


class RouteTable(Base):
    __tablename__ = "route_table"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    vpc = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.region = data.get("region")
        self.zone = data.get("zone")
        self.status = data.get("status")
        self.result_json = data.get("result_json") or '{}'
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.updated_time = data.get("updated_time")
        self.vpc = data.get("vpc")


class RouteEntry(Base):
    __tablename__ = "route_entry"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    vpc = Column(String(64))
    route_table = Column(String(64))
    next_type = Column(String(64))
    next_hub = Column(String(128))
    destination = Column(String(128))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.destination = data.get("destination")
        self.next_hub = data.get("next_hub")
        self.next_type = data.get("next_type")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.route_table = data.get("route_table")
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.vpc = data.get("vpc")
        self.zone = data.get("zone")


class SecGroup(Base):
    __tablename__ = "security_group"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    vpc = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.region = data.get("region")
        self.zone = data.get("zone")
        self.status = data.get("status")
        self.result_json = data.get("result_json") or '{}'
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.updated_time = data.get("updated_time")
        self.vpc = data.get("vpc")


class SecGroupRule(Base):
    __tablename__ = "security_group_rule"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    name = Column(String(64))
    resource_id = Column(String(64))
    description = Column(String(64))
    security_group_id = Column(String(64))
    type = Column(String(64))
    cider_ip = Column(String(64))
    ip_protocol = Column(String(64))
    ports = Column(String(64))
    policy = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.cider_ip = data.get("cider_ip")
        self.name = data.get("name")
        self.description = data.get("description")
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.ip_protocol = data.get("ip_protocol")
        self.is_deleted = data.get("is_deleted")
        self.policy = data.get("policy")
        self.ports = data.get("ports")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.security_group_id = data.get("security_group_id")
        self.status = data.get("status")
        self.type = data.get("type")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class NatGateway(Base):
    __tablename__ = "nat_gateway"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    vpc = Column(String(64))
    subnet = Column(String(64))
    ipaddress = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.ipaddress = data.get("ipaddress")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.status = data.get("status")
        self.subnet = data.get("subnet")
        self.updated_time = data.get("updated_time")
        self.vpc = data.get("vpc")
        self.zone = data.get("zone")


class Eip(Base):
    __tablename__ = "eip"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    ipaddress = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.ipaddress = data.get("ipaddress")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class EipAssociation(Base):
    __tablename__ = "eip_association"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    eip_id = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.eip_id = data.get("eip_id")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class LoadBalance(Base):
    __tablename__ = "load_balance"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    subnet_id = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.subnet_id = data.get("subnet_id")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class LBListener(Base):
    __tablename__ = "load_balance_listener"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    lb_id = Column(String(36))
    port = Column(Integer())
    protocol = Column(String(36))
    backend_server = Column(String(1024))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.backend_server = data.get("backend_server")
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.lb_id = data.get("lb_id")
        self.port = data.get("port")
        self.protocol = data.get("protocol")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class Disk(Base):
    __tablename__ = "disk"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    size = Column(Integer())
    type = Column(String(36))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.size = data.get("size")
        self.status = data.get("status")
        self.type = data.get("type")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class DiskAttach(Base):
    __tablename__ = "disk_attach"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    disk = Column(String(64))
    instance = Column(String(36))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.disk = data.get("disk")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.instance = data.get("instance")
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class InstanceType(Base):
    __tablename__ = "instance_type"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    name = Column(String(64))
    origin_name = Column(String(64))
    network = Column(String(64))
    cpu = Column(Integer)
    memory = Column(Integer)
    extend_info = Column(String(512))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.cpu = data.get("cpu")
        self.created_time = data.get("created_time")
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info")
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.memory = data.get("memory")
        self.name = data.get("name")
        self.origin_name = data.get("origin_name")
        self.network = data.get("network")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.updated_time = data.get("updated_time")


class Instance(Base):
    __tablename__ = "instance"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    disk = Column(String(64))
    name = Column(String(64))
    hostname = Column(String(64))
    instance_type = Column(String(64))
    disk_type = Column(String(64))
    disk_size = Column(String(64))
    subnet_id = Column(String(64))
    ipaddress = Column(String(64))
    cpu = Column(Integer)
    memory = Column(Integer)
    power_state = Column(String(32))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.cpu = data.get("cpu")
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.disk = data.get("disk")
        self.disk_size = data.get("disk_size")
        self.disk_type = data.get("disk_type")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.hostname = data.get("hostname")
        self.name = data.get("name")
        self.id = data.get("id")
        self.subnet_id = data.get("subnet_id")
        self.instance_type = data.get("instance_type")
        self.ipaddress = data.get("ipaddress")
        self.is_deleted = data.get("is_deleted")
        self.memory = data.get("memory")
        self.power_state = data.get("power_state")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class ConnectNetwork(Base):
    __tablename__ = "connect_network"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class ConnectNetworkAttach(Base):
    __tablename__ = "connect_network_attach"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    connect_id = Column(String(64))
    instance_type = Column(String(64))
    instance_id = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.connect_id = data.get("connect_id")
        self.define_json = data.get("define_json") or '{}'
        self.deleted_time = data.get("deleted_time")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.id = data.get("id")
        self.instance_id = data.get("instance_id")
        self.instance_type = data.get("instance_type")
        self.is_deleted = data.get("is_deleted")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json") or '{}'
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")


class RdsDb(Base):
    __tablename__ = "rds_db"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    engine = Column(String(64))
    version = Column(String(32))
    instance_type = Column(String(64))
    disk_type = Column(String(64))
    disk_size = Column(String(64))
    subnet_id = Column(String(64))
    ipaddress = Column(String(64))
    port = Column(String(32))
    user = Column(String(32))
    password = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = data.get("created_time") or datetime.datetime.now()
        self.define_json = data.get("define_json")
        self.deleted_time = data.get("deleted_time")
        self.disk_size = data.get("disk_size")
        self.disk_type = data.get("disk_type")
        self.enabled = data.get("enabled")
        self.engine = data.get("engine")
        self.extend_info = data.get("extend_info")
        self.id = data.get("id")
        self.instance_type = data.get("instance_type")
        self.ipaddress = data.get("ipaddress")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.port = data.get("port")
        self.user = data.get("user")
        self.password = data.get("password")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json")
        self.status = data.get("status")
        self.subnet_id = data.get("subnet_id")
        self.updated_time = data.get("updated_time")
        self.version = data.get("version")
        self.zone = data.get("zone")


class Nosql(Base):
    __tablename__ = "nosql"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    engine = Column(String(64))
    version = Column(String(32))
    instance_type = Column(String(64))
    disk_type = Column(String(64))
    disk_size = Column(String(64))
    subnet_id = Column(String(64))
    ipaddress = Column(String(64))
    port = Column(String(32))
    user = Column(String(32))
    password = Column(String(64))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = data.get("created_time") or datetime.datetime.now()
        self.define_json = data.get("define_json")
        self.deleted_time = data.get("deleted_time")
        self.disk_size = data.get("disk_size")
        self.disk_type = data.get("disk_type")
        self.enabled = data.get("enabled")
        self.engine = data.get("engine")
        self.extend_info = data.get("extend_info")
        self.id = data.get("id")
        self.instance_type = data.get("instance_type")
        self.ipaddress = data.get("ipaddress")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.port = data.get("port")
        self.user = data.get("user")
        self.password = data.get("password")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json")
        self.status = data.get("status")
        self.subnet_id = data.get("subnet_id")
        self.updated_time = data.get("updated_time")
        self.version = data.get("version")
        self.zone = data.get("zone")


class KVStore(Base):
    __tablename__ = "kvstore"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32), nullable=False)
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    name = Column(String(64))
    engine = Column(String(64))
    version = Column(String(32))
    instance_type = Column(String(64))
    subnet_id = Column(String(64))
    ipaddress = Column(String(64))
    port = Column(String(32))
    extend_info = Column(String(512))
    define_json = Column(String(512))
    status = Column(String(36))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = data.get("created_time") or datetime.datetime.now()
        self.define_json = data.get("define_json")
        self.deleted_time = data.get("deleted_time")
        self.disk_size = data.get("disk_size")
        self.disk_type = data.get("disk_type")
        self.enabled = data.get("enabled")
        self.engine = data.get("engine")
        self.extend_info = data.get("extend_info")
        self.id = data.get("id")
        self.instance_type = data.get("instance_type")
        self.ipaddress = data.get("ipaddress")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.port = data.get("port")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.result_json = data.get("result_json")
        self.status = data.get("status")
        self.subnet_id = data.get("subnet_id")
        self.updated_time = data.get("updated_time")
        self.version = data.get("version")
        self.zone = data.get("zone")

# p = dir(RdsDb)
# for x in p:
#     if not x.startswith("_") and x not in ["to_dict", "metadata"]:
#         print
#         'self.%s = data.get("%s")' % (x, x)
