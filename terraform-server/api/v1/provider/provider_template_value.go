package provider

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func ProviderTemplateValueList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.ProviderTemplateValueList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.ProviderTemplateValueTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func ProviderTemplateValueBatchCreate(c *gin.Context) {
	var param []*models.ProviderTemplateValueTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	// rowData, err := db.ProviderTemplateValueBatchCreate(user, param)
	rowData, err := db.ProviderTemplateValueBatchCreateUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func ProviderTemplateValueBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.ProviderTemplateValueBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func ProviderTemplateValueBatchUpdate(c *gin.Context) {
	var param []*models.ProviderTemplateValueTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.ProviderTemplateValueBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func ProviderTemplateValueListByTemplate(c *gin.Context) {
	templateId := c.Param("templateId")
	if templateId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param templateId can not be empty"))
		return
	}
	rowData, err := db.ProviderTemplateValueListByTemplate(templateId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.TemplateValueQuery{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}