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

	for i := range param {
		id := guid.CreateGuid()
		data := &models.TfstateAttributeTable{Id: id, Name: param[i].Name, Source: param[i].Source, Parameter: param[i].Parameter, DefaultValue: param[i].DefaultValue, IsNull: param[i].IsNull, Type: param[i].Type,
			IsMulti: param[i].IsMulti, ConvertWay: param[i].ConvertWay, RelativeParameter: param[i].RelativeParameter, RelativeValue: param[i].RelativeValue, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
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
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
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
