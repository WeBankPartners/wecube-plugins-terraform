package tfstate_attribute

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func TfstateAttributeCreate(c *gin.Context) {
	var param models.TfstateAttributeTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	param.CreateUser = user
	rowData, err := db.TfstateAttributeCreate(&param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func TfstateAttributeList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
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

func TfstateAttributeDelete(c *gin.Context) {
	tfstateAttributeId := c.Param("tfstateAttributeId")

	if tfstateAttributeId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param tfstateAttributeId can not be empty"))
		return
	}
	err := db.TfstateAttributeDelete(tfstateAttributeId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TfstateAttributeUpdate(c *gin.Context) {
	var param models.TfstateAttributeTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	tfstateAttributeId := c.Param("tfstateAttributeId")
	if tfstateAttributeId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param tfstateAttributeId can not be empty"))
		return
	}
	user := middleware.GetRequestUser(c)
	param.UpdateUser = user
	err = db.TfstateAttributeUpdate(tfstateAttributeId, &param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
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
	rowData, err := db.TfstateAttributeBatchCreate(user, param)
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
