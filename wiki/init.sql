create table plugin
(
    id varchar(32) not null
        primary key,
    name varchar(32) not null comment '名称',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint plugin_name
        unique (name)
)
    comment '记录抽象的资源:instance, vpc, subnet, route_table, security_group...';

create table interface
(
    id varchar(32) not null
        primary key,
    name varchar(32) not null comment '操作名称',
    plugin varchar(32) not null,
    description varchar(64) default '' null comment '描述',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment 'update_user',
    constraint interface_plugin
        foreign key (plugin) references plugin (name)
)
    comment '记录 plugin 的操作:apply, destroy, query...';

create table provider
(
    id varchar(32) not null
        primary key,
    name varchar(32) not null comment '名称',
    version varchar(64) not null comment 'provider 版本号',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint provider_name
        unique (name)
)
    comment '记录云厂商类别:tencentcloud, alicloud, aws...';

create table provider_info
(
    id varchar(32) not null
        primary key,
    name varchar(32) not null comment '名称',
    provider varchar(32) not null,
    secret_id varchar(512) not null comment '密钥 id',
    secret_key varchar(512) not null comment '密钥 key',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint provider_info_provider
        foreign key (provider) references provider (id)
)
    comment '记录云厂商信息';

create table source
(
    id varchar(32) not null
        primary key,
    name varchar(64) not null comment '名称',
    plugin varchar(32) not null,
    provider varchar(32) not null,
    resource_asset_id_attribute varchar(32) not null comment '资源执行 action 后结果中的代表云上资源 resource asset id 的属性名(通常为 "id"),用于 resource_data 表中 resource_asset_id 值的获取',
    action varchar(32) not null comment '操作的名称:apply, destroy, query...',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint source_plugin
        foreign key (plugin) references plugin (name),
    constraint source_provider
        foreign key (provider) references provider (name)
)
    comment '记录 Terraform data /resource后面那个type名字(如 resource "alicloud_instance" "instance" {}中的 alicloud_instance, data "alicloud_zones" "default" {}中的 alicloud_zones)';

create table resource_data
(
    id varchar(32) not null
        primary key,
    source varchar(32) not null,
    resource_id varchar(128) not null comment 'wecube 资源的 id',
    resource_asset_id varchar(128) not null comment '云上资源的 id',
    tf_file text null comment 'tf file 内容',
    tf_state_file text null comment 'tf state file 内容',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint resource_data_source
        foreign key (source) references source (id)
)
    comment '记录 Terraform action 资源操作后的 data';

create table sys_log
(
    id int auto_increment comment '自增主键'
        primary key,
    log_cat varchar(64) default '' not null comment ' 日志归类',
    operator varchar(20) default '' not null comment '操作用户',
    operation varchar(64) default '' not null comment '操作行为',
    content longtext null comment '具体内容',
    request_url varchar(512) default '' null comment '请求url',
    client_host varchar(20) null comment '请求客户端IP',
    created_date varchar(32) not null comment '日志时间',
    data_ci_type varchar(32) null comment '数据所属ci',
    data_guid varchar(64) null comment '数据guid',
    data_key_name varchar(32) null comment '数据名称'
)
    comment '记录操作的日志信息';

create table template
(
    id varchar(32) not null
        primary key,
    name varchar(32) not null comment '名称',
    description varchar(64) default '' null comment '描述',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint template_name
        unique (name)
)
    comment '记录抽象的配置名: 如 instance_type,此表用作抽象,以免出现多个重复的 template_value';

create table parameter
(
    id varchar(128) not null
        primary key,
    name varchar(64) not null comment '名称',
    type varchar(32) not null comment '类型(list, 非 list)',
    multiple varchar(32) not null comment 'type 字段中元素的类型(string, number, object...)',
    interface varchar(32) not null,
    template varchar(32) null,
    datatype varchar(32) null,
    object_name varchar(128) null,
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint parameter_interface
        foreign key (interface) references interface (id),
    constraint parameter_object_name
        foreign key (object_name) references parameter (id),
    constraint parameter_template
        foreign key (template) references template (name)
)
    comment '记录抽象的配置参数:image_id, instance_type, instance_name...';

create index parameter_object_name_idx
	on parameter (object_name);

create table template_value
(
    id varchar(128) not null
        primary key,
    value varchar(64) not null comment '配置值',
    template varchar(64) not null,
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint template_value_template
        foreign key (template) references template (name)
)
    comment '记录抽象的配置值:1C2G...';

create table provider_template_value
(
    id varchar(128) not null
        primary key,
    value varchar(64) not null comment '配置值',
    provider varchar(32) not null,
    template_value varchar(128) not null,
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint provider_template_value_provider
        foreign key (provider) references provider (name),
    constraint provider_template_value_template_value
        foreign key (template_value) references template_value (id)
)
    comment '记录云厂商的配置值:S2.SMALL2...';

create table tfstate_attribute
(
    id varchar(32) not null
        primary key,
    name varchar(32) not null comment '名称',
    source varchar(32) not null,
    parameter varchar(128) not null,
    default_value varchar(64) default '' null comment '默认值',
    is_null tinyint(1) null comment '是否为空',
    type varchar(32) default '' null comment '数据类型',
    is_multi tinyint(1) not null comment '是否支持多个值',
    convert_way varchar(32) default '' null comment '转换方式',
    relative_parameter varchar(32) default '' null comment '关联参数，用于上下文 context 转换',
    relative_value text null comment '关联值，用于上下文 context 转换',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint tfstate_attribute_parameter
        foreign key (parameter) references parameter (id),
    constraint tfstate_attribute_source
        foreign key (source) references source (id)
)
    comment '记录 Terraform action 输出的参数字段';

create table tf_argument
(
    id varchar(32) not null
        primary key,
    name varchar(32) not null comment '名称',
    source varchar(32) not null,
    parameter varchar(128) not null,
    tfstate_attribute varchar(32) null comment '关联 attr，用于 attr 转换',
    default_value varchar(64) default '' null comment '默认值',
    is_null tinyint(1) null comment '是否为空',
    type varchar(32) null comment '数据类型',
    is_multi tinyint(1) not null comment '是否支持多个值',
    convert_way varchar(32) default '' null comment '转换方式',
    relative_parameter varchar(32) default '' null comment '关联参数，用于上下文 context 转换',
    relative_value text null comment '关联值，用于上下文 context 转换',
    create_time datetime null comment '创建日期',
    create_user varchar(32) default '' null comment '创建者',
    update_time datetime null comment '更新日期',
    update_user varchar(32) default '' null comment '更新者',
    constraint tf_argument_parameter
        foreign key (parameter) references parameter (id),
    constraint tf_argument_source
        foreign key (source) references source (id),
    constraint tf_argument_tfstate_attribute
        foreign key (tfstate_attribute) references tfstate_attribute (id)
)
    comment '记录 Terraform action 输入的参数字段';

