package source

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func SourceCreate(c *gin.Context) {
	var param models.SourceTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	param.CreateUser = user
	rowData, err := db.SourceCreate(&param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func SourceList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.SourceList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.SourceTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func SourceDelete(c *gin.Context) {
	sourceId := c.Param("sourceId")

	if sourceId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param sourceId can not be empty"))
		return
	}
	err := db.SourceDelete(sourceId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func SourceUpdate(c *gin.Context) {
	var param models.SourceTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	sourceId := c.Param("sourceId")
	if sourceId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param sourceId can not be empty"))
		return
	}
	user := middleware.GetRequestUser(c)
	param.UpdateUser = user
	err = db.SourceUpdate(sourceId, &param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func SourceBatchCreate(c *gin.Context) {
	var param []*models.SourceTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	rowData, err := db.SourceBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func SourceBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.SourceBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func SourceBatchUpdate(c *gin.Context) {
	var param []*models.SourceTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.SourceBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}
