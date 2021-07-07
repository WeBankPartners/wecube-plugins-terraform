package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func TfArgumentCreate(param *models.TfArgumentTable) (rowData *models.TfArgumentTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO tf_argument(id,name,source,parameter,tfstate_attribute,default_value,is_null,type,is_multi,convert_way,relative_parameter,relative_value,create_user,create_time) VALUE (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
		id, param.Name, param.Source, param.Parameter, param.TfstateAttribute, param.DefaultValue, param.IsNull, param.Type, param.IsMulti, param.ConvertWay, param.RelativeParameter, param.RelativeValue, param.CreateUser, createTime)

	rowData = &models.TfArgumentTable{Id: id, Name: param.Name, Source: param.Source, Parameter: param.Parameter, TfstateAttribute: param.TfstateAttribute,
		DefaultValue: param.DefaultValue, IsNull: param.IsNull, Type: param.Type, IsMulti: param.IsMulti, ConvertWay: param.ConvertWay, RelativeParameter: param.RelativeParameter, RelativeValue: param.RelativeValue, CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create tfArgument fail,%s ", err.Error())
	}
	return
}

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

func TfArgumentDelete(tfArgumentId string) (err error) {
	var tfArgumentList []*models.TfArgumentTable
	err = x.SQL("SELECT id FROM tf_argument WHERE id=?", tfArgumentId).Find(&tfArgumentList)
	if err != nil {
		log.Logger.Error("Try to query tfArgument fail", log.String("tfArgumentId", tfArgumentId), log.Error(err))
		return
	}
	if len(tfArgumentList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM tf_argument WHERE id=?", tfArgumentId)
	return
}

func TfArgumentUpdate(tfArgumentId string, param *models.TfArgumentTable) (err error) {
	var tfArgumentList []*models.TfArgumentTable
	err = x.SQL("SELECT id FROM tf_argument WHERE id=?", tfArgumentId).Find(&tfArgumentList)
	if err != nil {
		log.Logger.Error("Try to query tfArgument fail", log.String("tfArgumentId", tfArgumentId), log.Error(err))
		return
	}
	if len(tfArgumentList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE tf_argument SET name=?,source=?,parameter=?,tfstate_attribute=?,default_value=?,is_null=?,type=?,is_multi=?,convert_way=?relative_parameter=?,relative_value=?,update_time=?,update_user=? WHERE id=?",
		param.Name, param.Source, param.Parameter, param.TfstateAttribute, param.DefaultValue, param.IsNull, param.Type, param.IsMulti, param.ConvertWay, param.RelativeParameter, param.RelativeValue, updateTime, param.UpdateUser, tfArgumentId)
	return
}

func TfArgumentBatchCreate(user string, param []*models.TfArgumentTable) (rowData []*models.TfArgumentTable, err error) {
	actions := []*execAction{}
	tableName := "tf_argument"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.TfArgumentTable{Id: id, Name: param[i].Name, Source: param[i].Source, Parameter: param[i].Parameter, TfstateAttribute: param[i].TfstateAttribute, DefaultValue: param[i].DefaultValue,
			IsNull: param[i].IsNull, Type: param[i].Type, IsMulti: param[i].IsMulti, ConvertWay: param[i].ConvertWay, RelativeParameter: param[i].RelativeParameter, RelativeValue: param[i].RelativeValue, CreateUser: user,
			CreateTime: createTime, UpdateTime: createTime}
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
