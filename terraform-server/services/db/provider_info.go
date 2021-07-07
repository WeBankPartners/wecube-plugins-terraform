package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func ProviderInfoCreate(param *models.ProviderInfoTable) (rowData *models.ProviderInfoTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO provider_info(id,name,provider,secret_id,secret_key,create_user,create_time) VALUE (?,?,?,?,?,?,?)",
		id, param.Name, param.Provider, param.SecretId, param.SecretKey, param.CreateUser, createTime)

	rowData = &models.ProviderInfoTable{Id: id, Name: param.Name, Provider: param.Provider, SecretId: param.SecretId,
		SecretKey: param.SecretKey, CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create providerInfo fail,%s ", err.Error())
	}
	return
}

func ProviderInfoList(paramsMap map[string]interface{}) (rowData []*models.ProviderInfoTable, err error) {
	sqlCmd := "SELECT * FROM provider_info WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get providerInfo list error", log.Error(err))
	}
	return
}

func ProviderInfoDelete(providerInfoId string) (err error) {
	var providerInfoList []*models.ProviderInfoTable
	err = x.SQL("SELECT id FROM provider_info WHERE id=?", providerInfoId).Find(&providerInfoList)
	if err != nil {
		log.Logger.Error("Try to query providerInfo fail", log.String("providerInfoId", providerInfoId), log.Error(err))
		return
	}
	if len(providerInfoList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM provider_info WHERE id=?", providerInfoId)
	return
}

func ProviderInfoUpdate(providerInfoId string, param *models.ProviderInfoTable) (err error) {
	var providerInfoList []*models.ProviderInfoTable
	err = x.SQL("SELECT id FROM provider_info WHERE id=?", providerInfoId).Find(&providerInfoList)
	if err != nil {
		log.Logger.Error("Try to query providerInfo fail", log.String("providerInfoId", providerInfoId), log.Error(err))
		return
	}
	if len(providerInfoList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE provider_info SET name=?,provider=?,secret_id=?,secret_key=?,update_time=?,update_user=? WHERE id=?",
		param.Name, param.Provider, param.SecretId, param.SecretKey, updateTime, param.UpdateUser, providerInfoId)
	return
}

func ProviderInfoBatchCreate(user string, param []*models.ProviderInfoTable) (rowData []*models.ProviderInfoTable, err error) {
	actions := []*execAction{}
	tableName := "provider_info"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.ProviderInfoTable{Id: id, Name: param[i].Name, Provider: param[i].Provider, SecretId: param[i].SecretId,
			SecretKey: param[i].SecretKey, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create provider_info fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create provider_info fail,%s ", err.Error())
	}
	return
}

func ProviderInfoBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "provider_info"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete provider_info fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete provider_info fail,%s ", err.Error())
	}
	return
}

func ProviderInfoBatchUpdate(user string, param []*models.ProviderInfoTable) (err error) {
	actions := []*execAction{}
	tableName := "provider_info"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update provider_info fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update provider_info fail,%s ", err.Error())
	}
	return
}
