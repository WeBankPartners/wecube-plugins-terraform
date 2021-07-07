package tf_argument

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func TfArgumentCreate(c *gin.Context) {
	var param models.TfArgumentTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	param.CreateUser = user
	rowData, err := db.TfArgumentCreate(&param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func TfArgumentList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.TfArgumentList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.TfArgumentTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func TfArgumentDelete(c *gin.Context) {
	tfArgumentId := c.Param("tfArgumentId")

	if tfArgumentId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param tfArgumentId can not be empty"))
		return
	}
	err := db.TfArgumentDelete(tfArgumentId)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TfArgumentUpdate(c *gin.Context) {
	var param models.TfArgumentTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	tfArgumentId := c.Param("tfArgumentId")
	if tfArgumentId == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param tfArgumentId can not be empty"))
		return
	}
	user := middleware.GetRequestUser(c)
	param.UpdateUser = user
	err = db.TfArgumentUpdate(tfArgumentId, &param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TfArgumentBatchCreate(c *gin.Context) {
	var param []*models.TfArgumentTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	rowData, err := db.TfArgumentBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func TfArgumentBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.TfArgumentBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TfArgumentBatchUpdate(c *gin.Context) {
	var param []*models.TfArgumentTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.TfArgumentBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}
