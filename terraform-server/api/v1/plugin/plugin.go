package plugin

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func PluginCreate(c *gin.Context) {
	var param models.PluginTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	param.CreateUser = user
	rowData, err := db.PluginCreate(&param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func PluginList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.PluginList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.PluginTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func PluginDelete(c *gin.Context) {
	pluginId := c.Param("pluginId")

	if pluginId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param pluginId can not be empty"))
		return
	}
	err := db.PluginDelete(pluginId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func PluginUpdate(c *gin.Context) {
	var param models.PluginTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	pluginId := c.Param("pluginId")
	if pluginId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param pluginId can not be empty"))
		return
	}
	user := middleware.GetRequestUser(c)
	param.UpdateUser = user
	err = db.PluginUpdate(pluginId, &param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func PluginBatchCreate(c *gin.Context) {
	var param []*models.PluginTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	rowData, err := db.PluginBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func PluginBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.PluginBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func PluginBatchUpdate(c *gin.Context) {
	var param []*models.PluginTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.PluginBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}
