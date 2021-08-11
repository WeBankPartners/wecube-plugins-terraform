### 1. plugin -- 记录抽象的资源: instance, vpc, subnet, route_table, security_group...

​    (1) create (支持批量)

​    	POST: http://127.0.0.1:8999/weterraform/api/v1/plugins

```json
[
	{
		"name": "instance"
	},
	{
		"name": "vpc"
	}
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/plugins

```json
{
    "statusCode": "OK",
    "data": [
        {
            "id": "60dd22ee45f5ee1e415b9f07f320739a",
            "name": "vpc",
            "createTime": "2021-07-01 10:05:34",
            "createUser": "SUPER_ADMIN",
            "updateTime": "2021-07-01 10:05:34",
            "updateUser": ""
        },
        {
            "id": "60dd22ee6c9048743226d56ec20f00cd",
            "name": "instance",
            "createTime": "2021-07-01 10:05:34",
            "createUser": "SUPER_ADMIN",
            "updateTime": "2021-07-01 10:05:34",
            "updateUser": ""
        }
    ]
}
```

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/plugin

```json
[
        {
            "id": "60dd22ee6c9048743226d56ec20f00cd",
            "name": "instance",
            "createTime": "2021-07-01 10:05:34",
            "createUser": "SUPER_ADMIN",
            "updateTime": "2021-07-01 10:05:34",
            "updateUser": ""
        },
        {
            "id": "60dd22ee45f5ee1e415b9f07f320739a",
            "name": "vpc",
            "createTime": "2021-07-01 10:05:34",
            "createUser": "SUPER_ADMIN",
            "updateTime": "2021-07-01 10:05:34",
            "updateUser": ""
        }
	]
```

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/plugin?ids=id1,id2

### 2. interface -- 记录 plugin 的操作: apply, destroy, query...

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/interfaces

```json
[
    {
        "name": "apply",
        "plugin": "instance",
        "description": "test"
    },
    {
        "name": "destroy",
        "plugin": "instance",
        "description": "test"
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/interfaces

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/interface

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/interface?ids=id1,id2

### 3. template -- 记录抽象的配置名: 如 instance_type,此表用作抽象,以免出现多个重复的 template_value

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/templates

```json
[
    {
        "name": "instance_type",
        "description": "test"
    },
    {
        "name": "image",
        "description": "test"
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/templates

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/template

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/template?ids=id1,id2

### 4. template_value -- 记录抽象的配置值:1C2G...

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/template_values

```json
[
    {
        "value": "1C2G",
        "template": "instance_type"
    },
    {
        "value": "CentOS7.5",
        "template": "image"
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/template_values

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/template_value

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/template_values?ids=id1,id2

### 5. parameter -- 记录抽象的配置参数:image_id, instance_type, instance_name...

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/parameters

```json
[
    {
      	"name": "x",
      	"type": "x",
      	"referenceType": "x",
        "interface": "x",
        "template": "x"
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/.parameters

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/parameter

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/parameter?ids=id1,id2

### 6. provider -- 记录云厂商类别:tencentcloud, alicloud, aws...

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/providers

```json
[
    {
      	"name": "x"
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/providers

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/provider

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/provider?ids=id1,id2

### 7. provider_info -- 记录云厂商信息

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/provider_infos

```json
[
    {
      	"name": "x",
      	"provider": "x",
      	"secretId": "x",
        "secretKey": "x",
        "version": "x"
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/provider_infos

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/provider_info

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/provider_info?ids=id1,id2

### 8. provider_template_value -- 记录云厂商的配置值:S2.SMALL2...

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/provider_template_values

```json
[
    {
      	"value": "x",
      	"provider": "x",
      	"templateValue": "x"
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/provider_template_values

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/provider_template_value

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/provider_template_value?ids=id1,id2

### 9. source -- 记录 Terraform data /resource后面那个type名字(如 resource "alicloud_instance" "instance" {}中的 alicloud_instance, data "alicloud_zones" "default" {}中的 alicloud_zones)

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/sources

```json
[
    {
      	"name": "x",
      	"plugin": "x",
      	"provider": "x",
        "resourceAssetIdAttribute": "x",
        "action": "x"
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/sources

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/source

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/source?ids=id1,id2

### 10. tf_argument -- 记录 Terraform action 输入的参数字段

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/tf_arguments

```json
[
    {
      	"source": "x",
      	"parameter": "x",
      	"tfstateAttribute": "x",
        "defaultValue": "x",
        "isNull": "x",
      	"type": "x",
      	"convertType": "x",
      	"convertWay": "x",
        "convertAttribute": "x",
        "value": "x",
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/tf_arguments

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/tf_argument

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/tf_argument?ids=id1,id2

### 11. tfstate_attribute -- 记录 Terraform action 输出的参数字段

​	(1) create (支持批量)

​		POST: http://127.0.0.1:8999/weterraform/api/v1/tfstate_attributes

```json
[
    {
      	"source": "x",
      	"parameter": "x",
        "defaultValue": "x",
        "isNull": "x",
      	"type": "x",
      	"convertType": "x",
      	"convertWay": "x",
        "convertAttribute": "x",
        "value": "x",
    }
]
```

​	(2) list 

​		GET: http://127.0.0.1:8999/weterraform/api/v1/tfstate_attributes

​	(3) update (全量字段更新，支持批量)

​		PUT: http://127.0.0.1:8999/weterraform/api/v1/tfstate_attribute

​	(4) delete (支持批量, ids 的多个值以 "," 分隔)

​		DELETE: http://127.0.0.1:8999/weterraform/api/v1/tfstate_attribute?ids=id1,id2

