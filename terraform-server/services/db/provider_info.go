package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func ProviderInfoList(paramsMap map[string]interface{}) (rowData []*models.ProviderInfoQuery, err error) {
	/*
	sqlCmd := "SELECT * FROM provider_info WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	 */
	sqlCmd := "SELECT t1.*,t2.name AS provider_title FROM provider_info t1 LEFT JOIN provider t2 ON t1.provider=t2.id"
	sqlCmd += " ORDER BY t1.id DESC"
	err = x.SQL(sqlCmd).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get providerInfo list error", log.Error(err))
	}
	return
}

func ProviderInfoBatchCreate(user string, param []*models.ProviderInfoTable) (rowData []*models.ProviderInfoTable, err error) {
	actions := []*execAction{}
	tableName := "provider_info"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.ProviderInfoTable{Id: id, Name: param[i].Name, Provider: param[i].Provider, SecretId: param[i].SecretId,
			SecretKey: param[i].SecretKey, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
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
