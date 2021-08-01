package provider

import (
	"fmt"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/cipher"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
)

func ProviderInfoList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.ProviderInfoList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.ProviderInfoQuery{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func ProviderInfoBatchCreate(c *gin.Context) {
	var param []*models.ProviderInfoTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	for i := range param {
		enCodeSecretId, encodeErr := cipher.AesEnPasswordByGuid(models.PGuid, models.Config.Auth.PasswordSeed, param[i].SecretId, "")
		if encodeErr != nil {
			err = fmt.Errorf("Try to encode secretId fail,%s ", encodeErr.Error())
			return
		}
		enCodeSecretKey, encodeErr := cipher.AesEnPasswordByGuid(models.PGuid, models.Config.Auth.PasswordSeed, param[i].SecretKey, "")
		if encodeErr != nil {
			err = fmt.Errorf("Try to encode secretKey fail,%s ", encodeErr.Error())
			return
		}
		param[i].SecretId = enCodeSecretId
		param[i].SecretKey = enCodeSecretKey
	}
	rowData, err := db.ProviderInfoBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func ProviderInfoBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.ProviderInfoBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func ProviderInfoBatchUpdate(c *gin.Context) {
	var param []*models.ProviderInfoTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	for i := range param {
		enCodeSecretId, encodeErr := cipher.AesEnPasswordByGuid(models.PGuid, models.Config.Auth.PasswordSeed, param[i].SecretId, "")
		if encodeErr != nil {
			err = fmt.Errorf("Try to encode secretId fail,%s ", encodeErr.Error())
			return
		}
		enCodeSecretKey, encodeErr := cipher.AesEnPasswordByGuid(models.PGuid, models.Config.Auth.PasswordSeed, param[i].SecretKey, "")
		if encodeErr != nil {
			err = fmt.Errorf("Try to encode secretKey fail,%s ", encodeErr.Error())
			return
		}
		param[i].SecretId = enCodeSecretId
		param[i].SecretKey = enCodeSecretKey
	}
	err = db.ProviderInfoBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}
