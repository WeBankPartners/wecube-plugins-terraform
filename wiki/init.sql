SET NAMES utf8 ;
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `interface` (
  `id` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL COMMENT '操作名称',
  `plugin` varchar(32) NOT NULL,
  `description` varchar(64) DEFAULT '' COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT 'update_user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_plugin_name` (`plugin`,`name`),
  KEY `interface_plugin` (`plugin`),
  CONSTRAINT `interface_plugin` FOREIGN KEY (`plugin`) REFERENCES `plugin` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录 plugin 的操作:apply, destroy, query...';

CREATE TABLE `parameter` (
  `id` varchar(32) NOT NULL,
  `name` varchar(64) NOT NULL COMMENT '名称',
  `type` varchar(32) NOT NULL COMMENT '类型(list, 非 list)',
  `multiple` varchar(32) NOT NULL COMMENT 'type 字段中元素的类型(string, number, object...)',
  `interface` varchar(32) NOT NULL,
  `template` varchar(32) DEFAULT NULL,
  `datatype` varchar(32) DEFAULT NULL,
  `object_name` varchar(32) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  `source` varchar(32) DEFAULT 'custom' COMMENT '属性来源',
  `nullable` varchar(4) DEFAULT 'N',
  `sensitive` varchar(4) DEFAULT 'N',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_interface_type_name` (`interface`,`type`,`name`),
  KEY `parameter_interface` (`interface`),
  KEY `parameter_object_name_idx` (`object_name`),
  KEY `parameter_template` (`template`),
  CONSTRAINT `parameter_interface` FOREIGN KEY (`interface`) REFERENCES `interface` (`id`),
  CONSTRAINT `parameter_object_name` FOREIGN KEY (`object_name`) REFERENCES `parameter` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `parameter_template` FOREIGN KEY (`template`) REFERENCES `template` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录抽象的配置参数:image_id, instance_type, instance_name...';

CREATE TABLE `plugin` (
  `id` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL COMMENT '名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  PRIMARY KEY (`id`),
  UNIQUE KEY `plugin_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录抽象的资源:instance, vpc, subnet, route_table, security_group...';

CREATE TABLE `provider` (
  `id` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL COMMENT '名称',
  `version` varchar(64) NOT NULL COMMENT 'provider 版本号',
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  `secret_id_attr_name` varchar(32) DEFAULT NULL,
  `secret_key_attr_name` varchar(32) DEFAULT NULL,
  `region_attr_name` varchar(32) DEFAULT NULL,
  `Initialized` varchar(4) DEFAULT NULL,
  `name_space` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `provider_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录云厂商类别:tencentcloud, alicloud, aws...';

CREATE TABLE `provider_info` (
  `id` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL COMMENT '名称',
  `provider` varchar(32) NOT NULL,
  `secret_id` varchar(512) NOT NULL COMMENT '密钥 id',
  `secret_key` varchar(512) NOT NULL COMMENT '密钥 key',
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  `import_prefix` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  KEY `provider_info_provider` (`provider`),
  CONSTRAINT `provider_info_provider` FOREIGN KEY (`provider`) REFERENCES `provider` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录云厂商信息';

CREATE TABLE `provider_template_value` (
  `id` varchar(32) NOT NULL,
  `value` varchar(64) NOT NULL COMMENT '配置值',
  `provider` varchar(32) NOT NULL,
  `template_value` varchar(32) NOT NULL,
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_provider_template_value_value` (`provider`,`template_value`,`value`),
  KEY `provider_template_value_template_value` (`template_value`),
  KEY `provider_template_value_provider` (`provider`),
  CONSTRAINT `provider_template_value_provider` FOREIGN KEY (`provider`) REFERENCES `provider` (`id`),
  CONSTRAINT `provider_template_value_template_value` FOREIGN KEY (`template_value`) REFERENCES `template_value` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录云厂商的配置值:S2.SMALL2...';

CREATE TABLE `resource_data` (
  `id` varchar(32) NOT NULL,
  `resource` varchar(32) NOT NULL,
  `resource_id` varchar(128) NOT NULL COMMENT 'wecube 资源的 id',
  `resource_asset_id` varchar(1024) NOT NULL COMMENT '云上资源的 id',
  `tf_file` text COMMENT 'tf file 内容',
  `tf_state_file` text COMMENT 'tf state file 内容',
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  `region_id` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `resource_data_source_idx` (`resource`),
  CONSTRAINT `resource_data_source` FOREIGN KEY (`resource`) REFERENCES `source` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录 Terraform action 资源操作后的 data';

CREATE TABLE `resource_data_debug` (
  `id` varchar(32) NOT NULL,
  `resource_id` varchar(128) DEFAULT NULL,
  `resource_asset_id` varchar(1024) DEFAULT NULL,
  `tf_file` text,
  `tf_state_file` text,
  `resource` varchar(32) NOT NULL,
  `region_id` varchar(128) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `create_user` varchar(64) DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `update_user` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `source` (
  `id` varchar(32) NOT NULL,
  `interface` varchar(32) NOT NULL,
  `provider` varchar(32) NOT NULL,
  `name` varchar(64) NOT NULL COMMENT '名称',
  `asset_id_attribute` varchar(32) DEFAULT NULL,
  `terraform_used` varchar(32) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  `import_prefix` varchar(256) DEFAULT '',
  `execution_seq_no` int(4) DEFAULT '1',
  `import_support` varchar(4) DEFAULT 'Y',
  `source_type` varchar(64) DEFAULT NULL,
  `remark` varchar(128) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_provider_interface_name` (`provider`,`interface`,`name`),
  KEY `source_interface_idx` (`interface`),
  KEY `source_provider` (`provider`),
  CONSTRAINT `source_interface` FOREIGN KEY (`interface`) REFERENCES `interface` (`id`),
  CONSTRAINT `source_provider` FOREIGN KEY (`provider`) REFERENCES `provider` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录 Terraform data /resource后面那个type名字(如 resource "alicloud_instance" "instance" {}中的 alicloud_instance, data "alicloud_zones" "default" {}中的 alicloud_zones)';

CREATE TABLE `sys_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `log_cat` varchar(64) NOT NULL DEFAULT '' COMMENT ' 日志归类',
  `operator` varchar(20) NOT NULL DEFAULT '' COMMENT '操作用户',
  `operation` varchar(64) NOT NULL DEFAULT '' COMMENT '操作行为',
  `content` longtext COMMENT '具体内容',
  `request_url` varchar(512) DEFAULT '' COMMENT '请求url',
  `client_host` varchar(20) DEFAULT NULL COMMENT '请求客户端IP',
  `created_date` varchar(32) NOT NULL COMMENT '日志时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='记录操作的日志信息';

CREATE TABLE `template` (
  `id` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL COMMENT '名称',
  `description` varchar(64) DEFAULT '' COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录抽象的配置名: 如 instance_type,此表用作抽象,以免出现多个重复的 template_value';

CREATE TABLE `template_value` (
  `id` varchar(32) NOT NULL,
  `value` varchar(64) NOT NULL COMMENT '配置值',
  `template` varchar(32) NOT NULL,
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT '' COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT '' COMMENT '更新者',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_template_value` (`template`,`value`),
  KEY `template_value_template` (`template`),
  CONSTRAINT `template_value_template` FOREIGN KEY (`template`) REFERENCES `template` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录抽象的配置值:1C2G...';

CREATE TABLE `tf_argument` (
  `id` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL COMMENT '名称',
  `source` varchar(32) NOT NULL,
  `parameter` varchar(32) DEFAULT NULL,
  `default_value` varchar(128) DEFAULT NULL COMMENT '默认值',
  `is_null` varchar(4) DEFAULT NULL COMMENT '是否为空',
  `type` varchar(32) NOT NULL COMMENT '数据类型',
  `object_name` varchar(32) DEFAULT NULL,
  `is_multi` varchar(4) NOT NULL COMMENT '是否支持多个值',
  `convert_way` varchar(32) DEFAULT NULL COMMENT '转换方式',
  `relative_source` varchar(32) DEFAULT NULL,
  `relative_tfstate_attribute` varchar(32) DEFAULT NULL COMMENT '关联 attr，用于 attr 转换',
  `relative_parameter` varchar(32) DEFAULT NULL COMMENT '关联参数，用于上下文 context 转换',
  `relative_parameter_value` varchar(128) DEFAULT NULL COMMENT '关联值，用于上下文 context 转换',
  `function_define` text,
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT NULL COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT NULL COMMENT '更新者',
  `key_argument` varchar(4) DEFAULT 'N',
  PRIMARY KEY (`id`),
  KEY `tf_argument_source` (`source`),
  KEY `tf_argument_relative_parameter_idx` (`relative_parameter`),
  KEY `tf_argument_relative_source` (`relative_source`),
  KEY `tf_argument_parameter` (`parameter`),
  KEY `tf_argument_object_name_idx` (`object_name`),
  KEY `tf_argument_relative_tfstate_attribute_idx` (`relative_tfstate_attribute`),
  CONSTRAINT `tf_argument_object_name` FOREIGN KEY (`object_name`) REFERENCES `tf_argument` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tf_argument_parameter` FOREIGN KEY (`parameter`) REFERENCES `parameter` (`id`),
  CONSTRAINT `tf_argument_relative_parameter` FOREIGN KEY (`relative_parameter`) REFERENCES `parameter` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tf_argument_relative_source` FOREIGN KEY (`relative_source`) REFERENCES `source` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tf_argument_relative_tfstate_attribute` FOREIGN KEY (`relative_tfstate_attribute`) REFERENCES `tfstate_attribute` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tf_argument_source` FOREIGN KEY (`source`) REFERENCES `source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录 Terraform action 输入的参数字段';

CREATE TABLE `tfstate_attribute` (
  `id` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL COMMENT '名称',
  `source` varchar(32) NOT NULL,
  `parameter` varchar(32) DEFAULT NULL,
  `default_value` varchar(64) DEFAULT '' COMMENT '默认值',
  `is_null` varchar(4) DEFAULT NULL COMMENT '是否为空',
  `type` varchar(32) NOT NULL COMMENT '数据类型',
  `object_name` varchar(32) DEFAULT NULL,
  `is_multi` varchar(4) NOT NULL COMMENT '是否支持多个值',
  `convert_way` varchar(32) DEFAULT NULL COMMENT '转换方式',
  `relative_source` varchar(32) DEFAULT NULL,
  `relative_tfstate_attribute` varchar(32) DEFAULT NULL,
  `relative_parameter` varchar(32) DEFAULT NULL COMMENT '关联参数，用于上下文 context 转换',
  `relative_parameter_value` varchar(128) DEFAULT NULL COMMENT '关联值，用于上下文 context 转换',
  `function_define` text,
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `create_user` varchar(32) DEFAULT NULL COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `update_user` varchar(32) DEFAULT NULL COMMENT '更新者',
  PRIMARY KEY (`id`),
  KEY `tfstate_attribute_relative_source_idx` (`relative_source`),
  KEY `tfstate_attribute_source` (`source`),
  KEY `tfstate_attribute_relative_parameter_idx` (`relative_parameter`),
  KEY `tfstate_attribute_source_idx` (`object_name`),
  KEY `tfstate_attribute_parameter` (`parameter`),
  CONSTRAINT `tfstate_attribute_object_name` FOREIGN KEY (`object_name`) REFERENCES `tfstate_attribute` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tfstate_attribute_parameter` FOREIGN KEY (`parameter`) REFERENCES `parameter` (`id`),
  CONSTRAINT `tfstate_attribute_relative_parameter` FOREIGN KEY (`relative_parameter`) REFERENCES `parameter` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tfstate_attribute_relative_source` FOREIGN KEY (`relative_source`) REFERENCES `source` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tfstate_attribute_source` FOREIGN KEY (`source`) REFERENCES `source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='记录 Terraform action 输出的参数字段';


SET FOREIGN_KEY_CHECKS=1;