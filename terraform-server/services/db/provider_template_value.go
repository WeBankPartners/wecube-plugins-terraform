package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func ProviderTemplateValueCreate(param *models.ProviderTemplateValueTable) (rowData *models.ProviderTemplateValueTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO provider_template_value(id,value,provider,template_value,create_user,create_time) VALUE (?,?,?,?,?,?)",
		id, param.Value, param.Provider, param.TemplateValue, param.CreateUser, createTime)

	rowData = &models.ProviderTemplateValueTable{Id: id, Value: param.Value, Provider: param.Provider, TemplateValue: param.TemplateValue, CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create providerTemplateValue fail,%s ", err.Error())
	}
	return
}

func ProviderTemplateValueList(paramsMap map[string]interface{}) (rowData []*models.ProviderTemplateValueTable, err error) {
	sqlCmd := "SELECT * FROM provider_template_value WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get providerTemplateValue list error", log.Error(err))
	}
	return
}

func ProviderTemplateValueDelete(providerTemplateValueId string) (err error) {
	var providerTemplateValueList []*models.ProviderTemplateValueTable
	err = x.SQL("SELECT id FROM provider_template_value WHERE id=?", providerTemplateValueId).Find(&providerTemplateValueList)
	if err != nil {
		log.Logger.Error("Try to query providerTemplateValue fail", log.String("providerTemplateValueId", providerTemplateValueId), log.Error(err))
		return
	}
	if len(providerTemplateValueList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM provider_template_value WHERE id=?", providerTemplateValueId)
	return
}

func ProviderTemplateValueUpdate(providerTemplateValueId string, param *models.ProviderTemplateValueTable) (err error) {
	var providerTemplateValueList []*models.ProviderTemplateValueTable
	err = x.SQL("SELECT id FROM provider_template_value WHERE id=?", providerTemplateValueId).Find(&providerTemplateValueList)
	if err != nil {
		log.Logger.Error("Try to query providerTemplateValue fail", log.String("providerTemplateValueId", providerTemplateValueId), log.Error(err))
		return
	}
	if len(providerTemplateValueList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE provider_template_value SET value=?,provider=?,template_value=?,update_time=?,update_user=? WHERE id=?",
		param.Value, param.Provider, param.TemplateValue, updateTime, param.UpdateUser, providerTemplateValueId)
	return
}

func ProviderTemplateValueBatchCreate(user string, param []*models.ProviderTemplateValueTable) (rowData []*models.ProviderTemplateValueTable, err error) {
	actions := []*execAction{}
	tableName := "provider_template_value"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.ProviderTemplateValueTable{Id: id, Value: param[i].Value, Provider: param[i].Provider, TemplateValue: param[i].TemplateValue, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create provider_template_value fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create provider_template_value fail,%s ", err.Error())
	}
	return
}

func ProviderTemplateValueBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "provider_template_value"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete provider_template_value fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete provider_template_value fail,%s ", err.Error())
	}
	return
}

func ProviderTemplateValueBatchUpdate(user string, param []*models.ProviderTemplateValueTable) (err error) {
	actions := []*execAction{}
	tableName := "provider_template_value"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update provider_template_value fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update provider_template_value fail,%s ", err.Error())
	}
	return
}

func ProviderTemplateValueListByTemplate(templateName string) (rowData []*models.ProviderTemplateValueTable, err error) {
	sqlCmd := "SELECT * FROM provider_template_value t1 LEFT JOIN template_value t2 on t1.template_value=t2.id LEFT JOIN template t3 on " +
		"t2.template=t3.name WHERE t3.name=? ORDER BY t1.create_time DESC"
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, templateName)
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get provider_template_value list by template error", log.String("template", templateName), log.Error(err))
	}
	return
}