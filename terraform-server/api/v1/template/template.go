package template

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func TemplateCreate(c *gin.Context) {
	var param models.TemplateTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	param.CreateUser = user
	rowData, err := db.TemplateCreate(&param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
	return
}

func TemplateList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.TemplateList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.TemplateTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func TemplateDelete(c *gin.Context) {
	templateId := c.Param("templateId")

	if templateId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param templateId can not be empty"))
		return
	}
	err := db.TemplateDelete(templateId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TemplateUpdate(c *gin.Context) {
	var param models.TemplateTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	templateId := c.Param("templateId")
	if templateId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param templateId can not be empty"))
		return
	}
	user := middleware.GetRequestUser(c)
	param.UpdateUser = user
	err = db.TemplateUpdate(templateId, &param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TemplateBatchCreate(c *gin.Context) {
	var param []*models.TemplateTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	rowData, err := db.TemplateBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func TemplateBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.TemplateBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TemplateBatchUpdate(c *gin.Context) {
	var param []*models.TemplateTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.TemplateBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TemplateListByPlugin(c *gin.Context) {
	pluginId := c.Param("pluginId")
	if pluginId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param pluginId can not be empty"))
		return
	}
	rowData, err := db.TemplateListByPlugin(pluginId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.TemplateTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}