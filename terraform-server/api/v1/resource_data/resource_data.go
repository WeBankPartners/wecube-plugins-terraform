package resource_data

import (
	"encoding/json"
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
	"io/ioutil"
	"reflect"
	"strings"
)

func ResourceDataBatchCreate(c *gin.Context) {
	var param []*models.ResourceDataTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	rowData, err := db.ResourceDataBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func ResourceDataList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.ResourceDataList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.ResourceDataTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func ResourceDataBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.ResourceDataBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func ResourceDataBatchUpdate(c *gin.Context) {
	var param []*models.ResourceDataTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.ResourceDataBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TerraformOperation(c *gin.Context) {
	plugin := c.Param("plugin")
	action := c.Param("action")

	if plugin == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param plugin can not be empty "))
		return
	}

	if action == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param action can not be empty "))
		return
	}

	var err error
	bodyData, err := ioutil.ReadAll(c.Request.Body)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	}

	var request_param map[string]interface{}
	err = json.Unmarshal(bodyData, &request_param)
	inputs := request_param["inputs"]
	p := reflect.ValueOf(inputs)
	params := []map[string]interface{}{}
	for i := 0; i < p.Len(); i++ {
		params = append(params, p.Index(i).Interface().(map[string]interface{}))
	}

	for i := range params {
		rowData, err := db.TerraformOperation(plugin, action, params[i])

		if err != nil {
			middleware.ReturnServerHandleError(c, err)
		} else {
			if rowData == nil {
				middleware.ReturnData(c, []string{})
			} else {
				middleware.ReturnData(c, rowData)
			}
		}
	}
	return
}
