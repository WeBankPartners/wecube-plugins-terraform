package provider

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func ProviderTemplateValueCreate(c *gin.Context) {
	var param models.ProviderTemplateValueTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	param.CreateUser = user
	rowData, err := db.ProviderTemplateValueCreate(&param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

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

func ProviderTemplateValueDelete(c *gin.Context) {
	Id := c.Param("providerTemplateValueId")

	if Id == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param Id can not be empty"))
		return
	}
	err := db.ProviderTemplateValueDelete(Id)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func ProviderTemplateValueUpdate(c *gin.Context) {
	var param models.ProviderTemplateValueTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	Id := c.Param("providerTemplateValueId")
	if Id == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param Id can not be empty"))
		return
	}
	user := middleware.GetRequestUser(c)
	param.UpdateUser = user
	err = db.ProviderTemplateValueUpdate(Id, &param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
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
	rowData, err := db.ProviderTemplateValueBatchCreate(user, param)
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
	templateName := c.Param("templateName")
	if templateName == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param templateName can not be empty"))
		return
	}
	rowData, err := db.ProviderTemplateValueListByTemplate(templateName)
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