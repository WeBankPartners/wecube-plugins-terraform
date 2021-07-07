package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func SourceCreate(param *models.SourceTable) (rowData *models.SourceTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO source(id,name,plugin,provider,resource_asset_id_attribute,action,create_user,create_time) VALUE (?,?,?,?,?,?,?,?)",
		id, param.Name, param.Plugin, param.Provider, param.ResourceAssetIdAttribute, param.Action, param.CreateUser, createTime)

	rowData = &models.SourceTable{Id: id, Name: param.Name, Plugin: param.Plugin, Provider: param.Provider, ResourceAssetIdAttribute: param.ResourceAssetIdAttribute, Action: param.Action, CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create source fail,%s ", err.Error())
	}
	return
}

func SourceList(paramsMap map[string]interface{}) (rowData []*models.SourceTable, err error) {
	sqlCmd := "SELECT * FROM source WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get source list error", log.Error(err))
	}
	return
}

func SourceDelete(sourceId string) (err error) {
	var sourceList []*models.SourceTable
	err = x.SQL("SELECT id FROM source WHERE id=?", sourceId).Find(&sourceList)
	if err != nil {
		log.Logger.Error("Try to query source fail", log.String("sourceId", sourceId), log.Error(err))
		return
	}
	if len(sourceList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM source WHERE id=?", sourceId)
	return
}

func SourceUpdate(sourceId string, param *models.SourceTable) (err error) {
	var sourceList []*models.SourceTable
	err = x.SQL("SELECT id FROM source WHERE id=?", sourceId).Find(&sourceList)
	if err != nil {
		log.Logger.Error("Try to query source fail", log.String("sourceId", sourceId), log.Error(err))
		return
	}
	if len(sourceList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE source SET name=?,plugin=?,provider=?,resource_asset_id_attribute=?,action=?,update_time=?,update_user=? WHERE id=?",
		param.Name, param.Plugin, param.Provider, param.ResourceAssetIdAttribute, param.Action, updateTime, param.UpdateUser, sourceId)
	return
}

func SourceBatchCreate(user string, param []*models.SourceTable) (rowData []*models.SourceTable, err error) {
	actions := []*execAction{}
	tableName := "source"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.SourceTable{Id: id, Name: param[i].Name, Plugin: param[i].Plugin, Provider: param[i].Provider,
			ResourceAssetIdAttribute: param[i].ResourceAssetIdAttribute, Action: param[i].Action, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create source fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create source fail,%s ", err.Error())
	}
	return
}

func SourceBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "source"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete source fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete source fail,%s ", err.Error())
	}
	return
}

func SourceBatchUpdate(user string, param []*models.SourceTable) (err error) {
	actions := []*execAction{}
	tableName := "source"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update source fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update source fail,%s ", err.Error())
	}
	return
}
