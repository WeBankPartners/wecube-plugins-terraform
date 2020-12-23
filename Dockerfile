FROM python:2.7.18-slim
LABEL maintainer = "Webank CTB Team"

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    mkdir -p /app/wecube-plugins-terraform

WORKDIR /app/wecube-plugins-terraform/

COPY . .

RUN ls -la && \
    pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r /app/wecube-plugins-terraform/requirements.txt && \
    chmod +x /app/wecube-plugins-terraform/bin/*.sh

EXPOSE 8999
CMD ["/app/wecube-plugins-terraform/bin/start.sh"]