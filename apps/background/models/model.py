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


class ResourceHistory(Base):
    __tablename__ = "resource_history"

    xid = Column(String(36), primary_key=True)
    id = Column(String(36), primary_key=True)
    resource = Column(String(36))
    ora_data = Column(String(65535))
    created_time = Column(DateTime)

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.xid = data.get("xid")
        self.id = data.get("id")
        self.resource = data.get("resource")
        self.ora_data = data.get("ora_data")


class Providers(Base):
    __tablename__ = "cloud_providers"

    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False)
    display_name = Column(String(64), nullable=False)
    plugin_source = Column(String(64))
    secret_id = Column(String(256))
    secret_key = Column(String(256))
    region = Column(String(64))
    zone = Column(String(64))
    extend_info = Column(String(1024))
    provider_property = Column(String(1024))
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


class ProviderSecret(Base):
    __tablename__ = "cloud_secret"

    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False)
    display_name = Column(String(64))
    provider = Column(String(64), nullable=False)
    region = Column(String(64))
    extend_info = Column(String(2048))
    secret_info = Column(String(2048))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    enabled = Column(TINYINT(1), server_default=text("'1'"))
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.deleted_time = data.get("deleted_time")
        self.display_name = data.get("display_name")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info")
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.name = data.get("name")
        self.provider = data.get("provider")
        self.region = data.get("region")
        self.secret_info = data.get("secret_info")
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
    source_property = Column(String(64))
    data_source = Column(String(1024))
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
        self.source_property = data.get("source_property")
        self.data_source = data.get("data_source")
        self.extend_info = data.get("extend_info") or '{}'
        self.resource_property = data.get("resource_property") or '{}'
        self.output_property = data.get("output_property") or '{}'
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
    extend_info = Column(String(1024))
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
    name = Column(String(64))
    hostname = Column(String(64))
    instance_type = Column(String(64))
    disk_type = Column(String(64))
    disk_size = Column(String(64))
    subnet_id = Column(String(64))
    ipaddress = Column(String(64))
    image = Column(String(64))
    password = Column(String(64))
    public_ip = Column(String(64))
    cpu = Column(Integer)
    memory = Column(Integer)
    power_state = Column(String(32))
    extend_info = Column(String(1024))
    define_json = Column(String(1024))
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
        self.image = data.get("image")
        self.disk_size = data.get("disk_size")
        self.disk_type = data.get("disk_type")
        self.enabled = data.get("enabled")
        self.extend_info = data.get("extend_info") or '{}'
        self.hostname = data.get("hostname")
        self.name = data.get("name")
        self.id = data.get("id")
        self.password = data.get("password")
        self.public_ip = data.get("public_ip")
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


class CloudResource(Base):
    __tablename__ = "cloud_resource"

    id = Column(String(36), primary_key=True)
    provider_id = Column(String(36))
    provider = Column(String(32))
    region = Column(String(64))
    zone = Column(String(64))
    resource_id = Column(String(64))
    owner_id = Column(String(64))
    relation_id = Column(String(64))
    resource_name = Column(String(64), nullable=False)
    propertys = Column(String(1024))
    extend_info = Column(String(1024))
    define_json = Column(String(4096))
    status = Column(String(36))
    output_json = Column(String(2048))
    result_json = Column(String(5120))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    deleted_time = Column(DateTime)
    is_deleted = Column(TINYINT(1), server_default=text("'0'"))

    def __init__(self, data):
        self.created_time = datetime.datetime.now()
        self.define_json = data.get("define_json")
        self.deleted_time = data.get("deleted_time")
        self.extend_info = data.get("extend_info")
        self.id = data.get("id")
        self.is_deleted = data.get("is_deleted")
        self.output_json = data.get("output_json")
        self.propertys = data.get("propertys")
        self.provider = data.get("provider")
        self.provider_id = data.get("provider_id")
        self.region = data.get("region")
        self.resource_id = data.get("resource_id")
        self.owner_id = data.get("owner_id")
        self.relation_id = data.get("relation_id")
        self.resource_name = data.get("resource_name")
        self.result_json = data.get("result_json")
        self.status = data.get("status")
        self.updated_time = data.get("updated_time")
        self.zone = data.get("zone")

# p = dir(ProviderSecret)
# for x in p:
#     if not x.startswith("_") and x not in ["to_dict", "metadata"]:
#         print('self.%s = data.get("%s")' % (x, x))
