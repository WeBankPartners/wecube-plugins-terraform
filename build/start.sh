#!/bin/bash

sed -i "s~{{TERRAFORM_MYSQL_HOST}}~$TERRAFORM_MYSQL_HOST~g" /app/terraform/conf/default.json
sed -i "s~{{TERRAFORM_MYSQL_PORT}}~$TERRAFORM_MYSQL_PORT~g" /app/terraform/conf/default.json
sed -i "s~{{TERRAFORM_MYSQL_SCHEMA}}~$TERRAFORM_MYSQL_SCHEMA~g" /app/terraform/conf/default.json
sed -i "s~{{TERRAFORM_MYSQL_USER}}~$TERRAFORM_MYSQL_USER~g" /app/terraform/conf/default.json
sed -i "s~{{TERRAFORM_MYSQL_PWD}}~$TERRAFORM_MYSQL_PWD~g" /app/terraform/conf/default.json
sed -i "s~{{TERRAFORM_LOG_LEVEL}}~$TERRAFORM_LOG_LEVEL~g" /app/terraform/conf/default.json
sed -i "s~{{GATEWAY_URL}}~$GATEWAY_URL~g" /app/terraform/conf/default.json
sed -i "s~{{JWT_SIGNING_KEY}}~$JWT_SIGNING_KEY~g" /app/terraform/conf/default.json
sed -i "s~{{SUB_SYSTEM_CODE}}~$SUB_SYSTEM_CODE~g" /app/terraform/conf/default.json
sed -i "s~{{SUB_SYSTEM_KEY}}~$SUB_SYSTEM_KEY~g" /app/terraform/conf/default.json
sed -i "s~{{PLUGIN_VERSION}}~$PLUGIN_VERSION~g" /app/terraform/conf/default.json

./terraform-server