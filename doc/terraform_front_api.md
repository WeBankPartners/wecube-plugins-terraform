#### provider (云厂商)

##### list:

url: /terraform/v1/configer/provider

参数： "id", "name", "region"

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":2,
        "data":[
            {
                "display_name":"腾讯云", 
                "name":"tencentcloud",
                "zone":null,
                "deleted_time":null,
                "region":null,
                "enabled":1,
                "secret_id":"xxxx",
                "updated_time":"2021-01-13 11:15:56",
                "provider_property":{
                    "region":"region",
                    "secret_key":"secret_key",
                    "secret_id":"secret_id"
                },
                "created_time":"2021-01-13 11:15:56",
                "extend_info":{

                },
                "plugin_source":null,
                "is_init":1,
                "is_deleted":0,
                "secret_key":"xxx",
                "id":"73aa4d40248849c48cb0fcde88d1d1d1"
            }
        ]
    }
}
```



##### create:

url: /terraform/v1/configer/provider

字段：



输入：


```
name         string  必填
display_name  string  选填
secret_id    string  必填
secret_key    string  必填
region        string  隐藏
zone          string  隐藏
extend_info    json
provider_property  json


示例：
{
"display_name": "腾讯云",
"name": "tencentcloud02",
"zone": "",
"region": "",
"secret_id": "31313",
"secret_key": "3131313",
"extend_info": {},
"provider_property": {
	"secret_id": "secret_id",
	"secret_key":"secret_key",
	"region": "region"
}
}

```



输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":{
                "id":"76c8286bed1e444db7bee8ef5129ede5"
            }

    }
}
```



##### 详情:

url: /terraform/v1/configer/provider/{id}

参数： "id", 

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "display_name":"腾讯云",
        "name":"tencentcloud02",
        "zone":null,
        "deleted_time":null,
        "region":null,
        "enabled":1,
        "secret_id":"34242",
        "updated_time":"2021-01-21 10:37:10",
        "provider_property":{
            "region":"region",
            "secret_key":"secret_key",
            "secret_id":"secret_id"
        },
        "created_time":"2021-01-21 10:37:10",
        "extend_info":{

        },
        "plugin_source":null,
        "is_init":1,
        "is_deleted":0,
        "secret_key":"xxxx",
        "id":"c73b8db43df24a2899da00d9dc7afbb9"
    }
}
```


##### update:

url: /terraform/v1/configer/provider/{id}

参数： 
"zone",  
"secret_id",
"secret_key",  
"region", 
"enabled",
"extend_info",
"provider_property"

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":[
            {
                "is_deleted":0,
                "name":"tencentcloud",
                "zone":null,
                "deleted_time":null,
                "region":"ap-guangzhou",
                "enabled":1,
                "secret_id":"dasdad",
                "updated_time":"2020-12-15 16:12:30",
                "provider_property":"{}",
                "created_time":"2020-12-15 16:12:30",
                "extend_info":"{}",
                "plugin_source":null,
                "is_init":1,
                "secret_key":"ddada",
                "id":"76c8286bed1e444db7bee8ef5129ede5"
            }
        ]
    }
}
```


##### delete:

url: /terraform/v1/configer/provider/{id}

参数： id


输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "data":[
            {
                "id":"76c8286bed1e444db7bee8ef5129ede5"
            }
        ]
    }
}
```

-----

----
#### resource(资源/云产品）

##### list:

url: /terraform/v1/configer/resource

参数："id", "provider", "resource_type", "resource_name"

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":6,
        "data":[
            {
                "resource_name":"vpc",
                "is_deleted":0,
                "resource_property":{
                    "cidr":{
                        "convert":"cidr_block",
                        "allow_null":0,
                        "type":"string"
                    },
                    "name":{
                        "convert":"name",
                        "allow_null":0,
                        "type":"string"
                    }
                },
                "is_locked":0,
                "deleted_time":null,
                "enabled":1,
                "resource_output":{
                    "resource_id":"id"
                },
                "updated_time":"2021-01-16 12:35:44",
                "extend_info":{
                    "is_multicast":false,
                    "tags":{
                        "type":"json"
                    }
                },
                "provider":"tencentcloud",
                "created_time":"2021-01-16 12:35:44",
                "resource_type":"tencentcloud_vpc",
                "id":"b0126dffc4114d9495b3d22ce8ca99ec"
            }
        ]
    }
}
```



