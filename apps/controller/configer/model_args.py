# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

resouce_property_models = {
    "provider": [
        "secret_id",
        "secret_key",
        "region"
    ],
    "vpc": [
        "name",
        "cidr"
    ],
    "subnet": [
        "cidr",
        "name",
        "vpc_id",
        "zone"
    ],
    "route_table": [
        "name",
        "vpc_id"
    ],
    "route_entry": [
        "name",
        "vpc_id",
        "route_table_id",
        "next_type",
        "next_hub",
        "destination"
    ],
    "security_group": [
        "name",
        "vpc_id"
    ],
    "security_group_rule": [
        "description",
        "type",
        "security_group_id",
        "cidr_ip",
        "policy",
        "ip_protocol",
        "ports"
    ],
    "nat": [
        "name",
        "vpc_id",
        "subnet_id",
        "eip",
        "bandwidth"
    ],
    "peer_connection": [
        "name",
        "vpc_id",
        "peer_vpc_id",
        "peer_region"
    ],
    "eip": [
        "name",
        "charge_type"
    ],
    "eip_association": [
        "name",
        "eip_id",
        "instance_id",
        "private_ip"
    ],
    "lb": [
        "name",
        "network_type",
        "vpc_id",
        "subnet_id",
        "charge_type"
    ],
    "lb_listener": [
        "name",
        "port",
        "protocol",
        "backend_port",
        "health_check",
        "health_check_uri",
        "lb_id"
    ],
    "lb_attach": [
        "backend_servers",
        "instance_id",
        "weight",
        "listener_id",
        "lb_id"
    ],
    "disk": [
        "name",
        "type",
        "size",
        "zone",
        "charge_type"
    ],
    "disk_attach": [
        "disk_id",
        "instance_id"
    ],
    "network_interface": [
        "name",
        "ipaddress",
        "vpc_id",
        "subnet_id",
        "security_group_id"
    ],
    "network_interface_attach": [
        "network_interface_id",
        "instance_id"
    ],
    "object_storage": [
        "name",
        "acl"
    ],
    "bucket_object": [
        "key",
        "context",
        "source",
        "bucket_id"
    ],
    "ccn": [
        "name"
    ],
    "ccn_attach": [
        "instance_type",
        "instance_region",
        "instance_id",
        "ccn_id"
    ],
    "ccn_bandwidth": [
        "bandwidth",
        "from_region",
        "dest_region",
        "ccn_id"
    ],
    "instance": [
        "name",
        "hostname",
        "password",
        "vpc_id",
        "security_group_id",
        "data_disks",
        "instance_type",
        "disk_type",
        "disk_size",
        "subnet_id",
        "zone",
        "image",
        "power_action",
        "force_delete",
        "charge_type"
    ],
    "mysql": [
        "name",
        "charge_type",
        "engine",
        "zone",
        "version",
        "disk_type",
        "disk_size",
        "subnet_id",
        "instance_type",
        "vpc_id",
        "security_group_id",
        "port",
        "user",
        "first_slave_zone",
        "second_slave_zone",
        "password",
        "force_delete"
    ],
    "mysql_database": [
        "name",
        "mysql_id"
    ],
    "mysql_account": [
        "name",
        "password",
        "mysql_id"
    ],
    "mysql_privilege": [
        "usrename",
        "mysql_id",
        "database_columns",
        "database",
        "privileges"
    ],
    "mysql_backup": [
        "backup_model",
        "mysql_id",
        "backup_time"
    ],
    "mariadb": [
        "charge_type",
        "name",
        "engine",
        "zone",
        "version",
        "disk_type",
        "disk_size",
        "subnet_id",
        "instance_type",
        "vpc_id",
        "security_group_id",
        "port",
        "user",
        "first_slave_zone",
        "second_slave_zone",
        "password",
        "force_delete"
    ],
    "postgreSQL": [
        "charge_type",
        "name",
        "engine",
        "zone",
        "version",
        "disk_type",
        "disk_size",
        "subnet_id",
        "instance_type",
        "vpc_id",
        "security_group_id",
        "port",
        "user",
        "first_slave_zone",
        "second_slave_zone",
        "password",
        "force_delete"
    ],
    "rds": [
        "name",
        "engine",
        "zone",
        "version",
        "disk_type",
        "disk_size",
        "subnet_id",
        "instance_type",
        "vpc_id",
        "security_group_id",
        "port",
        "user",
        "password",
        "charge_type",
        "force_delete"
    ],
    "nosql": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "instance_type",
        "port",
        "password",
        "charge_type",
        "force_delete"
    ],
    "mongodb": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "instance_type",
        # "port",
        "disk_size",
        "password",
        "charge_type",
        "force_delete"
    ],
    "kvstore": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "vpc_id",
        "security_group_id",
        "instance_type",
        "port",
        "password",
        "charge_type",
        "force_delete"
    ],
    "redis": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "vpc_id",
        "security_group_id",
        "instance_type",
        "port",
        "password",
        "charge_type",
        "force_delete"
    ],
    "memcached": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "vpc_id",
        "security_group_id",
        "instance_type",
        "port",
        "password",
        "force_delete",
        "charge_type"
    ],
    "kvstore_backup": [
        "backup_time",
        "backup_period",
        "kvstore_id"
    ],
    "redis_backup": [
        "backup_time",
        "backup_period",
        "redis_id"
    ],
    "memcached_backup": [
        "backup_time",
        "backup_period",
        "memcached_id"
    ],
}

