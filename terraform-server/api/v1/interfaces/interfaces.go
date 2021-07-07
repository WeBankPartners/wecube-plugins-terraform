package interfaces

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func InterfaceCreate(c *gin.Context) {
	var param models.InterfaceTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	param.CreateUser = user
	rowData, err := db.InterfaceCreate(&param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
	return
}

func InterfaceList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.InterfaceList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.InterfaceTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func InterfaceDelete(c *gin.Context) {
	interfaceId := c.Param("interfaceId")

	if interfaceId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param interfaceId can not be empty"))
		return
	}
	err := db.InterfaceDelete(interfaceId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func InterfaceUpdate(c *gin.Context) {
	var param models.InterfaceTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	interfaceId := c.Param("interfaceId")
	if interfaceId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param interfaceId can not be empty"))
		return
	}
	user := middleware.GetRequestUser(c)
	param.UpdateUser = user
	err = db.InterfaceUpdate(interfaceId, &param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func InterfaceBatchCreate(c *gin.Context) {
	var param []*models.InterfaceTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	rowData, err := db.InterfaceBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func InterfaceBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.InterfaceBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func InterfaceBatchUpdate(c *gin.Context) {
	var param []*models.InterfaceTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.InterfaceBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}
