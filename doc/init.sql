#@v0.1.0-begin@;

DROP TABLE IF EXISTS `cloud_providers`;

CREATE TABLE `cloud_providers` (
  `id` VARCHAR(64) NOT NULL,
  `display_name` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) NOT NULL,
  `secret_id` VARCHAR(256),
  `secret_key` VARCHAR(256),
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


DROP TABLE IF EXISTS `cloud_secret`;

CREATE TABLE `cloud_secret` (
  `id` VARCHAR(64) NOT NULL,
  `name` VARCHAR(64) NOT NULL,
  `display_name` VARCHAR(64) DEFAULT NULL,
  `provider` VARCHAR(64) NOT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `secret_info` VARCHAR(2048) NOT NULL,
  `extend_info` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_name` (`name`, `provider`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `resource`;

CREATE TABLE `resource` (
  `id` varchar(64) NOT NULL,
  `provider` varchar(64) NOT NULL,
  `resource_type` varchar(64) NOT NULL,
  `resource_name` varchar(64) NOT NULL,
  `extend_info` text NOT NULL,
  `resource_property` text NOT NULL,
  `resource_output` text,
  `data_source_name` varchar(64) DEFAULT NULL,
  `data_source_argument` varchar(64) DEFAULT NULL,
  `data_source` text,
  `data_source_output` varchar(2048) DEFAULT NULL,
  `is_locked` tinyint(1) DEFAULT '0',
  `created_time` datetime DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  `deleted_time` datetime DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT '1',
  `is_deleted` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_property` (`provider`,`resource_type`,`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `common_keys`;

CREATE TABLE `common_keys` (
  `id` VARCHAR(64) NOT NULL,
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
  `id` VARCHAR(64) NOT NULL,
  `provider` VARCHAR(64) NOT NULL,
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


DROP TABLE IF EXISTS `cloud_resource`;

CREATE TABLE `cloud_resource` (
  `id` VARCHAR(64) NOT NULL,
  `provider_id` VARCHAR(64) DEFAULT NULL,
  `provider` VARCHAR(64) DEFAULT NULL,
  `region` VARCHAR(64) DEFAULT NULL,
  `zone` VARCHAR(64) DEFAULT NULL,
  `resource_name` VARCHAR(64) NOT NULL,
  `resource_id` VARCHAR(64) DEFAULT NULL,
  `owner_id` VARCHAR(64) DEFAULT NULL,
  `relation_id` VARCHAR(64) DEFAULT NULL,
  `propertys` text DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `result_json` TEXT DEFAULT NULL,
  `output_json` TEXT DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`, `resource_name`),
  INDEX `idx_id` (`resource_id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

ALTER TABLE `cloud_resource`
  CHANGE `resource_id` `resource_id` VARCHAR(255) CHARSET utf8 COLLATE utf8_general_ci NULL;


DROP TABLE IF EXISTS `instance_type`;

CREATE TABLE `instance_type` (
  `id` VARCHAR(64) NOT NULL,
  `provider_id` VARCHAR(64) DEFAULT NULL,
  `provider` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `origin_name` VARCHAR(64) DEFAULT NULL,
  `cpu` int(11) DEFAULT NULL,
  `memory` int(11) DEFAULT NULL,
  `network` VARCHAR(64) DEFAULT NULL,
  `extend_info` text DEFAULT NULL,
  `define_json` text DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
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
  `xid` VARCHAR(64) NOT NULL,
  `id` VARCHAR(64) DEFAULT NULL,
  `resource` VARCHAR(64) DEFAULT NULL,
  `ora_data` text DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
    PRIMARY KEY (`xid`),
  INDEX `idx_id` (`id`, `created_time`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

#@v0.1.0-end@;