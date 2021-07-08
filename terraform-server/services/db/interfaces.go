package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func InterfaceCreate(param *models.InterfaceTable) (rowData *models.InterfaceTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO interface(id,name,plugin,description,create_time,create_user) VALUE (?,?,?,?,?,?)",
		id, param.Name, param.Plugin, param.Description, createTime, param.CreateUser)

	rowData = &models.InterfaceTable{Id: id, Name: param.Name, Plugin: param.Plugin, Description: param.Description,
		CreateTime: createTime, CreateUser: param.CreateUser}

	if err != nil {
		err = fmt.Errorf("Try to create interface fail,%s ", err.Error())
	}
	return
}

func InterfaceList(paramsMap map[string]interface{}) (rowData []*models.InterfaceTable, err error) {
	sqlCmd := "SELECT * FROM interface WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get interface list error", log.Error(err))
	}
	return
}

func InterfaceDelete(interfaceId string) (err error) {
	var interfaceList []*models.InterfaceTable
	err = x.SQL("SELECT id FROM interface WHERE id=?", interfaceId).Find(&interfaceList)
	if err != nil {
		log.Logger.Error("Try to query interface fail", log.String("interfaceId", interfaceId), log.Error(err))
		return
	}
	if len(interfaceList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM interface WHERE id=?", interfaceId)
	return
}

func InterfaceUpdate(interfaceId string, param *models.InterfaceTable) (err error) {
	var interfaceList []*models.InterfaceTable
	err = x.SQL("SELECT id FROM interface WHERE id=?", interfaceId).Find(&interfaceList)
	if err != nil {
		log.Logger.Error("Try to query interface fail", log.String("interfaceId", interfaceId), log.Error(err))
		return
	}
	if len(interfaceList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE interface SET name=?,plugin=?,description=?,update_time=?,update_user=? WHERE id=?",
		param.Name, param.Plugin, param.Description, updateTime, param.UpdateUser, interfaceId)
	return
}

func InterfaceBatchCreate(user string, param []*models.InterfaceTable) (rowData []*models.InterfaceTable, err error) {
	actions := []*execAction{}
	tableName := "interface"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.InterfaceTable{Id: id, Name: param[i].Name, Plugin: param[i].Plugin, Description: param[i].Description,
			CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create interface fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create interface fail,%s ", err.Error())
	}
	return
}

func InterfaceBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "interface"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete interface fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete interface fail,%s ", err.Error())
	}
	return
}

func InterfaceBatchUpdate(user string, param []*models.InterfaceTable) (err error) {
	actions := []*execAction{}
	tableName := "interface"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update interface fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update interface fail,%s ", err.Error())
	}
	return
}