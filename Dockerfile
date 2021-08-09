FROM ccr.ccs.tencentyun.com/webankpartners/terrafrom-base:v1.0.2

ENV BASE_HOME=/app/terraform

RUN mkdir -p $BASE_HOME $BASE_HOME/conf $BASE_HOME/logs
RUN mv /data/terraform/providers /data/terraform/providers_tpl
RUN mkdir -p /data/terraform/providers

ADD build/start.sh $BASE_HOME/
ADD build/stop.sh $BASE_HOME/
ADD build/default.json $BASE_HOME/conf/
ADD terraform-server/terraform-server $BASE_HOME/
ADD ui/dist $BASE_HOME/public

WORKDIR $BASE_HOME
ENTRYPOINT ["/bin/sh", "start.sh"]