package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func TemplateList(paramsMap map[string]interface{}) (rowData []*models.TemplateTable, err error) {
	sqlCmd := "SELECT * FROM template WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get template list error", log.Error(err))
	}
	return
}

func TemplateBatchCreate(user string, param []*models.TemplateTable) (rowData []*models.TemplateTable, err error) {
	actions := []*execAction{}
	tableName := "template"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.TemplateTable{Id: id, Name: param[i].Name, Description: param[i].Description, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create template fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create template fail,%s ", err.Error())
	}
	return
}

func TemplateBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "template"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete template fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete template fail,%s ", err.Error())
	}
	return
}

func TemplateBatchUpdate(user string, param []*models.TemplateTable) (err error) {
	actions := []*execAction{}
	tableName := "template"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update template fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update template fail,%s ", err.Error())
	}
	return
}

func TemplateListByPlugin(pluginId string) (rowData []*models.TemplateTable, err error) {
	sqlCmd := "SELECT t1.* FROM template t1 LEFT JOIN parameter t2 on t1.id=t2.template LEFT JOIN interface t3 on " +
		"t2.interface=t3.id LEFT JOIN plugin t4 on t3.plugin=t4.id WHERE t4.id=? GROUP BY t1.id ORDER BY t1.id DESC"
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, pluginId)
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get template by plugin list error", log.String("plugin", pluginId), log.Error(err))
	}
	return
}