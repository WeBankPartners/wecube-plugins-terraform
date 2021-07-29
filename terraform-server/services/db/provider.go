package db

import (
	"fmt"
	"strings"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func ProviderList(paramsMap map[string]interface{}) (rowData []*models.ProviderTable, err error) {
	sqlCmd := "SELECT * FROM provider WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get provider list error", log.Error(err))
	}
	return
}

func ProviderBatchCreate(user string, param []*models.ProviderTable) (rowData []*models.ProviderTable, err error) {
	actions := []*execAction{}
	tableName := "provider"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.ProviderTable{Id: id, Name: param[i].Name, Version: param[i].Version, SecretIdAttrName: param[i].SecretIdAttrName,
			SecretKeyAttrName: param[i].SecretKeyAttrName, RegionAttrName: param[i].RegionAttrName, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create provider fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create provider fail,%s ", err.Error())
	}
	return
}

func ProviderBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "provider"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete provider fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete provider fail,%s ", err.Error())
	}
	return
}

func ProviderBatchUpdate(user string, param []*models.ProviderTable) (err error) {
	actions := []*execAction{}
	tableName := "provider"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update provider fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update provider fail,%s ", err.Error())
	}
	return
}

func ProviderPluginExport(providerName, pluginName string) (result models.ProviderPluginImportObj, err error) {
	result = models.ProviderPluginImportObj{Provider: []*models.ProviderTable{}, Plugin: []*models.PluginTable{}}
	result.ProviderTemplateValue = []*models.ProviderTemplateValueTable{}
	result.Template = []*models.TemplateTable{}
	result.TemplateValue = []*models.TemplateValueTable{}
	result.Interface = []*models.InterfaceTable{}
	result.Parameter = []*models.ParameterTable{}
	result.Source = []*models.SourceTable{}
	result.TfArgument = []*models.TfArgumentTable{}
	result.TfstateAttribute = []*models.TfstateAttributeTable{}
	err = x.SQL("select * from provider where name=?", providerName).Find(&result.Provider)
	if err != nil {
		err = fmt.Errorf("Query database provider table fail,%s ", err.Error())
		return
	}
	if len(result.Provider) == 0 {
		err = fmt.Errorf("Can not find any provider with name:%s ", providerName)
		return
	}
	providerId := result.Provider[0].Id
	err = x.SQL("select * from plugin where name=?", pluginName).Find(&result.Plugin)
	if err == nil && len(result.Plugin) == 0 {
		err = fmt.Errorf("Can not find any plugin with name:%s ", pluginName)
		return
	}
	pluginId := result.Plugin[0].Id
	x.SQL("select * from interface where plugin=?", pluginId).Find(&result.Interface)
	x.SQL("select * from `parameter` where interface in (select id from interface where plugin=?)", pluginId).Find(&result.Parameter)
	templateSql := "select * from template where id in (select template_value from provider_template_value where provider=?)"
	templateSql += " union "
	templateSql += "select * from template where id in (select template from `parameter` where interface in (select id from interface where plugin=?))"
	x.SQL(templateSql, providerId, pluginId).Find(&result.Template)
	x.SQL("select * from template_value where template in ("+strings.ReplaceAll(templateSql, "*", "id")+")", providerId, pluginId).Find(&result.TemplateValue)
	sourceSql := "select * from source where interface in (select id from interface where plugin=?) and provider=?"
	x.SQL(sourceSql, pluginId, providerId).Find(&result.Source)
	x.SQL("select * from tf_argument where source in ("+strings.ReplaceAll(sourceSql, "*", "id")+")", pluginId, providerId).Find(&result.TfArgument)
	x.SQL("select * from tfstate_attribute where source in ("+strings.ReplaceAll(sourceSql, "*", "id")+")", pluginId, providerId).Find(&result.TfstateAttribute)
	var sourceMap, tfStateAttrMap, parameterMap = make(map[string]bool), make(map[string]bool), make(map[string]bool)
	for _, v := range result.Source {
		sourceMap[v.Id] = true
	}
	for _, v := range result.TfstateAttribute {
		tfStateAttrMap[v.Id] = true
	}
	for _, v := range result.Parameter {
		parameterMap[v.Id] = true
	}
	for i, v := range result.TfArgument {
		if _, b := sourceMap[v.RelativeSource]; !b {
			result.TfArgument[i].RelativeSource = ""
		}
		if _, b := tfStateAttrMap[v.RelativeTfstateAttribute]; !b {
			result.TfArgument[i].RelativeTfstateAttribute = ""
		}
		if _, b := parameterMap[v.RelativeParameter]; !b {
			result.TfArgument[i].RelativeParameter = ""
			result.TfArgument[i].RelativeParameterValue = ""
		}
	}
	for i, v := range result.TfstateAttribute {
		if _, b := sourceMap[v.RelativeSource]; !b {
			result.TfstateAttribute[i].RelativeSource = ""
		}
		if _, b := tfStateAttrMap[v.RelativeTfstateAttribute]; !b {
			result.TfstateAttribute[i].RelativeTfstateAttribute = ""
		}
		if _, b := parameterMap[v.RelativeParameter]; !b {
			result.TfstateAttribute[i].RelativeParameter = ""
			result.TfstateAttribute[i].RelativeParameterValue = ""
		}
	}
	return
}

