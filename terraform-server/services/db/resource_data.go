package db

import (
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"time"
)

var resourceDataFieldMap = map[string]struct {
	Column    string
	QueryType string // "eq" 或 "like"
}{
	"resource":          {"t1.resource", "eq"},
	"resource_id":       {"t1.resource_id", "like"},
	"resource_asset_id": {"t1.resource_asset_id", "like"},
}

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

func ResourceDataListWithPage(paramsMap map[string]interface{}, page, pageSize int) (rowData []*models.ResourceDataQuery, total int, err error) {
	sqlCmd := "SELECT t1.*,t2.name AS resource_title,t3.id AS provider_id,t3.name AS provider_name,t3.version AS provider_version,t3.secret_id_attr_name " +
		"AS provider_secret_id_attr_name,t3.secret_key_attr_name AS provider_secret_key_attr_name,t3.region_attr_name AS provider_region_attr_name,t3.Initialized " +
		"AS provider_initialized,t3.name_space AS provider_namespace FROM resource_data t1 LEFT JOIN source t2 ON t1.resource=t2.id LEFT JOIN provider t3 ON t2.provider=t3.id WHERE 1=1"
	countCmd := "SELECT count(1) FROM resource_data t1 LEFT JOIN source t2 ON t1.resource=t2.id LEFT JOIN provider t3 ON t2.provider=t3.id WHERE 1=1"
	var paramArgs []interface{}
	var countArgs []interface{}
	for k, v := range paramsMap {
		if field, ok := resourceDataFieldMap[k]; ok {
			if field.QueryType == "eq" {
				sqlCmd += " AND " + field.Column + "=?"
				countCmd += " AND " + field.Column + "=?"
				paramArgs = append(paramArgs, v)
				countArgs = append(countArgs, v)
			} else if field.QueryType == "like" {
				sqlCmd += " AND " + field.Column + " LIKE ?"
				countCmd += " AND " + field.Column + " LIKE ?"
				paramArgs = append(paramArgs, "%"+fmt.Sprint(v)+"%")
				countArgs = append(countArgs, "%"+fmt.Sprint(v)+"%")
			}
		}
	}
	sqlCmd += " ORDER BY t1.id DESC LIMIT ? OFFSET ?"
	paramArgs = append(paramArgs, pageSize, (page-1)*pageSize)
	_, err = x.SQL(countCmd, countArgs...).Get(&total)
	if err != nil {
		log.Logger.Error("Get resource_data count error", log.Error(err))
		return
	}
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

func GetAllResourceTypes() (resourceList []*models.SourceTable, err error) {
	sqlCmd := "SELECT id, name FROM source"
	err = x.SQL(sqlCmd).Find(&resourceList)
	if err != nil {
		log.Logger.Error("Get all resource types error", log.Error(err))
	}
	return
}
