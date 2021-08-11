package template

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func TemplateValueList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.TemplateValueList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.TemplateValueTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func TemplateValueBatchCreate(c *gin.Context) {
	var param []*models.TemplateValueTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	// rowData, err := db.TemplateValueBatchCreate(user, param)
	rowData, err := db.TemplateValueBatchCreateUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func TemplateValueBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.TemplateValueBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TemplateValueBatchUpdate(c *gin.Context) {
	var param []*models.TemplateValueTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.TemplateValueBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TemplateValueListByParameter(c *gin.Context) {
	parameterId := c.Param("parameterId")
	if parameterId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param pluginId can not be empty"))
		return
	}
	rowData, err := db.TemplateValueListByParameter(parameterId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.TemplateValueTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}