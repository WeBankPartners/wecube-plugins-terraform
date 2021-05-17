# _ coding:utf-8 _*_


xml_register = {
    "region": {
        "apply": {
            "path": "/terraform/v1/az/backend/region/apply",
            "method": "POST",
            "notnull": ["asset_id", "provider"],
            "inputParameters": ['id', 'name', 'provider', 'asset_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "destroy": {
            "path": "/terraform/v1/az/backend/region/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
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
            "path": "/terraform/v1/az/backend/az/apply",
            "method": "POST",
            "notnull": ["asset_id", "provider"],
            "inputParameters": ['id', 'name', 'provider', 'asset_id', 'region', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "destroy": {
            "path": "/terraform/v1/az/backend/az/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/az/backend/az/source",
            "method": "POST",
            "notnull": [],
            "inputParameters": ['id', 'provider', 'asset_id', 'name', 'region'],
            "outputParameters": ['errorCode', 'errorMessage', 'name', 'id', 'asset_id', 'extend_info', 'region',
                                 'provider']
        },
    },
    "vpc": {
        "apply": {
            "path": "/terraform/v1/network/backend/vpc/apply",
            "method": "POST",
            "notnull": ["name", "cidr", "region", "provider"],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'region', 'cidr', 'asset_id', 'resource_id',
                                'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "resource_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/vpc/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/vpc/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'tag', 'cidr'],
            "outputParameters": ['errorCode', 'errorMessage', 'name', 'cidr', 'resource_id', 'region', 'secret',
                                 'provider']
        },
    },
    "subnet": {
        "apply": {
            "path": "/terraform/v1/network/backend/subnet/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', 'zone', 'region', 'cidr'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'zone', 'region', 'cidr', 'asset_id',
                                'resource_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "resource_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/subnet/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/subnet/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'zone', 'cidr', 'tag', 'vpc_id'],
            "outputParameters": ['region', 'secret', 'provider', 'errorCode', 'name', 'zone', 'resource_id', 'vpc_id',
                                 'cidr', 'errorMessage']
        }
    },
    "route_table": {
        "apply": {
            "path": "/terraform/v1/network/backend/route_table/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'zone', 'region', 'asset_id',
                                'resource_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "resource_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/route_table/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/route_table/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'tag', 'vpc_id'],
            "outputParameters": ['region', 'secret', 'provider', 'name', 'resource_id', 'errorMessage', 'errorCode',
                                 'vpc_id']
        }
    },
    "route_entry": {
        "apply": {
            "path": "/terraform/v1/network/backend/route_entry/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', 'destination', 'route_table_id', 'next_type', 'next_hub',
                        'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'destination', 'route_table_id',
                                'next_type', 'next_hub', 'zone', 'region', 'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "resource_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/route_entry/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/route_entry/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'route_table_id', 'cidr', 'type'],
            "outputParameters": ['region', 'secret', 'provider', 'next_hub', 'resource_id', 'errorMessage',
                                 'errorCode', 'name', 'destination', 'next_type', 'route_table_id']
        }
    },
    "peer_connection": {
        "apply": {
            "path": "/terraform/v1/network/backend/peer_connection/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', 'peer_vpc_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'peer_vpc_id', 'peer_region', 'zone',
                                'region', 'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "resource_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/peer_connection/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/peer_connection/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'vpc_id', 'peer_vpc_id',
                                'peer_region'],
            "outputParameters": ['region', 'secret', 'provider', 'name', 'resource_id', 'errorMessage', 'errorCode',
                                 'vpc_id', 'peer_vpc_id', 'peer_region']
        }
    },
    "security_group": {
        "apply": {
            "path": "/terraform/v1/network/backend/security_group/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'zone', 'region', 'asset_id',
                                'resource_id', 'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "resource_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/security_group/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/security_group/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'vpc_id', 'tag'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'vpc_id']
        }
    },
    "security_group_rule": {
        "apply": {
            "path": "/terraform/v1/network/backend/security_group_rule/apply",
            "method": "POST",
            "notnull": ['provider', 'security_group_id', 'region', 'type', 'cidr_ip', 'ip_protocol', 'ports', 'policy'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'security_group_id', 'zone', 'region', 'type',
                                'cidr_ip', 'ip_protocol', 'ports', 'policy', 'asset_id', 'resource_id', 'description',
                                'extend_info'],
            "outputParameters": ["errorMessage", "errorCode", "id", "resource_id"]
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/security_group_rule/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "nat": {
        "apply": {
            "path": "/terraform/v1/network/backend/nat/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'vpc_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'vpc_id', 'subnet_id', 'eip', 'zone', 'region',
                                'asset_id', 'resource_id', 'extend_info', 'bandwidth'],
            "outputParameters": ['errorMessage', 'errorCode', 'ipaddress', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/nat/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/nat/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'type', 'tag', 'vpc_id'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'vpc_id', 'eip', 'ipaddress', 'bandwidth']
        }
    },
    "eip": {
        "apply": {
            "path": "/terraform/v1/network/backend/eip/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'zone', 'region', 'asset_id', 'resource_id',
                                'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'ipaddress', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/eip/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/eip/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'ipaddress', 'tag'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'ipaddress', "charge_type"]
        }
    },
    "eip_association": {
        "apply": {
            "path": "/terraform/v1/network/backend/eip_association/apply",
            "method": "POST",
            "notnull": ['provider', 'eip_id', 'instance_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'eip_id', 'instance_id', 'private_ip', 'zone',
                                'region', 'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/eip_association/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "ccn": {
        "apply": {
            "path": "/terraform/v1/network/backend/ccn/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'zone', 'region', 'asset_id', 'resource_id',
                                'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'ipaddress', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/ccn/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/network/backend/ccn/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name']
        }
    },
    "ccn_attach": {
        "apply": {
            "path": "/terraform/v1/network/backend/ccn_attach/apply",
            "method": "POST",
            "notnull": ['provider', 'ccn_id', 'instance_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'ccn_id', 'instance_id', 'instance_type',
                                'instance_region', 'zone', 'region', 'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/ccn_attach/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "ccn_bandwidth": {
        "apply": {
            "path": "/terraform/v1/network/backend/ccn_bandwidth/apply",
            "method": "POST",
            "notnull": ['provider', 'ccn_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'ccn_id', 'from_region', 'dest_region', 'bandwidth',
                                'zone', 'region', 'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/network/backend/ccn_bandwidth/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "disk": {
        "apply": {
            "path": "/terraform/v1/storage/backend/disk/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'type', 'size', 'zone', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'type', 'size', 'zone', 'region', 'asset_id',
                                'resource_id', 'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/storage/backend/disk/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/storage/backend/disk/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id',
                                'name', 'instance_id', 'type', 'tag', 'zone'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'type', 'size', 'zone', "charge_type"]
        }
    },
    "object_storage": {
        "apply": {
            "path": "/terraform/v1/storage/backend/object_storage/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'acl', 'appid', 'zone', 'region', 'asset_id',
                                'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'url', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/storage/backend/object_storage/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/storage/backend/object_storage/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'tag'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'acl', 'url']
        }
    },
    "instance": {
        "apply": {
            "path": "/terraform/v1/vm/backend/instance/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', 'hostname', 'image', 'instance_type', 'zone', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'subnet_id', 'hostname', 'image', 'instance_type',
                                'disk_type', 'disk_size', 'password', 'security_group_id', 'vpc_id', 'power_action',
                                'asset_id', 'resource_id', 'data_disks', 'zone', 'region', 'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'ipaddress', 'cpu', 'memory', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/vm/backend/instance/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/vm/backend/instance/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'ipaddress', 'public_ip', 'zone',
                                'image_id', 'tag', 'vpc_id', 'subnet_id'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'subnet_id', 'hostname', 'ipaddress', 'image', 'instance_type', 'disk_type',
                                 'disk_size', 'password', 'security_group_id', 'vpc_id', 'data_disks', 'zone',
                                 'power_action', 'force_delete', "charge_type"]
        }
    },
    "network_interface": {
        "apply": {
            "path": "/terraform/v1/storage/backend/network_interface/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', 'zone', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'ipaddress', 'subnet_id', 'vpc_id',
                                'security_group_id', 'zone', 'region', 'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'ipaddress', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/storage/backend/network_interface/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/storage/backend/network_interface/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'vpc_id', 'subnet_id', 'tag',
                                'ipaddress', 'public_ip'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'ipaddress', 'vpc_id', 'subnet_id', 'security_group_id']
        }
    },
    "network_interface_attach": {
        "apply": {
            "path": "/terraform/v1/vm/backend/network_interface/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'network_interface_id', 'instance_id', 'zone', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'network_interface_id', 'instance_id', 'zone',
                                'region', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/vm/backend/network_interface/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "lb": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'subnet_id', 'network_type', 'vpc_id', 'zone',
                                'region', 'asset_id', 'ipaddress', 'resource_id', 'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name', 'vpc_id', 'subnet_id', 'tag',
                                'ipaddress'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'network_type', 'vpc_id', 'subnet_id', 'ipaddress', "charge_type"]
        }
    },
    "lb_listener": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb_listener/apply",
            "method": "POST",
            "notnull": ['provider', 'lb_id', 'port', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'lb_id', 'port', 'protocol', 'backend_port',
                                'health_check', 'health_check_uri', 'zone', 'region', 'asset_id', 'resource_id',
                                'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb_listener/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb_listener/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'lb_id', 'tag'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode',
                                 'name', 'lb_id', 'port', 'protocol', 'health_check', 'health_check_uri']
        }
    },
    "lb_rule": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb_rule/apply",
            "method": "POST",
            "notnull": ['provider', 'region', 'lb_id'],
            "inputParameters": ['id', 'provider', 'secret', 'region', 'zone', 'listener_id', 'extend_info',
                                'lb_id', 'security_group_id', 'frontend_port', 'name'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb_rule/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb_rule/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'listener_id', 'lb_id', 'name'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode',
                                 'name', 'lb_id', 'listener_id', 'region', 'zone',
                                 'security_group_id', 'frontend_port']
        }
    },
    "lb_server_group": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb_server_group/apply",
            "method": "POST",
            "notnull": ['provider', 'region', 'name', 'lb_id'],
            "inputParameters": ['id', 'provider', 'secret', 'region', 'zone',
                                'name', 'lb_id', 'instance_id', 'port'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb_server_group/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/loadbalance/backend/lb_server_group/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider',
                                'resource_id', 'instance_id', 'lb_id', 'name'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id',
                                 'errorMessage', 'errorCode', 'name',
                                 'lb_id', 'instance_id', 'region', 'zone', 'port']
        }
    },
    "lb_attach": {
        "apply": {
            "path": "/terraform/v1/loadbalance/backend/lb_attach/apply",
            "method": "POST",
            "notnull": ['provider', 'lb_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'lb_id', 'listener_id', 'backend_servers',
                                'instance_id', 'weight', 'port', 'zone', 'region', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/loadbalance/backend/lb_attach/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "mysql": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', 'version', 'instance_type', 'zone', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'subnet_id', 'user', 'password', 'port',
                                'disk_type', 'disk_size', 'version', 'instance_type', 'vpc_id', 'security_group_id',
                                'second_slave_zone', 'first_slave_zone', 'zone', 'region', 'asset_id', 'resource_id',
                                'extend_info', "charge_type"],
            "outputParameters": ['errorMessage', 'errorCode', 'resource_id', 'user', 'password', 'ipaddress', 'port',
                                 'id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/database/backend/mysql/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'ipaddress', 'port', 'engine', 'version',
                                'name', 'vpc_id', 'subnet_id', 'tag'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'subnet_id', 'user', 'password', 'port', 'disk_type', 'disk_size', 'version',
                                 'instance_type', 'vpc_id', 'security_group_id', 'second_slave_zone',
                                 'first_slave_zone', 'zone', 'ipaddress', "charge_type"]
        }
    },
    "mysql_database": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql_database/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'mysql_id', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'mysql_id', 'zone', 'region', 'asset_id',
                                'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql_database/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "mysql_account": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql_account/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'mysql_id', 'password', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'mysql_id', 'password', 'zone', 'region',
                                'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql_account/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "mysql_privilege": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql_privilege/apply",
            "method": "POST",
            "notnull": ['provider', 'mysql_id', 'username', 'database', 'privileges', 'region'],
            "inputParameters": ['id', 'secret', 'provider', 'mysql_id', 'username', 'database', 'privileges', 'zone',
                                'region', 'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql_privilege/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "mysql_backup": {
        "apply": {
            "path": "/terraform/v1/database/backend/mysql_backup/apply",
            "method": "POST",
            "notnull": ['provider', 'mysql_id', 'backup_model', 'backup_time', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'mysql_id', 'backup_model', 'backup_time', 'zone',
                                'region', 'asset_id', 'resource_id', 'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'id', 'resource_id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/mysql_backup/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        }
    },
    "db_subnet_group": {
        "apply": {
            "path": "/terraform/v1/database/backend/db_subnet_group/apply",
            "method": "POST",
            "notnull": ['name', 'provider', 'subnet_id', 'zone', 'region'],
            "inputParameters": ['id', 'name', 'secret', 'provider', 'subnet_id',
                                'zone', 'region', 'asset_id', 'resource_id',
                                'extend_info'],
            "outputParameters": ['errorMessage', 'errorCode', 'resource_id', 'id']
        },
        "destroy": {
            "path": "/terraform/v1/database/backend/db_subnet_group/destroy",
            "method": "POST",
            "notnull": ["id"],
            "inputParameters": ["id"],
            "outputParameters": ["errorMessage", "errorCode", "result"]
        },
        "query": {
            "path": "/terraform/v1/database/backend/db_subnet_group/source",
            "method": "POST",
            "notnull": ["region", "provider"],
            "inputParameters": ['region', 'secret', 'provider', 'resource_id', 'name'],
            "outputParameters": ['region', 'secret', 'provider', 'resource_id', 'errorMessage', 'errorCode', 'name',
                                 'subnet_id', 'zone', ]
        }
    },
}

