FROM python:2.7.18-slim
LABEL maintainer = "Webank CTB Team"

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    mkdir /data && mkdir -p /app/wecube_plugins_terraform

WORKDIR /app/wecube_plugins_terraform/

COPY . .

RUN mkdir -p /usr/local/share/terraform/plugins && \
    rm -rf /app/wecube_plugins_terraform/bin/terraform_0.15.5_linux_amd64.zip && \
    ls /app/wecube_plugins_terraform/bin && \
    \cp /app/wecube_plugins_terraform/bin/terraform /usr/bin/terraform && \
    ls -la && \
    apt update && apt-get -y install gcc python-dev && \
    pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r /app/wecube_plugins_terraform/requirements.txt && \
    chmod +x /app/wecube_plugins_terraform/bin/*.sh

EXPOSE 8999
CMD ["/app/wecube_plugins_terraform/bin/start.sh"]