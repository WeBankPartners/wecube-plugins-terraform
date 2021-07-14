package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func TfstateAttributeList(paramsMap map[string]interface{}) (rowData []*models.TfstateAttributeTable, err error) {
	sqlCmd := "SELECT * FROM tfstate_attribute WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get tfstateAttribute list error", log.Error(err))
	}
	return
}

func TfstateAttributeBatchCreate(user string, param []*models.TfstateAttributeTable) (rowData []*models.TfstateAttributeTable, err error) {
	actions := []*execAction{}
	tableName := "tfstate_attribute"
	createTime := time.Now().Format(models.DateTimeFormat)

	// 当 transNullStr 的 key 表示的字段为空时，表示需要将其插入 null
	transNullStr := make(map[string]string)
	transNullStr["default_value"] = "true"
	transNullStr["object_name"] = "true"
	transNullStr["relative_source"] = "true"
	transNullStr["relative_tfstate_attribute"] = "true"
	transNullStr["relative_parameter"] = "true"
	transNullStr["relative_parameter_value"] = "true"

	for i := range param {
		id := guid.CreateGuid()
		data := &models.TfstateAttributeTable{Id: id, Name: param[i].Name, Source: param[i].Source, Parameter: param[i].Parameter, DefaultValue: param[i].DefaultValue, IsNull: param[i].IsNull, Type: param[i].Type, ObjectName: param[i].ObjectName,
			IsMulti: param[i].IsMulti, ConvertWay: param[i].ConvertWay, RelativeSource: param[i].RelativeSource, RelativeTfstateAttribute: param[i].RelativeTfstateAttribute, RelativeParameter: param[i].RelativeParameter,
			RelativeParameterValue: param[i].RelativeParameterValue, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], transNullStr)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create tfstate_attribute fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create tfstate_attribute fail,%s ", err.Error())
	}
	return
}

func TfstateAttributeBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "tfstate_attribute"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete tfstate_attribute fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete tfstate_attribute fail,%s ", err.Error())
	}
	return
}

func TfstateAttributeBatchUpdate(user string, param []*models.TfstateAttributeTable) (err error) {
	actions := []*execAction{}
	tableName := "tfstate_attribute"
	updateTime := time.Now().Format(models.DateTimeFormat)

	// 当 transNullStr 的 key 表示的字段为空时，表示需要将其插入 null
	transNullStr := make(map[string]string)
	transNullStr["default_value"] = "true"
	transNullStr["object_name"] = "true"
	transNullStr["relative_source"] = "true"
	transNullStr["relative_tfstate_attribute"] = "true"
	transNullStr["relative_parameter"] = "true"
	transNullStr["relative_parameter_value"] = "true"

	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], transNullStr)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update tfstate_attribute fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update tfstate_attribute fail,%s ", err.Error())
	}
	return
}

func TfstateAttributeBatchCreateUpdate(user string, param []*models.TfstateAttributeTable) (rowData []*models.TfstateAttributeTable, err error) {
	actions := []*execAction{}
	tableName := "tfstate_attribute"
	createTime := time.Now().Format(models.DateTimeFormat)
	updateDataIds := make(map[string]bool)
	var parameterId string

	for i := range param {
		var data *models.TfstateAttributeTable
		if param[i].Id == "" {
			parameterId = guid.CreateGuid()
			data = &models.TfstateAttributeTable{Id: parameterId, Name: param[i].Name, Source: param[i].Source, Parameter: param[i].Parameter, DefaultValue: param[i].DefaultValue,
				IsNull: param[i].IsNull, Type: param[i].Type, ObjectName: param[i].ObjectName, IsMulti: param[i].IsMulti, ConvertWay: param[i].ConvertWay, RelativeSource: param[i].RelativeSource,
				RelativeTfstateAttribute: param[i].RelativeTfstateAttribute, RelativeParameter: param[i].RelativeParameter, RelativeParameterValue: param[i].RelativeParameterValue, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		} else {
			updateDataIds[param[i].Id] = true
			parameterId = param[i].Id
			data = &models.TfstateAttributeTable{Id: parameterId, Name: param[i].Name, Source: param[i].Source, Parameter: param[i].Parameter, DefaultValue: param[i].DefaultValue,
				IsNull: param[i].IsNull, Type: param[i].Type, ObjectName: param[i].ObjectName, IsMulti: param[i].IsMulti, ConvertWay: param[i].ConvertWay, RelativeSource: param[i].RelativeSource,
				RelativeTfstateAttribute: param[i].RelativeTfstateAttribute, RelativeParameter: param[i].RelativeParameter, RelativeParameterValue: param[i].RelativeParameterValue, CreateUser: param[i].CreateUser, CreateTime: param[i].CreateTime, UpdateUser: user, UpdateTime: createTime}
		}
		rowData = append(rowData, data)
	}

	// 当 transNullStr 的 key 表示的字段为空时，表示需要将其插入 null
	transNullStr := make(map[string]string)
	transNullStr["default_value"] = "true"
	transNullStr["object_name"] = "true"
	transNullStr["relative_source"] = "true"
	transNullStr["relative_tfstate_attribute"] = "true"
	transNullStr["relative_parameter"] = "true"
	transNullStr["relative_parameter_value"] = "true"

	var tmpErr error
	for i := range rowData {
		var action *execAction
		if _, ok := updateDataIds[rowData[i].Id]; ok {
			action, tmpErr = GetUpdateTableExecAction(tableName, "id", rowData[i].Id, *rowData[i], transNullStr)
			if tmpErr != nil {
				err = fmt.Errorf("Try to get update_tfstate_attribute execAction fail,%s ", tmpErr.Error())
				return
			}
		} else {
			action, tmpErr = GetInsertTableExecAction(tableName, *rowData[i], transNullStr)
			if tmpErr != nil {
				err = fmt.Errorf("Try to create_tfstate_attribute execAction fail,%s ", tmpErr.Error())
				return
			}
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create or update tfstate_attribute fail,%s ", err.Error())
	}
	return
}
