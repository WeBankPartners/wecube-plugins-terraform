package db

import (
	"fmt"
	"strings"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func TemplateValueList(paramsMap map[string]interface{}) (rowData []*models.TemplateValueTable, err error) {
	sqlCmd := "SELECT * FROM template_value WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get template_value list error", log.Error(err))
	}
	return
}

func TemplateValueBatchCreate(user string, param []*models.TemplateValueTable) (rowData []*models.TemplateValueTable, err error) {
	actions := []*execAction{}
	tableName := "template_value"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.TemplateValueTable{Id: id, Value: param[i].Value, Template: param[i].Template, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create template_value fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create template_value fail,%s ", err.Error())
	}
	return
}

func TemplateValueBatchDelete(ids []string) (err error) {
	actions := []*execAction{}

	// find all providerTemplateValue by templateValueId
	templateValueIdsStr := strings.Join(ids, "','")
	sqlCmd := "SELECT id FROM provider_template_value WHERE template_value IN ('" + templateValueIdsStr + "')"
	providerTemplateValueList, err := x.QueryString(sqlCmd)
	if err != nil {
		log.Logger.Error("Try to query provider_template_value list by template_value fail", log.String("templateValueIds", templateValueIdsStr), log.Error(err))
		return
	}

	tableName := "provider_template_value"
	for i := range providerTemplateValueList {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", providerTemplateValueList[i]["id"])
		if tmpErr != nil {
			err = fmt.Errorf("Try to get delete provider_template_value execAction fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	tableName = "template_value"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to get delete template_value execAction fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete template_value fail,%s ", err.Error())
	}
	return
}

func TemplateValueBatchUpdate(user string, param []*models.TemplateValueTable) (err error) {
	actions := []*execAction{}
	tableName := "template_value"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update template_value fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update template_value fail,%s ", err.Error())
	}
	return
}

func TemplateValueListByParameter(parameterId string) (rowData []*models.TemplateValueTable, err error) {
	sqlCmd := "SELECT t1.* FROM template_value t1 LEFT JOIN template t2 on t1.template=t2.name LEFT JOIN parameter t3 on " +
		"t2.name=t3.template WHERE t3.id=? ORDER BY t1.create_time DESC"
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, parameterId)
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get template_value by parameter list error", log.String("parameter", parameterId), log.Error(err))
	}
	return
}