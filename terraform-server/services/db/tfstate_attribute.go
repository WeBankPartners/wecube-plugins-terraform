package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func TfstateAttributeCreate(param *models.TfstateAttributeTable) (rowData *models.TfstateAttributeTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO tfstate_attribute(id,name,source,parameter,default_value,is_null,type,is_multi,convert_way,relative_parameter,relative_value,create_user,create_time) VALUE (?,?,?,?,?,?,?,?,?,?,?,?,?)",
		id, param.Name, param.Source, param.Parameter, param.DefaultValue, param.IsNull, param.Type, param.IsMulti, param.ConvertWay, param.RelativeParameter, param.RelativeValue, param.CreateUser, createTime)

	rowData = &models.TfstateAttributeTable{Id: id, Name: param.Name, Source: param.Source, Parameter: param.Parameter, DefaultValue: param.DefaultValue,
		IsNull: param.IsNull, Type: param.Type, IsMulti: param.IsMulti, ConvertWay: param.ConvertWay, RelativeParameter: param.RelativeParameter, RelativeValue: param.RelativeValue, CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create tfstateAttribute fail,%s ", err.Error())
	}
	return
}

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

func TfstateAttributeDelete(tfstateAttributeId string) (err error) {
	var tfstateAttributeList []*models.TfstateAttributeTable
	err = x.SQL("SELECT id FROM tfstate_attribute WHERE id=?", tfstateAttributeId).Find(&tfstateAttributeList)
	if err != nil {
		log.Logger.Error("Try to query tfstateAttribute fail", log.String("tfstateAttributeId", tfstateAttributeId), log.Error(err))
		return
	}
	if len(tfstateAttributeList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM tfstate_attribute WHERE id=?", tfstateAttributeId)
	return
}

func TfstateAttributeUpdate(tfstateAttributeId string, param *models.TfstateAttributeTable) (err error) {
	var tfstateAttributeList []*models.TfstateAttributeTable
	err = x.SQL("SELECT id FROM tfstate_attribute WHERE id=?", tfstateAttributeId).Find(&tfstateAttributeList)
	if err != nil {
		log.Logger.Error("Try to query tfstateAttribute fail", log.String("tfstateAttributeId", tfstateAttributeId), log.Error(err))
		return
	}
	if len(tfstateAttributeList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE tfstate_attribute SET name=?,source=?,parameter=?,default_value=?,is_null=?,type=?,is_multi=?,convert_way=?relative_parameter=?,relative_value=?,update_time=?,update_user=? WHERE id=?",
		param.Name, param.Source, param.Parameter, param.DefaultValue, param.IsNull, param.Type, param.IsMulti, param.ConvertWay, param.RelativeParameter, param.RelativeValue, updateTime, param.UpdateUser, tfstateAttributeId)
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