##### create:

url: /terraform/v1/configer/resource

字段：



输入：


```
"provider"     云厂商   string  必填 
"resource_type"     类别： 如vpc   string  必填

<resource配置>
"resource_name"   资源名称 如tencent_vpc  string  必填
"extend_info"      资源其他属性字段  json
"resource_property"  资源转换的属性字段  json   如： cider需要转换为cider_block  则为｛“cider”: "cider_block"｝
"resource_output"  输出属性： 例如｛“resource_id”: "id"｝或｛“resource_id”: {"type": "string", "value": "id"}｝

<data source配置>
data_source_name  查询data source资源名称 string 选填
data_source_argument  data source输出资源字段 如: instance.configs   string 选填
data_source   data source查询字段转换    string  选填
data_source_output  data source资源输出转换字段  string 选填
```



输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":{
                "id":"76c8286bed1e444db7bee8ef5129ede5"
            }

    }
}
```



##### 详情:

url: /terraform/v1/configer/resource/{id}

参数： "id", 

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "data_source_name":"tencentcloud_vpc_instances",
        "resource_name":"tencentcloud_vpc",
        "is_deleted":0,
        "resource_property":{
            "cidr":{
                "convert":"cidr_block",
                "allow_null":0,
                "type":"string"
            },
            "name":{
                "convert":"name",
                "allow_null":0,
                "type":"string"
            }
        },
        "is_locked":0,
        "deleted_time":null,
        "resource_output":{
            "resource_id":{
                "type":"string",
                "value":"id"
            }
        },
        "enabled":1,
        "updated_time":"2021-03-25 15:39:17",
        "data_source":{
            "resource_id":"vpc_id"
        },
        "extend_info":{
            "tags":{
                "type":"json"
            },
            "is_multicast":false
        },
        "data_source_output":{
            "cidr":{
                "convert":"cidr_block",
                "allow_null":0,
                "type":"string"
            },
            "name":{
                "convert":"name",
                "allow_null":0,
                "type":"string",
                "resource_id":"vpc_id"
            }
        },
        "data_source_argument":"instance_list",
        "provider":"tencentcloud",
        "created_time":"2021-03-25 15:39:17",
        "id":"074354e0795a4e859cff2c6e7471e6bf",
        "resource_type":"vpc"
    }
}
```


##### update:

url: /terraform/v1/configer/resource/{id}

参数： 

```
"provider", 
"resource_type",
"extend_info"
"resource_name", 
"resource_property"
"resource_output"
data_source_name  
data_source_argument  
data_source  
data_source_output 
```
例如:
```
{
"data_source_name": "tencentcloud_vpc_subnets",
"data_source_argument": "instance_list",
"data_source": {"resource_id": "subnet_id"},
"data_source_output": {}
}
```

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":[
            {
        "resource_name":"vpc",
        "is_deleted":0,
        "resource_property":{
            "cidr":{
                "convert":"cidr_block",
                "allow_null":0,
                "type":"string"
            },
            "name":{
                "convert":"name",
                "allow_null":0,
                "type":"string"
            }
        },
        "is_locked":0,
        "deleted_time":null,
        "enabled":1,
        "resource_output":{
            "resource_id":"id"
        },
        "updated_time":"2021-01-16 12:35:44",
        "extend_info":{
            "is_multicast":false,
            "tags":{
                "type":"json"
            }
        },
        "provider":"tencentcloud",
        "created_time":"2021-01-16 12:35:44",
        "resource_type":"tencentcloud_vpc",
        "id":"b0126dffc4114d9495b3d22ce8ca99ec"
            }
        ]
    }
}
```


##### delete:

url: /terraform/v1/configer/resource/{id}

参数： id


输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "data":[
            {
                "id":"76c8286bed1e444db7bee8ef5129ede5"
            }
        ]
    }
}
```

----

-----

#### keyconfig（云资源的属性）

##### list:

url: /terraform/v1/configer/keyconfig

