package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func ParameterList(paramsMap map[string]interface{}) (rowData []*models.ParameterQuery, err error) {
	// sqlCmd := "SELECT * FROM parameter WHERE 1=1"
	// paramArgs := []interface{}{}
	//for k, v := range paramsMap {
	//	sqlCmd += " AND " + k + "=?"
	//	paramArgs = append(paramArgs, v)
	//}
	//sqlCmd += " ORDER BY create_time DESC"

	sqlCmd := "SELECT t1.*, t2.name AS object_name_title FROM parameter t1 LEFT JOIN parameter t2 ON t1.object_name=t2.id WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + "t1." + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY t1.id DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get parameter list error", log.Error(err))
	}
	return
}

func ParameterBatchCreate(user string, param []*models.ParameterTable) (rowData []*models.ParameterTable, err error) {
	actions := []*execAction{}
	tableName := "parameter"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.ParameterTable{Id: id, Name: param[i].Name, Type: param[i].Type, Multiple: param[i].Multiple,
			Interface: param[i].Interface, Template: param[i].Template, DataType: param[i].DataType, ObjectName: param[i].ObjectName,
			Source: models.ParameterSourceDefault, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	// 当 transNullStr 的 key 表示的字段为空时，表示需要将其插入 null
	transNullStr := make(map[string]string)
	transNullStr["template"] = "true"
	transNullStr["object_name"] = "true"

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], transNullStr)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create parameter fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create parameter fail,%s ", err.Error())
	}
	return
}

func ParameterBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "parameter"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete parameter fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete parameter fail,%s ", err.Error())
	}
	return
}

func ParameterBatchUpdate(user string, param []*models.ParameterTable) (err error) {
	actions := []*execAction{}
	tableName := "parameter"
	updateTime := time.Now().Format(models.DateTimeFormat)

	// 当 transNullStr 的 key 表示的字段为空时，表示需要将其插入 null
	transNullStr := make(map[string]string)
	transNullStr["template"] = "true"
	transNullStr["object_name"] = "true"
	transNullStr["source"] = "true"

	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], transNullStr)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update parameter fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update parameter fail,%s ", err.Error())
	}
	return
}

func ParameterBatchCreateUpdate(user string, param []*models.ParameterTable) (rowData []*models.ParameterTable, err error) {
	actions := []*execAction{}
	tableName := "parameter"
	createTime := time.Now().Format(models.DateTimeFormat)
	updateDataIds := make(map[string]bool)
	var parameterId string

	for i := range param {
		var data *models.ParameterTable
		if param[i].Id == "" {
			parameterId = guid.CreateGuid()
			data = &models.ParameterTable{Id: parameterId, Name: param[i].Name, Type: param[i].Type, Multiple: param[i].Multiple, Interface: param[i].Interface, Template: param[i].Template, DataType: param[i].DataType, ObjectName: param[i].ObjectName, Source: models.ParameterSourceDefault, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
		} else {
			updateDataIds[param[i].Id] = true
			parameterId = param[i].Id
			data = &models.ParameterTable{Id: parameterId, Name: param[i].Name, Type: param[i].Type, Multiple: param[i].Multiple, Interface: param[i].Interface, Template: param[i].Template, DataType: param[i].DataType, ObjectName: param[i].ObjectName, CreateUser: param[i].CreateUser, CreateTime: param[i].CreateTime, UpdateUser: user, UpdateTime: createTime}
		}
		rowData = append(rowData, data)
	}

	// 当 transNullStr 的 key 表示的字段为空时，表示需要将其插入 null
	transNullStr := make(map[string]string)
	transNullStr["template"] = "true"
	transNullStr["object_name"] = "true"

	var tmpErr error
	for i := range rowData {
		var action *execAction
		if _, ok := updateDataIds[rowData[i].Id]; ok {
			action, tmpErr = GetUpdateTableExecAction(tableName, "id", rowData[i].Id, *rowData[i], transNullStr)
			if tmpErr != nil {
				err = fmt.Errorf("Try to get update_parameter execAction fail,%s ", tmpErr.Error())
				return
			}
		} else {
			action, tmpErr = GetInsertTableExecAction(tableName, *rowData[i], transNullStr)
			if tmpErr != nil {
				err = fmt.Errorf("Try to get create_parameter execAction fail,%s ", tmpErr.Error())
				return
			}
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create or update parameter fail,%s ", err.Error())
	}
	return
}