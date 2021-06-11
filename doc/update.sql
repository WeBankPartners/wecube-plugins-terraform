
#@v0.2.0-begin@;
ALTER TABLE cloud_secret ADD server varchar(256) NULL  after  `region`;


DROP TABLE IF EXISTS `cloud_region`;

CREATE TABLE `cloud_region` (
  `id` VARCHAR(64) NOT NULL,
  `name` VARCHAR(128) DEFAULT NULL,
  `provider` VARCHAR(128) NOT NULL,
  `asset_id` VARCHAR(128) NOT NULL,
  `extend_info` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_asset` (`asset_id`, `provider`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `cloud_zone`;

CREATE TABLE `cloud_zone` (
  `id` VARCHAR(64) NOT NULL,
  `name` VARCHAR(128) DEFAULT NULL,
  `provider` VARCHAR(128) NOT NULL,
  `asset_id` VARCHAR(128) NOT NULL,
  `region` VARCHAR(128) DEFAULT NULL,
  `extend_info` TEXT DEFAULT NULL,
  `created_time` DATETIME DEFAULT NULL,
  `updated_time` DATETIME DEFAULT NULL,
  `deleted_time` DATETIME DEFAULT NULL,
  `enabled` BOOL DEFAULT TRUE,
  `is_deleted` BOOL DEFAULT FALSE,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_asset` (`asset_id`, `provider`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

#@v0.2.0-end@;

#@v0.3.0-begin@;


ALTER TABLE resource MODIFY COLUMN data_source_argument varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE resource ADD pre_action varchar(256) NULL  after  `data_source_output`;
ALTER TABLE resource ADD pre_action_output varchar(512) NULL  after  `pre_action`;

ALTER TABLE resource MODIFY COLUMN data_source_name varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL;

ALTER TABLE instance_type ADD `type` varchar(64) default 'instance' after  `name`;


#@v0.3.0-end@;


