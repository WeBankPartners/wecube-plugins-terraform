FROM python:2.7.18-slim
LABEL maintainer = "Webank CTB Team"

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    mkdir -p /app/wecube_plugins_terraform

WORKDIR /app/wecube_plugins_terraform/

COPY . .

RUN mkdir -p /usr/local/share/terraform/plugins && \
    tar -xvf /app/wecube_plugins_terraform/plugins/registry.terraform.io.tar  -C /usr/local/share/terraform/plugins && \
    ls /app/wecube_plugins_terraform/bin && \
    ls -la && \
    pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r /app/wecube_plugins_terraform/requirements.txt && \
    chmod +x /app/wecube_plugins_terraform/bin/*.sh

EXPOSE 8999
CMD ["/app/wecube_plugins_terraform/bin/start.sh"]