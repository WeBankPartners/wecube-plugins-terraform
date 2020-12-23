
## 安装rpm包
```
yum install gcc -y
yum install -y python-virtualenv.noarch
```

## 创建虚拟环境
```
mkdir -p /nemo
cd /nemo
virtualenv terraform_env
 . /nemo/terraform_env/bin/activate
```