output_property_models = {
    "vpc": [
        "resource_id"
    ],
    "subnet": [
        "resource_id"
    ],
    "route_table": [
        "resource_id"
    ],
    "route_entry": [
        "resource_id"
    ],
    "security_group": [
        "resource_id"
    ],
    "security_group_rule": [
        "resource_id"
    ],
    "nat": [
        "resource_id",
        "ipaddress"
    ],
    "peer_connection": [
        "resource_id"
    ],
    "eip": [
        "resource_id",
        "ipaddress"
    ],
    "eip_association": [
        "resource_id"
    ],
    "lb": [
        "resource_id",
        "ipaddress"
    ],
    "lb_listener": [
        "resource_id"
    ],
    "lb_attach": [
        "resource_id"
    ],
    "disk": [
        "resource_id"
    ],
    "disk_attach": [
        "resource_id"
    ],
    "network_interface": [
        "resource_id",
        "ipaddress"
    ],
    "network_interface_attach": [
        "resource_id"
    ],
    "object_storage": [
        "resource_id",
        "url"
    ],
    "bucket_object": [
        "resource_id"
    ],
    "ccn": [
        "resource_id"
    ],
    "ccn_attach": [
        "resource_id"
    ],
    "ccn_bandwidth": [
        "resource_id"
    ],
    "instance": [
        "resource_id",
        "ipaddress",
        "public_ip"
    ],
    "mysql": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "mysql_database": [
        "resource_id",
    ],
    "mysql_account": [
        "resource_id",
    ],
    "mysql_privilege": [
        "resource_id",
    ],
    "mysql_backup": [
        "resource_id",
    ],
    "mariadb": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "postgreSQL": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "rds": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "nosql": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "mongodb": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "kvstore": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "redis": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "memcached": [
        "resource_id",
        "ipaddress",
        "port"
    ],
    "memcached_backup": [
        "resource_id"
    ],
    "redis_backup": [
        "resource_id"
    ],
    "kvstore_backup": [
        "resource_id"
    ],
}

