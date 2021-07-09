package db

import (
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func TemplateCreate(param *models.TemplateTable) (rowData *models.TemplateTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO template(id,name,description,create_user,create_time) VALUE (?,?,?,?,?)",
		id, param.Name, param.Description, param.CreateUser, createTime)

	rowData = &models.TemplateTable{Id: id, Name: param.Name, Description: param.Description,
		CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create template fail,%s ", err.Error())
	}
	return
}

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

func TemplateDelete(templateId string) (err error) {
	var templateList []*models.TemplateTable
	err = x.SQL("SELECT id FROM template WHERE id=?", templateId).Find(&templateList)
	if err != nil {
		log.Logger.Error("Try to query template fail", log.String("templateId", templateId), log.Error(err))
		return
	}
	if len(templateList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM template WHERE id=?", templateId)
	return
}

func TemplateUpdate(templateId string, param *models.TemplateTable) (err error) {
	var templateList []*models.TemplateTable
	err = x.SQL("SELECT id FROM template WHERE id=?", templateId).Find(&templateList)
	if err != nil {
		log.Logger.Error("Try to query template fail", log.String("templateId", templateId), log.Error(err))
		return
	}
	if len(templateList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE template SET name=?,description=?,update_time=?,update_user=? WHERE id=?",
		param.Name, param.Description, updateTime, param.UpdateUser, templateId)
	return
}

func TemplateBatchCreate(user string, param []*models.TemplateTable) (rowData []*models.TemplateTable, err error) {
	actions := []*execAction{}
	tableName := "template"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.TemplateTable{Id: id, Name: param[i].Name, Description: param[i].Description, CreateUser: user, CreateTime: createTime, UpdateTime: createTime}
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
	sqlCmd := "SELECT t1.* FROM template t1 LEFT JOIN parameter t2 on t1.name=t2.template LEFT JOIN interface t3 on " +
		"t2.interface=t3.id LEFT JOIN plugin t4 on t3.plugin=t4.name WHERE t4.id=? GROUP BY t1.id ORDER BY t1.create_time DESC"
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, pluginId)
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get template by plugin list error", log.String("plugin", pluginId), log.Error(err))
	}
	return
}