参数："id", "resource", "provider", "resource_type", "enabled"

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":[
            {
                "resource":"vpc",
                "is_locked":0,
                "deleted_time":null,
                "enabled":1,
                "updated_time":null,
                "value_config":"{
"cider":"cidr_block"
}",
                "provider":"tencentcloud",
                "created_time":null,
                "is_deleted":0,
                "resource_type":null,
                "id":"62e1376d-eb96-477b-927a-ce27d0ea6849"
            }
        ]
    }
}
```



##### create:

url: /terraform/v1/configer/keyconfig

字段：



输入：


```
"provider",   云厂商  string  必填
"resource",   资源名称  string  必填  如vpc
"resource_type",   资源属性  string 必填 如cider
"value_config"  资源属性值转换配置  json   如： “muliticate” 转换为“muliticate_info” 则配置为： ｛“muliticate”： “muliticate_info”｝
```



输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":{
                "id":"76c8286bed1e444db7bee8ef5129ede5"
            }

    }
}
```



##### 详情:

url: /terraform/v1/configer/keyconfig/{id}

参数： "id", 

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
                "resource":"vpc",
                "is_locked":0,
                "deleted_time":null,
                "enabled":1,
                "updated_time":null,
                "value_config":"{
"cider":"cidr_block"
}",
                "provider":"tencentcloud",
                "created_time":null,
                "is_deleted":0,
                "resource_type":null,
                "id":"62e1376d-eb96-477b-927a-ce27d0ea6849"
        ]
    }
}
```


##### update:

url: /terraform/v1/configer/keyconfig/{id}

参数： 

```
"provider",   
"resource",   
"resource_type",   
"value_config" 
```



输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":[
            {
                "resource":"vpc",
                "is_locked":0,
                "deleted_time":null,
                "enabled":1,
                "updated_time":null,
                "value_config":"{
"cider":"cidr_block"
}",
                "provider":"tencentcloud",
                "created_time":null,
                "is_deleted":0,
                "resource_type":null,
                "id":"62e1376d-eb96-477b-927a-ce27d0ea6849"
            }
        ]
    }
}
```


##### delete:

url: /terraform/v1/configer/keyconfig/{id}

参数： id


输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "data":[
            {
                "id":"76c8286bed1e444db7bee8ef5129ede5"
            }
        ]
    }
}
```

----

-----

#### instance type (实例规格)

包含： 虚拟机， RDS, NOSQL, KV STORAGE 等涉及规格选择的产品



##### list:

url: /terraform/v1/vm/instance_type

参数：

```
"id", "provider", "origin_name", "cpu", "memory", "provider_id", "name", "enabled"
```

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":[
            {
                "provider_id":"73aa4d40248849c48cb0fcde88d1d1d1",
                "is_deleted":0,
                "network":"1.5Gbps  --  25万PPS",
                "origin_name":"S5.SMALL2",
                "deleted_time":null,
                "memory":2,
                "enabled":1,
                "cpu":1,
                "extend_info":{

                },
                "provider":"tencentcloud",
                "created_time":"2021-01-21 11:31:34",
                "updated_time":"2021-01-21 11:31:34",
                "id":"a814c4b2400e43f89d30cd167a9cf9c3",
                "name":"1C-2G"
            }
        ]
    }
}
```



##### create:

url: /terraform/v1/vm/instance_type

字段：



输入：


```
"name"           类型名称       string  必填
"provider_id",   云厂商id      string  必填
"origin_name",   云厂商实例规格  string  必填
"cpu",           cpu个数        int  必填
"memory",        内存大小       int  必填
"network",       网络参数      string  选填
"extend_info"    其他信息      list   选填


例如： 
{
"name": "1C-2G",
 "provider_id": "73aa4d40248849c48cb0fcde88d1d1d1", 
"origin_name": "S5.SMALL2",
 "cpu": 1, 
"memory": 2,
 "network": "1.5Gbps  --  25万PPS",
 "extend_info": {}
}

```



