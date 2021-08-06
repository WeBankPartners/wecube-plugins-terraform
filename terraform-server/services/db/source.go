package db

import (
	"fmt"
	"strings"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func SourceList(paramsMap map[string]interface{}) (rowData []*models.SourceTable, err error) {
	sqlCmd := "SELECT * FROM source WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get source list error", log.Error(err))
	}
	return
}

func SourceBatchCreate(user string, param []*models.SourceTable) (rowData []*models.SourceTable, err error) {
	actions := []*execAction{}
	tableName := "source"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.SourceTable{Id: id, Interface: param[i].Interface, Provider: param[i].Provider, Name: param[i].Name,
			AssetIdAttribute: param[i].AssetIdAttribute, TerraformUsed: param[i].TerraformUsed, CreateUser: user, CreateTime: createTime,
			UpdateUser: user, UpdateTime: createTime, ImportPrefix: param[i].ImportPrefix, ImportSupport: param[i].ImportSupport,
			SourceType: param[i].SourceType, Remark: param[i].Remark}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create source fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create source fail,%s ", err.Error())
	}
	return
}

func SourceBatchDelete(ids []string) (err error) {
	actions := []*execAction{}

	// get the tfArgument by source id
	sourceidsStr := strings.Join(ids, "','")
	sqlCmd := "SELECT * FROM tf_argument WHERE source IN ('" + sourceidsStr + "')" + "ORDER BY object_name DESC"
	var tfArgumentList []*models.TfArgumentTable
	err = x.SQL(sqlCmd).Find(&tfArgumentList)
	if err != nil {
		log.Logger.Error("Get tfArgument list error", log.Error(err))
	}
	tableName := "tf_argument"
	for i := range tfArgumentList {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", tfArgumentList[i].Id)
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete tfArgument fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	// get the tfstateAttribute by source id
	sqlCmd = "SELECT * FROM tfstate_attribute WHERE source IN ('" + sourceidsStr + "')" + "ORDER BY object_name DESC"
	var tfstateAttributeList []*models.TfstateAttributeTable
	err = x.SQL(sqlCmd).Find(&tfstateAttributeList)
	if err != nil {
		log.Logger.Error("Get tfstateAttribute list error", log.Error(err))
	}
	tableName = "tfstate_attribute"
	for i := range tfstateAttributeList {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", tfstateAttributeList[i].Id)
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete tfstateAttribute fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	tableName = "source"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete source fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete source fail,%s ", err.Error())
	}
	return
}

func SourceBatchUpdate(user string, param []*models.SourceTable) (err error) {
	actions := []*execAction{}
	tableName := "source"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update source fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update source fail,%s ", err.Error())
	}
	return
}
