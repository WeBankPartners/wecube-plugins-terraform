package db

import (
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"time"
)

func ResourceDataList(paramsMap map[string]interface{}) (rowData []*models.ResourceDataTable, err error) {
	sqlCmd := "SELECT * FROM resource_data WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get resource_data list error", log.Error(err))
	}
	return
}

func ResourceDataBatchCreate(user string, param []*models.ResourceDataTable) (rowData []*models.ResourceDataTable, err error) {
	actions := []*execAction{}
	tableName := "resource_data"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.ResourceDataTable{Id: id, Source: param[i].Source, ResourceId: param[i].ResourceId, ResourceAssetId: param[i].ResourceAssetId,
			CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create resource_data fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create resource_data fail,%s ", err.Error())
	}
	return
}

func ResourceDataBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "resource_data"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete resource_data fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete resource_data fail,%s ", err.Error())
	}
	return
}

func ResourceDataBatchUpdate(user string, param []*models.ResourceDataTable) (err error) {
	actions := []*execAction{}
	tableName := "resource_data"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update resource_data fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update resource_data fail,%s ", err.Error())
	}
	return
}