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
        "eip"
    ],
    "eip": [
        "name"
    ],
    "eip_association": [
        "name",
        "eip_id",
        "instance_id",
        "private_ip"
    ],
    "lb": [
    ],
    "disk": [
        "name",
        "type",
        "size",
        "zone"
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
        "force_delete"
    ],
    "mysql": [
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
        "force_delete"
    ],
    "mariadb": [
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
        "force_delete"
    ],
    "postgreSQL": [
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
        "force_delete"
    ],
    "mongodb": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "instance_type",
        "port",
        "password",
        "force_delete"
    ],
    "kvstore": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "instance_type",
        "port",
        "password",
        "force_delete"
    ],
    "redis": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "instance_type",
        "port",
        "password",
        "force_delete"
    ],
    "memcached": [
        "name",
        "engine",
        "zone",
        "version",
        "subnet_id",
        "instance_type",
        "port",
        "password",
        "force_delete"
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
    "eip": [
        "resource_id",
        "ipaddress"
    ],
    "eip_association": [
        "resource_id"
    ],
    "lb": [
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
    ]
}


def property_necessary(resource_name, resource_property):
    if resource_name not in resouce_property_models.keys():
        return

    columns_property = resouce_property_models.get(resource_name)
    for column in columns_property:
        if column not in resource_property.keys():
            raise ValueError("缺少必要的property: %s" % column)


def output_necessary(resource_name, output_property):
    if resource_name not in output_property_models.keys():
        return

    columns_property = output_property_models.get(resource_name)
    for column in columns_property:
        if column not in output_property.keys():
            raise ValueError("缺少必要的output property: %s" % column)

    for key in output_property.keys():
        if key not in columns_property:
            raise ValueError("不合法的output property: %s， 允许值：%s" % (key, ",".join(columns_property)))
