package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func TfArgumentList(paramsMap map[string]interface{}) (rowData []*models.TfArgumentTable, err error) {
	sqlCmd := "SELECT * FROM tf_argument WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get tfArgument list error", log.Error(err))
	}
	return
}

func TfArgumentBatchCreate(user string, param []*models.TfArgumentTable) (rowData []*models.TfArgumentTable, err error) {
	actions := []*execAction{}
	tableName := "tf_argument"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.TfArgumentTable{Id: id, Name: param[i].Name, Source: param[i].Source, Parameter: param[i].Parameter, DefaultValue: param[i].DefaultValue,
			IsNull: param[i].IsNull, Type: param[i].Type, IsMulti: param[i].IsMulti, ConvertWay: param[i].ConvertWay, RelativeSource: param[i].RelativeSource,
			RelativeTfstateAttribute: param[i].RelativeTfstateAttribute, RelativeParameter: param[i].RelativeParameter, RelativeParameterValue: param[i].RelativeParameterValue, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	// 当 transNullStr 的 key 表示的字段为空时，表示需要将其插入 null
	transNullStr := make(map[string]string)
	transNullStr["tfstate_attribute"] = "true"

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], transNullStr)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create tf_argument fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create tf_argument fail,%s ", err.Error())
	}
	return
}

func TfArgumentBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "tf_argument"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete tf_argument fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete tf_argument fail,%s ", err.Error())
	}
	return
}

func TfArgumentBatchUpdate(user string, param []*models.TfArgumentTable) (err error) {
	actions := []*execAction{}
	tableName := "tf_argument"
	updateTime := time.Now().Format(models.DateTimeFormat)

	// 当 transNullStr 的 key 表示的字段为空时，表示需要将其插入 null
	transNullStr := make(map[string]string)
	transNullStr["tfstate_attribute"] = "true"

	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], transNullStr)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update tf_argument fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update tf_argument fail,%s ", err.Error())
	}
	return
}
