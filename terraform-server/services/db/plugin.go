package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func PluginCreate(param *models.PluginTable) (rowData *models.PluginTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO plugin(id,name,create_user,create_time) VALUE (?,?,?,?)",
		id, param.Name, param.CreateUser, createTime)

	rowData = &models.PluginTable{Id: id, Name: param.Name, CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create plugin fail,%s ", err.Error())
	}
	return
}

func PluginList(paramsMap map[string]interface{}) (rowData []*models.PluginTable, err error) {
	sqlCmd := "SELECT * FROM plugin WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get plugin list error", log.Error(err))
	}
	return
}

func PluginDelete(pluginId string) (err error) {
	var pluginList []*models.PluginTable
	err = x.SQL("SELECT id FROM plugin WHERE id=?", pluginId).Find(&pluginList)
	if err != nil {
		log.Logger.Error("Try to query plugin fail", log.String("pluginId", pluginId), log.Error(err))
		return
	}
	if len(pluginList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM plugin WHERE id=?", pluginId)
	return
}

func PluginUpdate(pluginId string, param *models.PluginTable) (err error) {
	var pluginList []*models.PluginTable
	err = x.SQL("SELECT id FROM plugin WHERE id=?", pluginId).Find(&pluginList)
	if err != nil {
		log.Logger.Error("Try to query plugin fail", log.String("pluginId", pluginId), log.Error(err))
		return
	}
	if len(pluginList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE plugin SET name=?,update_time=?,update_user=? WHERE id=?",
		param.Name, updateTime, param.UpdateUser, pluginId)
	return
}

func PluginBatchCreate(user string, param []*models.PluginTable) (rowData []*models.PluginTable, err error) {
	actions := []*execAction{}
	tableName := "plugin"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.PluginTable{Id: id, Name: param[i].Name, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create plugin fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create plugin fail,%s ", err.Error())
	}
	return
}

func PluginBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "plugin"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete plugin fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete plugin fail,%s ", err.Error())
	}
	return
}

func PluginBatchUpdate(user string, param []*models.PluginTable) (err error) {
	actions := []*execAction{}
	tableName := "plugin"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update plugin fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update plugin fail,%s ", err.Error())
	}
	return
}
