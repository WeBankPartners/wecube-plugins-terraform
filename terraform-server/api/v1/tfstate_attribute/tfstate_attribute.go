package tfstate_attribute

import (
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func TfstateAttributeList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	sourceId := c.Query("sourceId")
	if sourceId != "" {
		paramsMap["source"] = sourceId
	}
	rowData, err := db.TfstateAttributeList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.TfstateAttributeTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func TfstateAttributeBatchCreate(c *gin.Context) {
	var param []*models.TfstateAttributeTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	// rowData, err := db.TfstateAttributeBatchCreate(user, param)
	rowData, err := db.TfstateAttributeBatchCreateUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func TfstateAttributeBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.TfstateAttributeBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TfstateAttributeBatchUpdate(c *gin.Context) {
	var param []*models.TfstateAttributeTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.TfstateAttributeBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}
