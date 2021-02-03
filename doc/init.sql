DROP TABLE IF EXISTS `cloud_providers`;

CREATE TABLE `cloud_providers` (
  `id` VARCHAR(36) NOT NULL,
  `display_name` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) NOT NULL,
  `secret_id` VARCHAR(256) NOT NULL,
  `secret_key` VARCHAR(256) NOT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `plugin_source` VARCHAR(64) DEFAULT NULL,
  `extend_info` TEXT DEFAULT NULL,
  `provider_property` TEXT DEFAULT NULL,
  `is_init` BOOL DEFAULT FALSE,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_name` (`name`, `is_deleted`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `resource`;

CREATE TABLE `resource` (
  `id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) NOT NULL,
  `property` VARCHAR(64) NOT NULL,
  `resource_name` VARCHAR(64) NOT NULL,
  `extend_info` text NOT NULL,
  `resource_property` text NOT NULL,
  `output_property` text DEFAULT NULL,
  `is_locked` BOOL DEFAULT FALSE,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_property` (`provider`, `property`, `is_deleted`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `common_keys`;

CREATE TABLE `common_keys` (
  `id` VARCHAR(36) NOT NULL,
  `resource` VARCHAR(64) NOT NULL,
  `key` VARCHAR(64) NOT NULL,
  `property` VARCHAR(64) NOT NULL,
  `is_locked` BOOL DEFAULT FALSE,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `config`;

CREATE TABLE `config` (
  `id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) NOT NULL,
  `resource` VARCHAR(64) NOT NULL,
  `property` VARCHAR(64) DEFAULT NULL,
  `value_config` text NOT NULL,
  `is_locked` BOOL DEFAULT FALSE,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_pro_res` (`provider`, `resource`, `property`, `is_deleted`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `vpc`;

CREATE TABLE `vpc` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `cidr` VARCHAR(128) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `subnet`;

CREATE TABLE `subnet` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `vpc` VARCHAR(64) DEFAULT NULL,
  `cidr` VARCHAR(128) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `route_table`;

CREATE TABLE `route_table` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `vpc` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `route_entry`;

CREATE TABLE `route_entry` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64),
  `vpc` VARCHAR(64) DEFAULT NULL,
  `route_table` VARCHAR(64) DEFAULT NULL,
  `next_type` VARCHAR(64) DEFAULT NULL,
  `next_hub` VARCHAR(128) DEFAULT NULL,
  `destination` VARCHAR(128) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;



DROP TABLE IF EXISTS `security_group`;

CREATE TABLE `security_group` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `vpc` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `security_group_rule`;

CREATE TABLE `security_group_rule` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `description` VARCHAR(64) DEFAULT NULL,
  `security_group_id` VARCHAR(64) DEFAULT NULL,
  `type` VARCHAR(64) DEFAULT NULL,
  `cidr_ip` VARCHAR(64) DEFAULT NULL,
  `ip_protocol` VARCHAR(64) DEFAULT NULL,
  `ports` VARCHAR(64) DEFAULT NULL,
  `policy` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `nat_gateway`;

CREATE TABLE `nat_gateway` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `vpc` VARCHAR(64) DEFAULT NULL,
  `subnet` VARCHAR(64) DEFAULT NULL,
  `ipaddress` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `eip`;

CREATE TABLE `eip` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `ipaddress` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `eip_association`;

CREATE TABLE `eip_association` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `eip_id` VARCHAR(64) DEFAULT NULL,
  `instance_id` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `load_balance`;

CREATE TABLE `load_balance` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `ipaddress` VARCHAR(64) DEFAULT NULL,
  `subnet_id` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `lb_listener`;

CREATE TABLE `lb_listener` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `lb_id` VARCHAR(36) DEFAULT NULL,
  `port` INT(11) DEFAULT NULL,
  `protocol` VARCHAR(36) DEFAULT NULL,
  `backend_port` INT(11) DEFAULT NULL,
  `health_check` VARCHAR(32) DEFAULT NULL,
  `health_check_uri` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `lb_attach`;

CREATE TABLE `lb_attach` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `lb_id` VARCHAR(36) DEFAULT NULL,
  `listener_id` VARCHAR(36) DEFAULT NULL,
  `backend_servers` text DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `lb_attach_instances`;

CREATE TABLE `lb_attach_instances` (
  `id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `lb_id` VARCHAR(36) DEFAULT NULL,
  `listener_id` VARCHAR(36) DEFAULT NULL,
  `instance_id` VARCHAR(36) DEFAULT NULL,
  `port` INT(11) DEFAULT NULL,
  `weigh` INT(11) DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `disk`;

CREATE TABLE `disk` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `type` VARCHAR(64) DEFAULT NULL,
  `size` int(11) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `disk_attach`;

CREATE TABLE `disk_attach` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `disk_id` VARCHAR(64) DEFAULT NULL,
  `instance_id` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `object_storage`;

CREATE TABLE `object_storage` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) NOT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) NOT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `acl` VARCHAR(64) DEFAULT NULL,
  `url` VARCHAR(128) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `bucket_object`;