func ProviderPluginImport(input models.ProviderPluginImportObj, updateUser string) error {
	updateTime := time.Now().Format(models.DateTimeFormat)
	var actions []*execAction
	for _, v := range input.Provider {
		tmpAction := execAction{Sql: "replace into provider(id,name,`version`,secret_id_attr_name,secret_key_attr_name,region_attr_name,Initialized,create_time,create_user,update_time,update_user) values (?,?,?,?,?,?,?,?,?,?,?)"}
		tmpAction.Param = []interface{}{v.Id, v.Name, v.Version, v.SecretIdAttrName, v.SecretKeyAttrName, v.RegionAttrName, v.Initialized, v.CreateTime, v.CreateUser, updateTime, updateUser}
		actions = append(actions, &tmpAction)
	}
	for _, v := range input.Plugin {
		actions = append(actions, &execAction{Sql: "replace into plugin(id,name,create_time,create_user,update_time,update_user) values (?,?,?,?,?,?)", Param: []interface{}{v.Id, v.Name, v.CreateTime, v.CreateUser, updateTime, updateUser}})
	}
	for _, v := range input.Interface {
		actions = append(actions, &execAction{Sql: "replace into interface(id,name,description,plugin,create_time,create_user,update_time,update_user) values (?,?,?,?,?,?,?,?)", Param: []interface{}{v.Id, v.Name, v.Description, v.Plugin, v.CreateTime, v.CreateUser, updateTime, updateUser}})
	}
	for _, v := range input.Template {
		actions = append(actions, &execAction{Sql: "replace into template(id,name,description,create_time,create_user,update_time,update_user) values (?,?,?,?,?,?,?)", Param: []interface{}{v.Id, v.Name, v.Description, v.CreateTime, v.CreateUser, updateTime, updateUser}})
	}
	for _, v := range input.ProviderTemplateValue {
		actions = append(actions, &execAction{Sql: "replace into provider_template_value(id,value,provider,template_value,create_time,create_user,update_time,update_user) values (?,?,?,?,?,?,?,?)", Param: []interface{}{v.Id, v.Value, v.Provider, v.TemplateValue, v.CreateTime, v.CreateUser, updateTime, updateUser}})
	}
	for _, v := range input.TemplateValue {
		actions = append(actions, &execAction{Sql: "replace into template_value(id,value,template,create_time,create_user,update_time,update_user) values (?,?,?,?,?,?,?)", Param: []interface{}{v.Id, v.Value, v.Template, v.CreateTime, v.CreateUser, updateTime, updateUser}})
	}
	for _, v := range input.Parameter {
		tmpAction := execAction{Sql: "replace into `parameter`(id,name,`type`,multiple,interface,datatype,source,create_time,create_user,update_time,update_user,nullable,`sensitive`,template,object_name) values (?,?,?,?,?,?,?,?,?,?,?,?,?"}
		tmpAction.Param = []interface{}{v.Id, v.Name, v.Type, v.Multiple, v.Interface, v.DataType, v.Source, v.CreateTime, v.CreateUser, updateTime, updateUser, v.Nullable, v.Sensitive}
		tmpAction.Sql += "," + getRelativeNullValue(v.Template)
		tmpAction.Sql += "," + getRelativeNullValue(v.ObjectName) + ")"
		actions = append(actions, &tmpAction)
	}
	for _, v := range input.Source {
		tmpAction := execAction{Sql: "replace into source(id,interface,provider,name,asset_id_attribute,terraform_used,import_prefix,execution_seq_no,import_support,source_type,create_time,create_user,update_time,update_user) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"}
		tmpAction.Param = []interface{}{v.Id, v.Interface, v.Provider, v.Name, v.AssetIdAttribute, v.TerraformUsed, v.ImportPrefix, v.ExecutionSeqNo, v.ImportSupport, v.SourceType, v.CreateTime, v.CreateUser, updateTime, updateUser}
		actions = append(actions, &tmpAction)
	}
	for _, v := range input.TfArgument {
		tmpAction := execAction{Sql: "replace into tf_argument(id,name,source,default_value,is_null,`type`,is_multi,convert_way,function_define,key_argument,create_time,create_user,update_time,update_user,`parameter`,object_name,relative_source,relative_tfstate_attribute,relative_parameter,relative_parameter_value) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?"}
		tmpAction.Param = []interface{}{v.Id, v.Name, v.Source, v.DefaultValue, v.IsNull, v.Type, v.IsMulti, v.ConvertWay, v.FunctionDefine, v.KeyArgument, v.CreateTime, v.CreateUser, updateTime, updateUser}
		tmpAction.Sql += "," + getRelativeNullValue(v.Parameter)
		tmpAction.Sql += "," + getRelativeNullValue(v.ObjectName)
		tmpAction.Sql += "," + getRelativeNullValue(v.RelativeSource)
		tmpAction.Sql += "," + getRelativeNullValue(v.RelativeTfstateAttribute)
		tmpAction.Sql += "," + getRelativeNullValue(v.RelativeParameter)
		tmpAction.Sql += "," + getRelativeNullValue(v.RelativeParameterValue) + ")"
		actions = append(actions, &tmpAction)
	}
	for _, v := range input.TfstateAttribute {
		tmpAction := execAction{Sql: "replace into tfstate_attribute(id,name,source,default_value,is_null,`type`,is_multi,convert_way,function_define,create_time,create_user,update_time,update_user,`parameter`,object_name,relative_source,relative_tfstate_attribute,relative_parameter,relative_parameter_value) values (?,?,?,?,?,?,?,?,?,?,?,?,?"}
		tmpAction.Param = []interface{}{v.Id, v.Name, v.Source, v.DefaultValue, v.IsNull, v.Type, v.IsMulti, v.ConvertWay, v.FunctionDefine, v.CreateTime, v.CreateUser, updateTime, updateUser}
		tmpAction.Sql += "," + getRelativeNullValue(v.Parameter)
		tmpAction.Sql += "," + getRelativeNullValue(v.ObjectName)
		tmpAction.Sql += "," + getRelativeNullValue(v.RelativeSource)
		tmpAction.Sql += "," + getRelativeNullValue(v.RelativeTfstateAttribute)
		tmpAction.Sql += "," + getRelativeNullValue(v.RelativeParameter)
		tmpAction.Sql += "," + getRelativeNullValue(v.RelativeParameterValue) + ")"
		actions = append(actions, &tmpAction)
	}
	return transactionWithoutForeignCheck(actions)
}

func getRelativeNullValue(input string) string {
	output := "NULL"
	if input != "" {
		output = "'" + input + "'"
	}
	return output
}
