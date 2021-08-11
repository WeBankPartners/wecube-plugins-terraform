package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

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

func ProviderTemplateValueBatchCreate(user string, param []*models.ProviderTemplateValueTable) (rowData []*models.ProviderTemplateValueTable, err error) {
	actions := []*execAction{}
	tableName := "provider_template_value"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.ProviderTemplateValueTable{Id: id, Value: param[i].Value, Provider: param[i].Provider, TemplateValue: param[i].TemplateValue, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
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

func ProviderTemplateValueListByTemplate(templateId string) (rowData []*models.TemplateValueQuery, err error) {
	sqlCmd := "SELECT * FROM template_value WHERE template=? ORDER BY id DESC"
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, templateId)
	var templateValueList []*models.TemplateValueQuery
	err = x.SQL(sqlCmd, paramArgs...).Find(&templateValueList)
	if err != nil {
		log.Logger.Error("Get template_value list by template error", log.String("template", templateId), log.Error(err))
		return
	}
	if len(templateValueList) == 0 {
		log.Logger.Warn("template_value list can not be found by template", log.String("template", templateId))
		return
	}

	m := make(map[string]*models.TemplateValueQuery)
	for i := range templateValueList {
		templateValueList[i].ProviderTemplateValueInfo = make(map[string]map[string]string)
		m[templateValueList[i].Id] = templateValueList[i]
	}

	sqlCmd = "SELECT t1.id AS providerTemplateValueId,t1.value AS providerTemplateValue,t4.name AS provider,t1.create_time AS providerTemplateValueCreateTime,t1.create_user AS providerTemplateValueCreateUser,t2.id " +
		"AS templateValueId,t2.value AS templateValue,t2.template AS templateId FROM provider_template_value t1 LEFT " +
		"JOIN template_value t2 on t1.template_value=t2.id LEFT JOIN template t3 on t2.template=t3.id LEFT JOIN provider t4 on t4.id=t1.provider WHERE t3.id=? ORDER BY t2.id DESC"
	sqlOrArgs := []interface{}{sqlCmd, templateId}
	providerTemplateValueList, err := x.QueryString(sqlOrArgs...)
	if err != nil {
		log.Logger.Error("Get provider_template_value list by template error", log.String("template", templateId), log.Error(err))
		return
	}
	for _, ptv := range providerTemplateValueList {
		templateValueInfo := m[ptv["templateValueId"]]
		if _, ok := templateValueInfo.ProviderTemplateValueInfo[ptv["provider"]]; !ok {
			templateValueInfo.ProviderTemplateValueInfo[ptv["provider"]] = make(map[string]string)
		}
		templateValueInfo.ProviderTemplateValueInfo[ptv["provider"]]["id"] = ptv["providerTemplateValueId"]
		templateValueInfo.ProviderTemplateValueInfo[ptv["provider"]]["value"] = ptv["providerTemplateValue"]
		templateValueInfo.ProviderTemplateValueInfo[ptv["provider"]]["createTime"] = ptv["providerTemplateValueCreateTime"]
		templateValueInfo.ProviderTemplateValueInfo[ptv["provider"]]["createUser"] = ptv["providerTemplateValueCreateUser"]
	}
	rowData = templateValueList
	return
}

func ProviderTemplateValueBatchCreateUpdate(user string, param []*models.ProviderTemplateValueTable) (rowData []*models.ProviderTemplateValueTable, err error) {
	actions := []*execAction{}
	tableName := "provider_template_value"
	createTime := time.Now().Format(models.DateTimeFormat)
	updateDataIds := make(map[string]bool)
	var providerTemplateValueId string
	for i := range param {
		var data *models.ProviderTemplateValueTable
		if param[i].Id == "" {
			providerTemplateValueId = guid.CreateGuid()
			data = &models.ProviderTemplateValueTable{Id: providerTemplateValueId, Value: param[i].Value, Provider: param[i].Provider, TemplateValue: param[i].TemplateValue, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
		} else {
			updateDataIds[param[i].Id] = true
			providerTemplateValueId = param[i].Id
			data = &models.ProviderTemplateValueTable{Id: providerTemplateValueId, Value: param[i].Value, Provider: param[i].Provider, TemplateValue: param[i].TemplateValue, CreateUser: param[i].CreateUser, CreateTime: param[i].CreateTime, UpdateUser: user, UpdateTime: createTime}
		}
		rowData = append(rowData, data)
	}

	var tmpErr error
	for i := range rowData {
		var action *execAction
		if _, ok := updateDataIds[rowData[i].Id]; ok {
			action, tmpErr = GetUpdateTableExecAction(tableName, "id", rowData[i].Id, *rowData[i], nil)
			if tmpErr != nil {
				err = fmt.Errorf("Try to get update_provider_template_value execAction fail,%s ", tmpErr.Error())
				return
			}
		} else {
			action, tmpErr = GetInsertTableExecAction(tableName, *rowData[i], nil)
			if tmpErr != nil {
				err = fmt.Errorf("Try to get create_provider_template_value execAction fail,%s ", tmpErr.Error())
				return
			}
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create or update provider_template_value fail,%s ", err.Error())
	}
	return
}