package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func ProviderCreate(param *models.ProviderTable) (rowData *models.ProviderTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO provider(id,name,version,create_user,create_time) VALUE (?,?,?,?,?)",
		id, param.Name, param.Version, param.CreateUser, createTime)

	rowData = &models.ProviderTable{Id: id, Name: param.Name, Version:param.Version, CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create provider fail,%s ", err.Error())
	}
	return
}

func ProviderList(paramsMap map[string]interface{}) (rowData []*models.ProviderTable, err error) {
	sqlCmd := "SELECT * FROM provider WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get provider list error", log.Error(err))
	}
	return
}

func ProviderDelete(providerId string) (err error) {
	var providerList []*models.ProviderTable
	err = x.SQL("SELECT id FROM provider WHERE id=?", providerId).Find(&providerList)
	if err != nil {
		log.Logger.Error("Try to query provider fail", log.String("providerId", providerId), log.Error(err))
		return
	}
	if len(providerList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM provider WHERE id=?", providerId)
	return
}

func ProviderUpdate(providerId string, param *models.ProviderTable) (err error) {
	var providerList []*models.ProviderTable
	err = x.SQL("SELECT id FROM provider WHERE id=?", providerId).Find(&providerList)
	if err != nil {
		log.Logger.Error("Try to query provider fail", log.String("providerId", providerId), log.Error(err))
		return
	}
	if len(providerList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE provider SET name=?,version=?,update_time=?,update_user=? WHERE id=?",
		param.Name, param.Version, updateTime, param.UpdateUser, providerId)
	return
}

func ProviderBatchCreate(user string, param []*models.ProviderTable) (rowData []*models.ProviderTable, err error) {
	actions := []*execAction{}
	tableName := "provider"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.ProviderTable{Id: id, Name: param[i].Name, Version: param[i].Version, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create provider fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create provider fail,%s ", err.Error())
	}
	return
}

func ProviderBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "provider"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete provider fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete provider fail,%s ", err.Error())
	}
	return
}

func ProviderBatchUpdate(user string, param []*models.ProviderTable) (err error) {
	actions := []*execAction{}
	tableName := "provider"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update provider fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update provider fail,%s ", err.Error())
	}
	return
}
