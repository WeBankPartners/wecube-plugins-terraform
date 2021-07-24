package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func TfstateAttributeList(paramsMap map[string]interface{}) (rowData []*models.TfstateAttributeQuery, err error) {
	/*
	sqlCmd := "SELECT * FROM tfstate_attribute WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	 */
	sqlCmd := "SELECT t1.*,t2.name AS object_name_title,t3.name AS source_title,t4.name AS parameter_title,t5.name AS " +
		"relative_source_title,t6.name AS relative_tfstate_attribute_title,t7.name AS relative_parameter_title FROM tfstate_attribute " +
		"t1 LEFT JOIN tfstate_attribute t2 ON t1.object_name=t2.id LEFT JOIN source t3 ON t3.id=t1.source LEFT JOIN parameter t4 " +
		"ON t4.id=t1.parameter LEFT JOIN source t5 ON t5.id=t1.relative_source LEFT JOIN tfstate_attribute t6 ON t6.id=t1.relative_tfstate_attribute " +
		"LEFT JOIN parameter t7 ON t7.id=t1.relative_parameter WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + "t1." + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY t1.id DESC"
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
	transNullStr["source"] = "true"
	transNullStr["parameter"] = "true"

	for i := range param {
		id := guid.CreateGuid()
		data := &models.TfstateAttributeTable{Id: id, Name: param[i].Name, Source: param[i].Source, Parameter: param[i].Parameter, DefaultValue: param[i].DefaultValue, IsNull: param[i].IsNull, Type: param[i].Type, ObjectName: param[i].ObjectName,
			IsMulti: param[i].IsMulti, ConvertWay: param[i].ConvertWay, RelativeSource: param[i].RelativeSource, RelativeTfstateAttribute: param[i].RelativeTfstateAttribute, RelativeParameter: param[i].RelativeParameter,
			RelativeParameterValue: param[i].RelativeParameterValue, FunctionDefine: param[i].FunctionDefine, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
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
	transNullStr["source"] = "true"
	transNullStr["parameter"] = "true"

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
				RelativeTfstateAttribute: param[i].RelativeTfstateAttribute, RelativeParameter: param[i].RelativeParameter, RelativeParameterValue: param[i].RelativeParameterValue,
				FunctionDefine: param[i].FunctionDefine, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
		} else {
			updateDataIds[param[i].Id] = true
			parameterId = param[i].Id
			data = &models.TfstateAttributeTable{Id: parameterId, Name: param[i].Name, Source: param[i].Source, Parameter: param[i].Parameter, DefaultValue: param[i].DefaultValue,
				IsNull: param[i].IsNull, Type: param[i].Type, ObjectName: param[i].ObjectName, IsMulti: param[i].IsMulti, ConvertWay: param[i].ConvertWay, RelativeSource: param[i].RelativeSource,
				RelativeTfstateAttribute: param[i].RelativeTfstateAttribute, RelativeParameter: param[i].RelativeParameter, RelativeParameterValue: param[i].RelativeParameterValue, FunctionDefine: param[i].FunctionDefine, CreateUser: param[i].CreateUser, CreateTime: param[i].CreateTime, UpdateUser: user, UpdateTime: createTime}
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
	transNullStr["source"] = "true"
	transNullStr["parameter"] = "true"

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
