package provider

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func ProviderList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.ProviderList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.ProviderTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func ProviderBatchCreate(c *gin.Context) {
	var param []*models.ProviderTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	rowData, err := db.ProviderBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func ProviderBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.ProviderBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func ProviderBatchUpdate(c *gin.Context) {
	var param []*models.ProviderTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.ProviderBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func ProviderPluginExport(c *gin.Context) {
	providerId := c.Query("provider")
	pluginId := c.Query("plugin")
	if providerId == "" || pluginId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Param provider and plugin can not emtpy "))
		return
	}
	result, err := db.ProviderPluginExport(providerId, pluginId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
		return
	}
	b, err := json.Marshal(result)
	if err != nil {
		middleware.ReturnServerHandleError(c, fmt.Errorf("Export terrform config fail, json marshal object error:%s ", err.Error()))
		return
	}
	c.Writer.Header().Add("Content-Disposition", fmt.Sprintf("attachment; filename=%s_%s.json", "terrform_config", time.Now().Format("20060102150405")))
	c.Data(http.StatusOK, "application/octet-stream", b)
}

func ProviderPluginImport(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ResponseErrorJson{StatusCode: "PARAM_HANDLE_ERROR", StatusMessage: "Http read upload file fail:" + err.Error(), Data: nil})
		return
	}
	f, err := file.Open()
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ResponseErrorJson{StatusCode: "PARAM_HANDLE_ERROR", StatusMessage: "File open error:" + err.Error(), Data: nil})
		return
	}
	var paramObj models.ProviderPluginImportObj
	b, err := ioutil.ReadAll(f)
	defer f.Close()
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ResponseErrorJson{StatusCode: "PARAM_HANDLE_ERROR", StatusMessage: "Read content fail error:" + err.Error(), Data: nil})
		return
	}
	err = json.Unmarshal(b, &paramObj)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ResponseErrorJson{StatusCode: "PARAM_HANDLE_ERROR", StatusMessage: "Json unmarshal fail error:" + err.Error(), Data: nil})
		return
	}
	err = db.ProviderPluginImport(paramObj, middleware.GetRequestUser(c))
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
}
