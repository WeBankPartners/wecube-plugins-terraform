package log_operation

import (
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

var operationLogChannel = make(chan *models.SysLogTable, 100)

func StartConsumeOperationLog() {
	log.Logger.Info("start consume operation log job")
	for {
		operationLogObj := <-operationLogChannel
		db.SaveOperationLog(operationLogObj)
	}
}

func HandleOperationLog(c *gin.Context) {
	var operationLogObj models.SysLogTable
	operationLogObj.Operator = c.GetString("user")
	operationLogObj.Operation = c.Param("operation")
	if operationLogObj.Operation == "" {
		operationLogObj.Operation = c.Request.Method
	}
	operationLogObj.Content = c.GetString("requestBody")
	operationLogObj.RequestUrl = c.Request.RequestURI
	for i, v := range strings.Split(operationLogObj.RequestUrl, "/") {
		if i == 4 {
			if v == "ci-data" {
				operationLogObj.LogCat = "CI Data Management"
			} else if v == "ci-types" || v == "ci-types-attr" {
				operationLogObj.LogCat = "CI Type Management"
			} else if v == "base-key" {
				operationLogObj.LogCat = "Base Data Management"
			} else if v == "permissions" {
				operationLogObj.LogCat = "Permission Management"
			} else {
				operationLogObj.LogCat = v
			}
			break
		}
	}
	operationLogObj.ClientHost = middleware.GetRemoteIp(c)
	operationLogChannel <- &operationLogObj
}

func QueryOperationLog(c *gin.Context) {
	//Param validate
	var param models.QueryRequestParam
	if err := c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	//Query database
	pageInfo, rowData, err := db.QueryOperationLog(&param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnPageData(c, pageInfo, rowData)
	}
}

func GetAllLogOperation(c *gin.Context) {
	operationList := db.GetAllLogOperation()
	middleware.ReturnData(c, operationList)
}