data_source_models = {
    "vpc": [
        "resource_id",
        "name",
        "tag",
        "cidr"
    ],
    "subnet": [
        "resource_id",
        "zone",
        "cidr",
        "tag",
        "vpc_id"
    ],
    "route_table": [
        "resource_id",
        "name",
        "tag",
        "vpc_id"
    ],
    "route_entry": [
        "resource_id",
        "route_table_id",
        "cidr",
        "type"
    ],
    "security_group": [
        "resource_id",
        "name",
        "vpc_id",
        "tag"
    ],
    "security_group_rule": [
        "resource_id",
        "security_group_id"
    ],
    "nat": [
        "resource_id",
        "name",
        "type",
        "tag",
        "vpc_id",
        "bandwidth"
    ],
    "peer_connection": [
        "resource_id",
        "name",
        "vpc_id",
        "peer_vpc_id",
        "peer_region"
    ],
    "eip": [
        "resource_id",
        "name",
        "ipaddress",
        "tag"
    ],
    "eip_association": [
        "resource_id",
        "instance_id"
    ],
    "lb": [
        "resource_id",
        "name",
        "vpc_id",
        "subnet_id",
        "tag",
        "ipaddress"
    ],
    "lb_listener": [
        "resource_id",
        "port",
        "protocol",
        "lb_id",
        "tag"
    ],
    "lb_attach": [
        "resource_id"
    ],
    "disk": [
        "resource_id",
        "name",
        "instance_id",
        "type",
        "tag"
    ],
    "disk_attach": [
        "resource_id",
        "instance_id"
    ],
    "network_interface": [
        "resource_id",
        "name",
        "vpc_id",
        "subnet_id",
        "tag",
        "ipaddress",
        "public_ip"
    ],
    "network_interface_attach": [
        "resource_id"
    ],
    "object_storage": [
        "resource_id",
        "name",
        "tag"
    ],
    "bucket_object": [
        "resource_id"
    ],
    "ccn": [
        "resource_id",
        "name"
    ],
    "ccn_attach": [
        "resource_id"
    ],
    "ccn_bandwidth": [
        "resource_id"
    ],
    "instance": [
        "resource_id",
        "ipaddress",
        "public_ip",
        "zone",
        "image_id",
        "tag",
        "vpc_id",
        "subnet_id"
    ],
    "mysql": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "mysql_database": [
        "resource_id",
    ],
    "mysql_account": [
        "resource_id",
        "instance_id",
        "name"
    ],
    "mysql_privilege": [
        "resource_id",
    ],
    "mysql_backup": [
        "resource_id",
    ],
    "mariadb": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "postgreSQL": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "rds": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "nosql": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "mongodb": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "kvstore": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "redis": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "memcached": [
        "resource_id",
        "ipaddress",
        "port",
        "engine",
        "version",
        "name",
        "vpc_id",
        "subnet_id",
        "tag"
    ],
    "memcached_backup": [
        "resource_id"
    ],
    "redis_backup": [
        "resource_id"
    ],
    "kvstore_backup": [
        "resource_id"
    ],
}


def property_necessary(resource_name, resource_property):
    if resource_name not in resouce_property_models.keys():
        return

    columns_property = resouce_property_models.get(resource_name)
    for column in columns_property:
        if column not in resource_property.keys():
            raise ValueError("缺少必要的property: %s" % column)


def output_necessary(resource_name, resource_output):
    if resource_name not in output_property_models.keys():
        return

    columns_property = output_property_models.get(resource_name)
    for column in columns_property:
        if column not in resource_output.keys():
            raise ValueError("缺少必要的output property: %s" % column)

    for key in resource_output.keys():
        if key not in columns_property:
            raise ValueError("不合法的output property: %s， 允许值：%s" % (key, ",".join(columns_property)))


def source_necessary(resource_name, data_source):
    if resource_name not in data_source_models.keys():
        return

    columns_property = data_source_models.get(resource_name)
    for column in columns_property:
        if column not in data_source.keys():
            raise ValueError("缺少必要的data source 字段: %s" % column)


def source_columns_outputs(resource_name):
    res = resouce_property_models.get(resource_name) or []
    res2 = output_property_models.get(resource_name) or []

    x_res = res + res2
    result = {}
    for key in x_res:
        result[key] = ""

    return result
