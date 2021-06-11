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
        "zone_id"
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
    "lb_rule": [
        "listener_id", "lb_id",
        "security_group_id", "frontend_port",
        "name"
    ],
    "lb_server_group": [
        "name",
        "lb_id",
        "instance_id",
        "port"
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
        "zone_id",
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
        "zone_id",
        "image",
        "power_action",
        "force_delete",
        "charge_type"
    ],
    "mysql": [
        "name",
        "charge_type",
        "engine",
        "zone_id",
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
        "parameters",
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
    "db_subnet_group": [
        "subnet_id",
        "name"
    ],
    "mariadb": [
        "charge_type",
        "name",
        "engine",
        "zone_id",
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
        "zone_id",
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
        "zone_id",
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
        "zone_id",
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
        "zone_id",
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
        "zone_id",
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
        "zone_id",
        "version",
        "subnet_id",
        "vpc_id",
        "security_group_id",
        "instance_type",
        "port",
        "password",
        "charge_type"
    ],
    "memcached": [
        "name",
        "engine",
        "zone_id",
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
        "asset_id"
    ],
    "subnet": [
        "asset_id"
    ],
    "route_table": [
        "asset_id"
    ],
    "route_entry": [
        "asset_id"
    ],
    "security_group": [
        "asset_id"
    ],
    "security_group_rule": [
        "asset_id"
    ],
    "nat": [
        "asset_id",
        "ipaddress"
    ],
    "peer_connection": [
        "asset_id"
    ],
    "eip": [
        "asset_id",
        "ipaddress"
    ],
    "eip_association": [
        "asset_id"
    ],
    "lb": [
        "asset_id",
        "ipaddress"
    ],
    "lb_listener": [
        "asset_id"
    ],
    "lb_rule": [
        "asset_id"
    ],
    "lb_server_group": [
        "asset_id"
    ],
    "lb_attach": [
        "asset_id"
    ],
    "disk": [
        "asset_id"
    ],
    "disk_attach": [
        "asset_id"
    ],
    "network_interface": [
        "asset_id",
        "ipaddress"
    ],
    "network_interface_attach": [
        "asset_id"
    ],
    "object_storage": [
        "asset_id",
        "url"
    ],
    "bucket_object": [
        "asset_id"
    ],
    "ccn": [
        "asset_id"
    ],
    "ccn_attach": [
        "asset_id"
    ],
    "ccn_bandwidth": [
        "asset_id"
    ],
    "instance": [
        "asset_id",
        "ipaddress",
        "public_ip"
    ],
    "mysql": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "mysql_database": [
        "asset_id",
    ],
    "mysql_account": [
        "asset_id",
    ],
    "mysql_privilege": [
        "asset_id",
    ],
    "mysql_backup": [
        "asset_id",
    ],
    "db_subnet_group": [
        "asset_id"
    ],
    "mariadb": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "postgreSQL": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "rds": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "nosql": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "mongodb": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "kvstore": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "redis": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "memcached": [
        "asset_id",
        "ipaddress",
        "port"
    ],
    "memcached_backup": [
        "asset_id"
    ],
    "redis_backup": [
        "asset_id"
    ],
    "kvstore_backup": [
        "asset_id"
    ],
}

data_source_models = {
    "vpc": [
        "asset_id",
        "cidr"
    ],
    "subnet": [
        "asset_id",
        "cidr",
        "vpc_id"
    ],
    "route_table": [
        "asset_id",
    ],
    "route_entry": [
        "asset_id",
        "route_table_id"
    ],
    "security_group": [
        "asset_id",
        "name",
    ],
    "security_group_rule": [
        "asset_id",
        "security_group_id"
    ],
    "nat": [
        "asset_id",
        "name",
    ],
    "peer_connection": [
        "asset_id",
        "peer_vpc_id"
    ],
    "eip": [
        "asset_id",
        "ipaddress"
    ],
    "eip_association": [
        "asset_id",
        "instance_id"
    ],
    "lb": [
        "asset_id",
        "name"
    ],
    "lb_listener": [
        "asset_id",
        "lb_id"
    ],
    "lb_rule": [
        "asset_id",
        "listener_id",
        "lb_id",
    ],
    "lb_server_group": [
        "asset_id",
        "lb_id",
        "instance_id"
    ],
    "lb_attach": [
        "asset_id",
        "instance_id"
    ],
    "disk": [
        "asset_id",
        "name",
        "instance_id"
    ],
    "disk_attach": [
        "asset_id",
        "instance_id"
    ],
    "network_interface": [
        "asset_id",
    ],
    "network_interface_attach": [
        "asset_id"
    ],
    "object_storage": [
        "asset_id"
    ],
    "bucket_object": [
        "asset_id"
    ],
    "ccn": [
        "asset_id"
    ],
    "ccn_attach": [
        "asset_id"
    ],
    "ccn_bandwidth": [
        "asset_id"
    ],
    "instance": [
        "asset_id",
        "ipaddress"
    ],
    "mysql": [
        "asset_id",
        "ipaddress"
    ],
    "mysql_database": [
        "asset_id",
    ],
    "db_subnet_group": [
        "asset_id"
    ],
    "mysql_account": [
        "asset_id",
        "instance_id",
        "name"
    ],
    "mysql_privilege": [
        "asset_id",
    ],
    "mysql_backup": [
        "asset_id",
    ],
    "mariadb": [
        "asset_id"
    ],
    "postgreSQL": [
        "asset_id"
    ],
    "rds": [
        "asset_id"
    ],
    "nosql": [
        "asset_id"
    ],
    "mongodb": [
        "asset_id"
    ],
    "kvstore": [
        "asset_id"
    ],
    "redis": [
        "asset_id"
    ],
    "memcached": [
        "asset_id",
    ],
    "memcached_backup": [
        "asset_id"
    ],
    "redis_backup": [
        "asset_id"
    ],
    "kvstore_backup": [
        "asset_id"
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

    # for key in resource_output.keys():
    #     if key not in columns_property:
    #         raise ValueError("不合法的output property: %s， 允许值：%s" % (key, ",".join(columns_property)))


def data_source_output_necessary(resource_name, resource_property):
    if resource_name not in resouce_property_models.keys():
        return

    if not resource_property:
        return

    columns_property = resouce_property_models.get(resource_name)
    for column in columns_property:
        if column not in resource_property.keys():
            raise ValueError("data_source_output缺少必要的property: %s" % column)

    columns_property = output_property_models.get(resource_name)
    for column in columns_property:
        if column not in resource_property.keys():
            raise ValueError("data_source_output缺少必要的property: %s" % column)


def source_necessary(resource_name, data_source):
    if resource_name not in data_source_models.keys():
        return

    if not data_source:
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