输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":"a814c4b2400e43f89d30cd167a9cf9c3"
    }
}
```



##### 详情:

url:  /terraform/v1/vm/instance_type/{id}

参数： "id", 

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "provider_id":"73aa4d40248849c48cb0fcde88d1d1d1",
        "is_deleted":0,
        "network":"1.5Gbps  --  25万PPS",
        "origin_name":"S5.SMALL2",
        "deleted_time":null,
        "memory":2,
        "enabled":1,
        "cpu":1,
        "extend_info":{

        },
        "provider":"tencentcloud",
        "created_time":"2021-01-21 11:31:34",
        "updated_time":"2021-01-21 11:31:34",
        "id":"a814c4b2400e43f89d30cd167a9cf9c3",
        "name":"1C-2G"
    }
}
```


##### update:

url:  /terraform/v1/vm/instance_type/{id}

参数： 

```
"name", 
"provider_id", 
"origin_name",
"cpu", 
"memory", 
"network", 
"extend_info"
```



输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":{
            "provider_id":"73aa4d40248849c48cb0fcde88d1d1d1",
            "provider":null,
            "created_time":"2021-01-21 11:31:34",
            "id":"a814c4b2400e43f89d30cd167a9cf9c3",
            "name":"1C-2G",
            "is_deleted":0,
            "network":"1.5Gbps  --  25万PPS",
            "origin_name":"S5.SMALL2",
            "deleted_time":null,
            "enabled":1,
            "updated_time":"2021-01-21 11:38:42",
            "extend_info":{

            },
            "memory":2,
            "cpu":1
        }
    }
}
```


##### delete:

url:  /terraform/v1/vm/instance_type/{id}

参数： id


输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "data":[
            {
                "id":"76c8286bed1e444db7bee8ef5129ede5"
            }
        ]
    }
}
```

---

---


#### secret (云厂商认证信息)

##### list:

url: /terraform/v1/configer/secret

参数： "id", "name", "display_name", "region", 

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":[
            {
                "secret_info":"{cipher_a}oc+hXvxxxxxxxxxxxxx",
                "display_name":"alicloud_secret",
                "name":"alicloud_secret",
                "deleted_time":null,
                "region":null,
                "enabled":1,
                "updated_time":"2021-02-22 16:47:45",
                "extend_info":{

                },
                "provider":"alicloud",
                "created_time":"2021-02-22 16:47:45",
                "is_deleted":0,
                "id":"443318b72e91438896fc5b901901c285"
            }
        ]
    }
}
```



##### create:

url: /terraform/v1/configer/secret

字段：



输入：


```
name         string  必填
display_name  string  选填
provider    string  云厂商  必填
secret_info    json  认证信息 必填
region        string  选填
extend_info    json



示例：
{
"name": "xxxxx", 
"display_name": "tencenssst", 
"provider": "tencentcloud",
"secret_info": {"secret_id": "xxxxxx", "secret_key": "xxxx"}, 
"region": null, 
"extend_info": {}
}

```



输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":"8a772999c34e40faa503b59a026971aa"
    }
}
```



##### 详情:

url: /terraform/v1/configer/secret/{id}

参数： "id", 

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "secret_info":"{cipher_a}Rxxxxxxxxxxxx",
        "display_name":"tencenssst",
        "name":"xxxxx",
        "deleted_time":null,
        "region":null,
        "enabled":1,
        "updated_time":"2021-02-23 11:23:08",
        "extend_info":{

        },
        "provider":"tencentcloud",
        "created_time":"2021-02-23 11:23:08",
        "is_deleted":0,
        "id":"8a772999c34e40faa503b59a026971aa"
    }
}
```


##### update:

url: /terraform/v1/configer/secret/{id}

参数： 
name         string  
display_name  string 
provider    string  
secret_info    json 
region        string 
extend_info    json

输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "count":1,
        "data":{
            "secret_info":"{cipher_a}+vvvvvv",
            "display_name":"tencenssst",
            "name":"xxxxx",
            "deleted_time":null,
            "region":null,
            "enabled":1,
            "updated_time":"2021-02-23 11:27:04",
            "extend_info":{

            },
            "provider":"tencentcloud",
            "created_time":"2021-02-23 11:23:08",
            "is_deleted":0,
            "id":"8a772999c34e40faa503b59a026971aa"
        }
    }
}
```


##### delete:

url: /terraform/v1/configer/secret/{id}

参数： id


输出：

```
{
    "status":"OK",
    "message":"OK",
    "code":0,
    "data":{
        "data":1
    }
}
```

-----