CREATE TABLE `bucket_object` (
  `id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) NOT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) NOT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `bucket_id` VARCHAR(64) DEFAULT NULL,
  `key` VARCHAR(128) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `vm_network_interface`;

CREATE TABLE `vm_network_interface` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `subnet_id` VARCHAR(36) DEFAULT NULL,
  `ipaddress` VARCHAR(36) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `vm_network_interface_attach`;

CREATE TABLE `vm_network_interface_attach` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `network_interface_id` VARCHAR(64) DEFAULT NULL,
  `instance_id` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `instance`;

CREATE TABLE `instance` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `hostname` VARCHAR(64) DEFAULT NULL,
  `instance_type` VARCHAR(64) DEFAULT NULL,
  `disk_type` VARCHAR(64) DEFAULT NULL,
  `disk_size` VARCHAR(64) DEFAULT NULL,
  `subnet_id` VARCHAR(64) DEFAULT NULL,
  `ipaddress` VARCHAR(64) DEFAULT NULL,
  `public_ip` VARCHAR(64) DEFAULT NULL,
  `image` VARCHAR(64) DEFAULT NULL,
  `password` VARCHAR(64) DEFAULT NULL,
  `cpu` int(11) DEFAULT NULL,
  `memory` int(11) DEFAULT NULL,
  `power_state` varchar(36) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `instance_type`;

CREATE TABLE `instance_type` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `origin_name` VARCHAR(64) DEFAULT NULL,
  `cpu` int(11) DEFAULT NULL,
  `memory` int(11) DEFAULT NULL,
  `network` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;



DROP TABLE IF EXISTS `rds_db`;

CREATE TABLE `rds_db` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `engine` VARCHAR(64) DEFAULT NULL,
  `version` VARCHAR(32) DEFAULT NULL,
  `instance_type` VARCHAR(64) DEFAULT NULL,
   `cpu` int(11) DEFAULT NULL,
  `memory` int(11) DEFAULT NULL,
  `disk_type` VARCHAR(64) DEFAULT NULL,
  `disk_size` VARCHAR(64) DEFAULT NULL,
  `subnet_id` VARCHAR(64) DEFAULT NULL,
  `ipaddress` VARCHAR(64) DEFAULT NULL,
  `port` VARCHAR(32) DEFAULT NULL,
  `user` VARCHAR(32) DEFAULT NULL,
  `password` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `rds_database`;

CREATE TABLE `rds_database` (
  `id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `rds_id` VARCHAR(64) DEFAULT NULL,
  `engine` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `rds_account`;

CREATE TABLE `rds_account` (
  `id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `rds_id` VARCHAR(64) DEFAULT NULL,
  `engine` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `password` VARCHAR(128) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `rds_account_privilege`;

CREATE TABLE `rds_account_privilege` (
  `id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `rds_id` VARCHAR(64) DEFAULT NULL,
  `engine` VARCHAR(64) DEFAULT NULL,
  `account_name` VARCHAR(64) DEFAULT NULL,
  `database` VARCHAR(64) DEFAULT NULL,
  `privileges` VARCHAR(256) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `rds_backup_policy`;

CREATE TABLE `rds_backup_policy` (
  `id` VARCHAR(36) NOT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `rds_id` VARCHAR(64) DEFAULT NULL,
  `engine` VARCHAR(64) DEFAULT NULL,
  `backup_model` VARCHAR(64) DEFAULT NULL,
  `backup_time` VARCHAR(128) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `nosql`;

CREATE TABLE `nosql` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `engine` VARCHAR(64) DEFAULT NULL,
  `version` VARCHAR(32) DEFAULT NULL,
  `instance_type` VARCHAR(64) DEFAULT NULL,
  `disk_type` VARCHAR(64) DEFAULT NULL,
  `disk_size` VARCHAR(64) DEFAULT NULL,
  `subnet_id` VARCHAR(64) DEFAULT NULL,
  `ipaddress` VARCHAR(64) DEFAULT NULL,
  `port` VARCHAR(32) DEFAULT NULL,
  `user` VARCHAR(32) DEFAULT NULL,
  `password` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `kvstore`;

CREATE TABLE `kvstore` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `engine` VARCHAR(64) DEFAULT NULL,
  `version` VARCHAR(32) DEFAULT NULL,
  `instance_type` VARCHAR(64) DEFAULT NULL,
  `subnet_id` VARCHAR(64) DEFAULT NULL,
  `ipaddress` VARCHAR(64) DEFAULT NULL,
  `port` VARCHAR(64) DEFAULT NULL,
  `password` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `kvstore_backup`;

CREATE TABLE `kvstore_backup` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `kvstore_id` VARCHAR(36) DEFAULT NULL,
  `backup_time` VARCHAR(64) DEFAULT NULL,
  `backup_period` VARCHAR(128) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `connect_network`;

CREATE TABLE `connect_network` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ccn_attach`;

CREATE TABLE `ccn_attach` (
  `id` VARCHAR(36) NOT NULL,
   `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `ccn_id` VARCHAR(64) DEFAULT NULL,
  `instance_type` VARCHAR(32) DEFAULT NULL,
  `instance_region` VARCHAR(32) DEFAULT NULL,
  `instance_id` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ccn_bandwidth`;

CREATE TABLE `ccn_bandwidth` (
  `id` VARCHAR(36) NOT NULL,
  `provider_id` VARCHAR(36) DEFAULT NULL,
  `provider` VARCHAR(32) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `ccn_id` VARCHAR(64) DEFAULT NULL,
  `from_region` VARCHAR(32) DEFAULT NULL,
  `dest_region` VARCHAR(32) DEFAULT NULL,
  `bandwidth` VARCHAR(32) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `resource_history`;

CREATE TABLE `resource_history` (
  `id` VARCHAR(36) DEFAULT NULL,
  `resource` VARCHAR(36) DEFAULT NULL,
  `ora_data` text DEFAULT NULL,
  INDEX `idx_id` (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

