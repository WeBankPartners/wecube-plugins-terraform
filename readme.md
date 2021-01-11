
### 一.简介
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
git clone xxx
pip install -r requirements.txt
```

###三. terraform 插件
在plugins 中创建provider name 目录， 并写入对应的版本需求文件 versions.tf

例如： 腾讯云 tencentcloud
则在 plugins 下创建 tencentcloud 目录， 并创建version.tf 文件

注： 为加速terraform执行， 需要将对应的provider插件放在os cache目录中：
/usr/local/share/terraform/plugins/registry.terraform.io

例如cache tencentcloud 的插件，
则将tencentcloud插件放入 /usr/local/share/terraform/plugins/registry.terraform.io/tencentcloudstack
