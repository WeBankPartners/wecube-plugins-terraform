
insert  into `config`(`id`,`provider`,`resource`,`property`,`value_config`,`is_locked`,`created_time`,`updated_time`,`deleted_time`,`enabled`,`is_deleted`) values 

('20d0c747c96040afbeab159a2f5e696c','tencentcloud','subnet','cidr','{\"subnet_20\": \"10.0.20.0/24\", \"subnet_1\": \"10.0.1.0/24\"}',0,'2021-01-12 19:43:17','2021-01-12 19:43:17',NULL,1,0),

('29207d072f0f4edb81540cf947b6b1cf','tencentcloud','zone','zone','{\"guangzhou4\": \"ap-guangzhou-4\", \"guangzhou3\": \"ap-guangzhou-3\"}',0,'2021-01-12 19:45:23','2021-01-12 19:45:23',NULL,1,0),

('9e70671e06f345d2872c339bc42a71c4','tencentcloud','region','region','{\"guangzhou\": \"ap-guangzhou\"}',0,'2021-01-13 10:19:34','2021-01-13 10:19:34',NULL,1,0),

('f5be05e69af540fb96440e0a403027db','tencentcloud','vpc','cidr','{\"vpc_1\": \"10.1.0.0/16\", \"vpc_0\": \"10.0.0.0/16\"}',0,'2021-01-13 10:05:52','2021-01-13 10:05:52',NULL,1,0);

/*Data for the table `connect_network` */

/*Data for the table `connect_network_attach` */

/*Data for the table `disk` */

/*Data for the table `disk_attach` */

/*Data for the table `eip` */

/*Data for the table `eip_association` */

/*Data for the table `instance` */

/*Data for the table `instance_type` */

/*Data for the table `kvstore` */

/*Data for the table `load_balance` */

/*Data for the table `load_balance_listener` */

/*Data for the table `nat_gateway` */

/*Data for the table `nosql` */

/*Data for the table `rds_db` */

/*Data for the table `resource` */

insert  into `resource`(`id`,`provider`,`property`,`resource_name`,`extend_info`,`resource_property`,`output_property`,`is_locked`,`created_time`,`updated_time`,`deleted_time`,`enabled`,`is_deleted`) values 

('1276c410c524401c9e37c5cab2add904','tencentcloud','tencentcloud_route_table','route_table','{}','{\"vpc_id\": {\"convert\": \"vpc_id\", \"allow_null\": 0, \"type\": \"string\"}, \"name\": {\"convert\": \"name\", \"allow_null\": 0, \"type\": \"string\"}}','{}',0,'2021-01-13 18:20:01','2021-01-13 18:20:01',NULL,1,0),

('161ba756498c4514893d7b37c83d3daf','tencentcloud','tencentcloud_security_group','security_group','{\"description\": \"from terraform\", \"tags\": {\"type\": \"json\"}}','{\"vpc_id\": \"-\", \"name\": {\"convert\": \"name\", \"allow_null\": 0, \"type\": \"string\"}}','{}',0,'2021-01-14 10:01:20','2021-01-14 10:01:20',NULL,1,0),

('2440b0e9abaf4ebca78461b1b64324ca','tencentcloud','tencentcloud_route_table_entry','route_entry','{\"description\": \"from terraform\"}','{\"next_hub\": {\"convert\": \"next_hub\", \"allow_null\": 0, \"type\": \"string\"}, \"name\": \"-\", \"destination\": {\"convert\": \"destination_cidr_block\", \"allow_null\": 0, \"type\": \"string\"}, \"next_type\": {\"convert\": \"next_type\", \"allow_null\": 0, \"type\": \"string\"}, \"route_table_id\": {\"convert\": \"route_table_id\", \"allow_null\": 0, \"type\": \"string\"}, \"vpc_id\": \"-\"}','{}',0,'2021-01-13 20:04:12','2021-01-13 20:04:12',NULL,1,0),

('2aa8cd54f561493a981eae5fbcd0661f','tencentcloud','tencentcloud_security_group_rule','security_group_rule','{\"description\": \"from terraform\"}','{\"cidr_ip\": {\"convert\": \"cidr_ip\", \"allow_null\": 0, \"type\": \"string\"}, \"description\": {\"convert\": \"description\", \"allow_null\": 1, \"type\": \"string\"}, \"security_group_id\": {\"convert\": \"security_group_id\", \"allow_null\": 0, \"type\": \"string\"}, \"policy\": {\"convert\": \"policy\", \"allow_null\": 0, \"type\": \"string\"}, \"vpc_id\": \"-\", \"type\": {\"convert\": \"type\", \"allow_null\": 0, \"type\": \"string\"}, \"ports\": {\"convert\": \"port_range\", \"allow_null\": 0, \"type\": \"string\"}, \"ip_protocol\": {\"convert\": \"ip_protocol\", \"allow_null\": 0, \"type\": \"string\"}}','{}',0,'2021-01-14 10:48:44','2021-01-14 10:48:44',NULL,1,0),

('39a526c0023e44e8bbbb736c1cd6487c','tencentcloud','tencentcloud_subnet','subnet','{\"is_multicast\": false}','{\"vpc_id\": {\"convert\": \"vpc_id\", \"allow_null\": 0, \"type\": \"string\"}, \"cidr\": {\"convert\": \"cidr_block\", \"allow_null\": 0, \"type\": \"string\"}, \"name\": {\"convert\": \"name\", \"allow_null\": 0, \"type\": \"string\"}, \"zone\": {\"convert\": \"availability_zone\", \"allow_null\": 0, \"type\": \"string\"}}','{}',0,'2021-01-12 19:11:46','2021-01-12 19:11:46',NULL,1,0),

('8fa4f45ed6a14b2085cc59eb64127319','tencentcloud','tencentcloud_vpc','vpc','{\"is_multicast\": false,\"tags\":{\"type\": \"json\"}}','{\"cidr\": {\"convert\": \"cidr_block\", \"allow_null\": 0, \"type\": \"string\"}, \"name\": {\"convert\": \"name\", \"allow_null\": 0, \"type\": \"string\"}}','{}',0,'2021-01-12 17:37:50','2021-01-12 17:37:50',NULL,1,0);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
