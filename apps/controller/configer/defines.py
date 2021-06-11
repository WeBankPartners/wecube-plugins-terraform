# _ coding:utf-8 _*_


xml_register = {
    "region": {
        "apply": {
            "path": "/terraform/v1/az/backend/region/apply",
            "method": "POST",
            "notnull": ["asset_id", "provider"],
            "inputParameters": ['id', 'name', 'provider', 'asset_id', 'extend_info', 'secret'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/az/backend/region/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/az/backend/region/source",
            "method": "POST",
            "notnull": [],
            "inputParameters": ['id', 'provider', 'asset_id', 'name'],
            "outputParameters": ['errorCode', 'errorMessage', 'name', 'id', 'asset_id', 'extend_info',
                                 'provider']
        },
    },
    "az": {
        "apply": {
            "path": "/terraform/v1/az/backend/zone/apply",
            "method": "POST",
            "notnull": ["asset_id", "provider"],
            "inputParameters": ['id', 'name', 'provider', 'asset_id', "region_id", 'extend_info', 'secret'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/az/backend/zone/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/az/backend/zone/source",
            "method": "POST",
            "notnull": [],
            "inputParameters": ['id', 'provider', 'asset_id', 'name', "region_id"],
            "outputParameters": ['errorCode', 'errorMessage', 'name', 'id', 'asset_id', 'extend_info', "region_id",
                                 'provider']
        },
    },
    "vpc": {
        "apply": {
            "path": "/terraform/v1/network/backend/vpc/apply",
            "method": "POST",
            "notnull": ["name", "cidr", "region", "provider"],
            "inputParameters": ['id', 'name', 'secret', 'provider', "region_id", 'cidr',  'asset_id',
                                'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/vpc/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/vpc/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'cidr', 'id'],
            "outputParameters": ['errorCode', 'errorMessage', 'name', 'cidr', 'asset_id', "region_id", 'secret',
                                 'provider']
        },
    },
    "subnet": {
        "apply": {
            "path": "/terraform/v1/network/backend/subnet/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', "zone_id", "region_id", 'cidr'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', "zone_id", "region_id", 'cidr',
                                'asset_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/subnet/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/subnet/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', "zone_id", 'cidr', 'vpc_id', "id"],
            "outputParameters": ["region_id", 'secret', 'provider', 'errorCode', 'name', "zone_id", 'asset_id', 'vpc_id',
                                 'cidr', 'errorMessage']
        }
    },
    "route_table": {
        "apply": {
            "path": "/terraform/v1/network/backend/route_table/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', "zone_id", "region_id",
                                'asset_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/route_table/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/route_table/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', "id"],
            "outputParameters": ["region_id", 'secret', 'provider', 'name', 'asset_id', 'errorMessage', 'errorCode',
                                 'vpc_id']
        }
    },
    "route_entry": {
        "apply": {
            "path": "/terraform/v1/network/backend/route_entry/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', 'destination', 'route_table_id', 'next_type', 'next_hub',
                        "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'destination', 'route_table_id',
                                'next_type', 'next_hub', "zone_id", "region_id", 'resource_id', 'asset_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/route_entry/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/route_entry/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'route_table_id', "id"],
            "outputParameters": ["region_id", 'secret', 'provider', 'next_hub', 'asset_id', 'errorMessage',
                                 'errorCode', 'name', 'destination', 'next_type', 'route_table_id']
        }
    },
    "peer_connection": {
        "apply": {
            "path": "/terraform/v1/network/backend/peer_connection/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', 'peer_vpc_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'peer_vpc_id', 'peer_region', "zone_id",
                                "region_id", 'asset_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/peer_connection/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/peer_connection/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id',  'peer_vpc_id', "id"],
            "outputParameters": ["region_id", 'secret', 'provider', 'name', 'asset_id', 'errorMessage', 'errorCode',
                                 'vpc_id', 'peer_vpc_id', 'peer_region']
        }
    },
    "security_group": {
        "apply": {
            "path": "/terraform/v1/network/backend/security_group/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', "zone_id", "region_id",
                                'asset_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/security_group/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/security_group/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'name', 'id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'vpc_id']
        }
    },
    "security_group_rule": {
        "apply": {
            "path": "/terraform/v1/network/backend/security_group_rule/apply",
            "method": "POST",
            "notnull": ['provider', 'security_group_id', "region_id", 'type', 'cidr_ip', 'ip_protocol', 'ports', 'policy'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'security_group_id', "zone_id", "region_id", 'type',
                                'cidr_ip', 'ip_protocol', 'ports', 'policy', 'resource_id', 'asset_id', 'description',
                                'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "asset_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/security_group_rule/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/security_group_rule/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'security_group_id'],
            "outputParameters":["region_id", 'secret', 'provider', 'asset_id', 'errorMessage',
                                'errorCode', 'name', 'security_group_id', 'type', 'cidr_ip',
                                'ip_protocol', 'ports', 'policy', 'description',
                                'from_port', 'to_port', 'priority', 'nic_type']
        }
    },
    "nat": {
        "apply": {
            "path": "/terraform/v1/network/backend/nat/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'subnet_id', 'eip', "zone_id", "region_id",
                                 'asset_id', 'extend_info', 'bandwidth'],
            "outputParameters": ['errorMessage', 'errorCode', 'ipaddress', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/nat/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/nat/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'name','id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'vpc_id', 'eip', 'ipaddress', 'bandwidth']
        }
    },
    "eip": {
        "apply": {
            "path": "/terraform/v1/network/backend/eip/apply",
            "method": "POST",
            "notnull": ['name', 'provider', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', "zone_id", "region_id",  'asset_id',
                                'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'ipaddress', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/eip/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/eip/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id',  'ipaddress', 'id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'ipaddress', "charge_type"]
        }
    },
    "eip_association": {
        "apply": {
            "path": "/terraform/v1/network/backend/eip_association/apply",
            "method": "POST",
            "notnull": ['provider', 'eip_id', 'instance_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'eip_id', 'instance_id', 'private_ip', "zone_id",
                                "region_id", 'resource_id', 'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/eip_association/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "ccn": {
        "apply": {
            "path": "/terraform/v1/network/backend/ccn/apply",
            "method": "POST",
            "notnull": ['name', 'provider', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', "zone_id", "region_id",  'asset_id',
                                'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'ipaddress', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/ccn/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/ccn/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name']
        }
    },
    "ccn_attach": {
        "apply": {
            "path": "/terraform/v1/network/backend/ccn_attach/apply",
            "method": "POST",
            "notnull": ['provider', 'ccn_id', 'instance_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'ccn_id', 'instance_id', 'instance_type',
                                'instance_region', "zone_id", "region_id", 'resource_id', 'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/ccn_attach/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "ccn_bandwidth": {
        "apply": {
            "path": "/terraform/v1/network/backend/ccn_bandwidth/apply",
            "method": "POST",
            "notnull": ['provider', 'ccn_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'ccn_id', 'from_region', 'dest_region', 'bandwidth',
                                "zone_id", "region_id",  'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/ccn_bandwidth/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "disk": {
        "apply": {
            "path": "/terraform/v1/storage/backend/disk/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'type', 'size', "zone_id", "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'type', 'size', "zone_id", "region_id",
                                'asset_id', 'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/storage/backend/disk/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/storage/backend/disk/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id',
                                'name', 'instance_id', "id"],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'type', 'size', "zone_id", "charge_type", "instance_id"]
        }
    },
    "disk_attach": {
        "apply": {
            "path": "/terraform/v1/storage/backend/disk_attach/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'disk_id', 'instance_id', "zone_id", "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'disk_id', 'instance_id', "zone_id", "region_id",
                                'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/storage/backend/disk/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "object_storage": {
        "apply": {
            "path": "/terraform/v1/storage/backend/object_storage/apply",
            "method": "POST",
            "notnull": ['name', 'provider', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'acl', 'appid', "zone_id", "region_id",
                                'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'url', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/storage/backend/object_storage/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/storage/backend/object_storage/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'acl', 'url']
        }
    },
    "instance": {
        "apply": {
            "path": "/terraform/v1/vm/backend/instance/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', 'hostname', 'image', 'instance_type', "zone_id", "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'subnet_id', 'hostname', 'image', 'instance_type',
                                'disk_type', 'disk_size', 'password', 'security_group_id', 'vpc_id', 'power_action',
                                 'asset_id', 'data_disks', "zone_id", "region_id", 'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'ipaddress', 'cpu', 'memory', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/vm/backend/instance/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/vm/backend/instance/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'ipaddress', 'id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'subnet_id', 'hostname', 'ipaddress', 'image', 'instance_type', 'disk_type',
                                 'disk_size', 'password', 'security_group_id', 'vpc_id', 'data_disks', "zone_id",
                                 'power_action', 'force_delete', "charge_type"]
        }
    },
    "network_interface": {
        "apply": {
            "path": "/terraform/v1/storage/backend/network_interface/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', "zone_id", "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'ipaddress', 'subnet_id', 'vpc_id',
                                'security_group_id', "zone_id", "region_id", 'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'ipaddress', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/storage/backend/network_interface/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/storage/backend/network_interface/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'ipaddress', 'vpc_id', 'subnet_id', 'security_group_id']
        }
    },
    "network_interface_attach": {
        "apply": {
            "path": "/terraform/v1/vm/backend/network_interface/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'network_interface_id', 'instance_id', "zone_id", "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'network_interface_id', 'instance_id', "zone_id",
                                "region_id", 'extend_info', 'asset_id', 'resource_id'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/vm/backend/network_interface/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "lb": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'subnet_id', 'network_type', 'vpc_id', "zone_id",
                                "region_id", 'ipaddress', 'asset_id', 'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'name', "id"],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'network_type', 'vpc_id', 'subnet_id', 'ipaddress', "charge_type"]
        }
    },
    "lb_listener": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb_listener/apply",
            "method": "POST",
            "notnull": ['provider', 'lb_id', 'port', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'lb_id', 'port', 'protocol', 'backend_port',
                                'health_check', 'health_check_uri', "zone_id", "region_id", 'asset_id',
                                'extend_info', 'default_action'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb_listener/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb_listener/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'lb_id', 'id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode',
                                 'name', 'lb_id', 'port', 'protocol', 'health_check', 'health_check_uri',
                                 'default_action']
        }
    },
    "lb_rule": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb_rule/apply",
            "method": "POST",
            "notnull": ['provider', "region_id", 'lb_id'],
            "inputParameters": ['id', 'provider', 'secret', "region_id", "zone_id", 'listener_id', 'extend_info',
                                'lb_id', 'security_group_id', 'frontend_port', 'name',
                                'asset_id', 'action', 'condition', 'resource_id'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb_rule/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb_rule/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'listener_id', 'lb_id', 'id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode',
                                 'name', 'lb_id', 'listener_id', "region_id", "zone_id",
                                 'security_group_id', 'frontend_port']
        }
    },
    "lb_server_group": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb_server_group/apply",
            "method": "POST",
            "notnull": ['provider', "region_id", 'name', 'lb_id'],
            "inputParameters": ['id', 'provider', 'secret', "region_id", "zone_id",
                                'name', 'lb_id', "asset_id", 'instance_id', 'port'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb_server_group/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb_server_group/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', "id",
                                'asset_id', 'instance_id', 'lb_id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id',
                                 'errorMessage', 'errorCode', 'name',
                                 'lb_id', 'instance_id', "region_id", "zone_id", 'port']
        }
    },
    "lb_attach": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb_attach/apply",
            "method": "POST",
            "notnull": ['provider', 'lb_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'lb_id', 'listener_id', 'backend_servers',
                                'instance_id', 'weight', 'port', "zone_id", "region_id", 'extend_info',
                                'asset_id', 'group_id', 'resource_id'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb_attach/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb_attach/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider',
                                'asset_id', 'instance_id', 'lb_id'],
            "outputParameters":["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                'lb_id', 'listener_id', 'backend_servers', 'instance_id', 'weight', 'port']
        }
    },
    "mysql": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', 'version', 'instance_type', "zone_id", "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'subnet_id', 'user', 'password', 'port',
                                'disk_type', 'disk_size', 'version', 'instance_type', 'vpc_id', 'security_group_id',
                                'second_slave_zone', 'first_slave_zone', "zone_id", "region_id", 'asset_id',
                                'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'asset_id', 'user', 'password', 'ipaddress', 'port',
                                 'id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/database/backend/mysql/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'ipaddress', "id"],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'subnet_id', 'user', 'password', 'port', 'disk_type', 'disk_size', 'version',
                                 'instance_type', 'vpc_id', 'security_group_id', 'second_slave_zone',
                                 'first_slave_zone', "zone_id", 'ipaddress', "charge_type"]
        }
    },
    "mysql_database": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql_database/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'mysql_id', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'mysql_id', "zone_id", "region_id", 'resource_id',
                                'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql_database/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "mysql_account": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql_account/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'mysql_id', 'password', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'mysql_id', 'password', "zone_id", "region_id",
                                'resource_id', 'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql_account/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "mysql_privilege": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql_privilege/apply",
            "method": "POST",
            "notnull": ['provider', 'mysql_id', 'username', 'database', 'privileges', "region_id"],
            "inputParameters": ['id', 'secret', 'provider', 'mysql_id', 'username', 'database', 'privileges', "zone_id",
                                "region_id", 'resource_id', 'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql_privilege/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "mysql_backup": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql_backup/apply",
            "method": "POST",
            "notnull": ['provider', 'mysql_id', 'backup_model', 'backup_time', "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'mysql_id', 'backup_model', 'backup_time', "zone_id",
                                "region_id", 'resource_id', 'asset_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'asset_id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql_backup/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        }
    },
    "db_subnet_group": {
        "apply": {
            "path": "/terraform/v1/database/backend/db_subnet_group/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', "zone_id", "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'subnet_id',
                                "zone_id", "region_id", 'asset_id',
                                'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'asset_id', 'id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/db_subnet_group/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/database/backend/db_subnet_group/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'id'],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'subnet_id', "zone_id", ]
        }
    },
    "redis": {
        "apply": {
            "path": "/terraform/v1/database/backend/redis/apply",
            "method": "POST",
            "notnull": ['provider', 'instance_type', "zone_id", "region_id"],
            "inputParameters": ['id', 'name', 'secret', 'provider',  'password', 'port',
                                 'version', 'instance_type', 'vpc_id', 'security_group_id',
                                "zone_id", "region_id", 'asset_id', 'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'asset_id', 'ipaddress', 'port',
                                 'id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/redis/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "id"]
        },
        "query": {
            "path": "/terraform/v1/database/backend/redis/source",
            "method": "POST",
            "notnull": ["region_id", "provider"],
            "inputParameters": ["region_id", 'secret', 'provider', 'asset_id', "id"],
            "outputParameters": ["region_id", 'secret', 'provider', 'asset_id', 'errorMessage', 'errorCode', 'name',
                                 'subnet_id',  'password', 'port', 'version',
                                 'instance_type', 'vpc_id', 'security_group_id',  "zone_id", 'ipaddress', "charge_type"]
        }
    },
}

# print(xml_register.keys())
# res = {}
# for key, define in xml_register.items():
#     res[key] = define.keys()
#
# print res