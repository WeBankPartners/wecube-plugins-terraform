
### 一.简介
Terraform 多云管理

支持的云厂商： 腾讯云(tencentcloud),


### 二. 安装

安装rpm包
```
yum install gcc -y
yum install -y python-virtualenv.noarch
```
创建python虚拟环境
```
mkdir -p /wecube
cd /wecube
virtualenv terraform_env
 . /wecube/terraform_env/bin/activate
```

初始化：
```
mkdir /apps/wecube_plugins_terraform
cd wecube_plugins_terraform
git clone https://github.com/WeBankPartners/wecube-plugins-terraform.git
pip install -r requirements.txt
```

### 三. terraform 插件配置
在plugins 中创建provider name 目录， 并写入对应的版本需求文件 versions.tf

例如： 腾讯云 tencentcloud
则在 plugins 下创建 tencentcloud 目录， 并创建version.tf 文件

注： 为加速terraform执行， 需要将对应的provider插件放在os cache目录中：
`/usr/local/share/terraform/plugins/registry.terraform.io`

例如cache tencentcloud 的插件，
则将tencentcloud插件放入 `/usr/local/share/terraform/plugins/registry.terraform.io/tencentcloudstack`

### 四. terraform 接入云厂商配置信息
转换规则：
字段属性转换定义说明：
1. string 直接转换为对应的值， 若为空字符串，则不转换， 如 {"cider": ''}
2. json 定义约束, 类型为json
   type定义类型, 可定义： [string, int, float, json, list]
   allow_null 是否允许为空， 0 为不允许为空，反之则允许为空
   convert 转换为对应的字段名称， 若不定义，则不转换

   例如： "name": {"type": "string", "allow_null": 0, "convert": "name"}
    name字段，定义type为string， 不运行为空， 转换为name
3. 要求的关键字不使用， 则可使用减号移除， 如：{"tag": "-"}

如下以腾讯云为例， 其他云厂商接入类似可参考进行配置：
1. 配置云厂商：
url: /terraform/v1/configer/provider

```
{
    "display_name":"腾讯云",
    "name":"tencentcloud",
    "zone":"",
    "region":"",
    "secret_id":"xxxx", # 云厂商提供的api key信息
    "secret_key":"xxxx", # 云厂商提供的api key信息
    "extend_info":{

    },
    "provider_property":{
        "secret_id":"secret_id",
        "secret_key":"secret_key",
        "region":"region"
    }
}
```
secret_id 云厂商提供的api key信息
secret_key 云厂商提供的api key信息
provider_property配置字段的转换： 如secret_id 需要转换为api_id 则配置 "secret_id": "api_id"

2. 配置属性资源：
例如： vpc 网段配置：
url: /terraform/v1/configer/resource

```
{
"resource_name": "vpc",
"property": "tencentcloud_vpc",
"provider": "tencentcloud",
"extend_info": {"is_multicast": false,"tags":{"type": "json"}},
"resource_property": {
	"name": {"type": "string", "allow_null": 0, "convert": "name"},
	"cider": {"type": "string", "allow_null": 0, "convert": "cidr_block"}
},
"output_property": {}
}
```

3. 配置通用值
用于将云厂商之间不同的值进行统一
例如image字段的 centos 7.2字段
云厂商A为： centos-7.2 x64
原厂商B为： linux centos 7.2 x64

则可以统一命名为centos 7.2 进行转换

url: /terraform/v1/configer/keyconfig

```
{
"resource": "subnet",
"property": "cidr",
"provider": "tencentcloud",
"value_config": {
	"subnet_20": "10.0.20.0/24",
	"subnet_1": "10.0.1.0/24"
}
}
```

