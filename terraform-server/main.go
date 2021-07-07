package main

import (
	"flag"
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/log_operation"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
)

// @title Terraform Server
// @version 1.0
// @description Terraform 插件后台服务
func main() {
	configFile := flag.String("c", "conf/default.json", "config file path")
	flag.Parse()
	if initConfigMessage := models.InitConfig(*configFile); initConfigMessage != "" {
		fmt.Printf("Init config file error,%s \n", initConfigMessage)
		return
	}
	log.InitLogger()
	if initDbError := db.InitDatabase(); initDbError != nil {
		return
	}

	go log_operation.StartConsumeOperationLog()
	//start http
	api.InitHttpServer()

}
