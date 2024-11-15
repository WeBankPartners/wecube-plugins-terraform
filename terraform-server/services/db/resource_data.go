package db

import (
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"time"
)

/*
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
*/

func ResourceDataList(ids string) (rowData []*models.ResourceDataQuery, err error) {
	sqlCmd := "SELECT t1.*,t2.name AS resource_title,t3.id AS provider_id,t3.name AS provider_name,t3.version AS provider_version,t3.secret_id_attr_name " +
		"AS provider_secret_id_attr_name,t3.secret_key_attr_name AS provider_secret_key_attr_name,t3.region_attr_name AS provider_region_attr_name,t3.Initialized " +
		"AS provider_initialized,t3.name_space AS provider_namespace FROM resource_data t1 LEFT JOIN source t2 ON t1.resource=t2.id LEFT JOIN provider t3 ON t2.provider=t3.id WHERE 1=1"
	if ids != "" {
		sqlCmd += " AND t1.id IN ('" + ids + "')"
	}
	sqlCmd += " ORDER BY t1.id DESC"
	err = x.SQL(sqlCmd).Find(&rowData)
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
		data := &models.ResourceDataTable{Id: id, Resource: param[i].Resource, ResourceId: param[i].ResourceId, ResourceAssetId: param[i].ResourceAssetId,
			RegionId: param[i].RegionId, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
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

func ResourceDataDebugList(ids string) (rowData []*models.ResourceDataQuery, err error) {
	sqlCmd := "SELECT t1.*,t2.name AS resource_title FROM resource_data_debug t1 LEFT JOIN source t2 ON t1.resource=t2.id WHERE 1=1"
	if ids != "" {
		sqlCmd += " AND t1.id IN ('" + ids + "')"
	}
	sqlCmd += " ORDER BY t1.id DESC"
	err = x.SQL(sqlCmd).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get resource_data_debug list error", log.Error(err))
	}
	return
}