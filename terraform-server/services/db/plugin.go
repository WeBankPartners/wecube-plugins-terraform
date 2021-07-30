package db

import (
	"bytes"
	"encoding/xml"
	"fmt"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func PluginCreate(param *models.PluginTable) (rowData *models.PluginTable, err error) {
	id := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("INSERT INTO plugin(id,name,create_user,create_time) VALUE (?,?,?,?)",
		id, param.Name, param.CreateUser, createTime)

	rowData = &models.PluginTable{Id: id, Name: param.Name, CreateUser: param.CreateUser, CreateTime: createTime}

	if err != nil {
		err = fmt.Errorf("Try to create plugin fail,%s ", err.Error())
	}
	return
}

func PluginList(paramsMap map[string]interface{}) (rowData []*models.PluginTable, err error) {
	sqlCmd := "SELECT * FROM plugin WHERE 1=1"
	paramArgs := []interface{}{}
	for k, v := range paramsMap {
		sqlCmd += " AND " + k + "=?"
		paramArgs = append(paramArgs, v)
	}
	sqlCmd += " ORDER BY create_time DESC"
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get plugin list error", log.Error(err))
	}
	return
}

func PluginDelete(pluginId string) (err error) {
	var pluginList []*models.PluginTable
	err = x.SQL("SELECT id FROM plugin WHERE id=?", pluginId).Find(&pluginList)
	if err != nil {
		log.Logger.Error("Try to query plugin fail", log.String("pluginId", pluginId), log.Error(err))
		return
	}
	if len(pluginList) == 0 {
		return
	}
	_, err = x.Exec("DELETE FROM plugin WHERE id=?", pluginId)
	return
}

func PluginUpdate(pluginId string, param *models.PluginTable) (err error) {
	var pluginList []*models.PluginTable
	err = x.SQL("SELECT id FROM plugin WHERE id=?", pluginId).Find(&pluginList)
	if err != nil {
		log.Logger.Error("Try to query plugin fail", log.String("pluginId", pluginId), log.Error(err))
		return
	}
	if len(pluginList) == 0 {
		return
	}
	updateTime := time.Now().Format(models.DateTimeFormat)
	_, err = x.Exec("UPDATE plugin SET name=?,update_time=?,update_user=? WHERE id=?",
		param.Name, updateTime, param.UpdateUser, pluginId)
	return
}

func PluginBatchCreate(user string, param []*models.PluginTable) (rowData []*models.PluginTable, err error) {
	actions := []*execAction{}
	tableName := "plugin"
	createTime := time.Now().Format(models.DateTimeFormat)

	for i := range param {
		id := guid.CreateGuid()
		data := &models.PluginTable{Id: id, Name: param[i].Name, CreateUser: user, CreateTime: createTime, UpdateUser: user, UpdateTime: createTime}
		rowData = append(rowData, data)
	}

	for i := range rowData {
		action, tmpErr := GetInsertTableExecAction(tableName, *rowData[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to create plugin fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to create plugin fail,%s ", err.Error())
	}
	return
}

func PluginBatchDelete(ids []string) (err error) {
	actions := []*execAction{}
	tableName := "plugin"
	for i := range ids {
		action, tmpErr := GetDeleteTableExecAction(tableName, "id", ids[i])
		if tmpErr != nil {
			err = fmt.Errorf("Try to delete plugin fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}
	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to delete plugin fail,%s ", err.Error())
	}
	return
}

func PluginBatchUpdate(user string, param []*models.PluginTable) (err error) {
	actions := []*execAction{}
	tableName := "plugin"
	updateTime := time.Now().Format(models.DateTimeFormat)
	for i := range param {
		param[i].UpdateTime = updateTime
		param[i].UpdateUser = user
		action, tmpErr := GetUpdateTableExecAction(tableName, "id", param[i].Id, *param[i], nil)
		if tmpErr != nil {
			err = fmt.Errorf("Try to update plugin fail,%s ", tmpErr.Error())
			return
		}
		actions = append(actions, action)
	}

	err = transaction(actions)
	if err != nil {
		err = fmt.Errorf("Try to update plugin fail,%s ", err.Error())
	}
	return
}

func PluginXmlExport() (result []byte, err error) {
	var pluginTable []*models.PluginTable
	err = x.SQL("select id,name from plugin").Find(&pluginTable)
	if err != nil {
		return result, fmt.Errorf("Try to query plugin table fail,%s ", err.Error())
	}
	if len(pluginTable) == 0 {
		return result, fmt.Errorf("Plugin table is empty ")
	}
	var interfaceTable []*models.InterfaceTable
	err = x.SQL("select id,name,plugin,description from interface order by plugin,name").Find(&interfaceTable)
	if err != nil {
		return result, fmt.Errorf("Try to query interface table fail,%s ", err.Error())
	}
	resultBuffer := bytes.NewBuffer(result)
	interfaceNameMap := make(map[string]string)
	pluginInterfaceMap := make(map[string][]*models.InterfaceTable)
	for _, v := range interfaceTable {
		interfaceNameMap[v.Id] = v.Name
		if _, b := pluginInterfaceMap[v.Plugin]; !b {
			pluginInterfaceMap[v.Plugin] = []*models.InterfaceTable{v}
		} else {
			pluginInterfaceMap[v.Plugin] = append(pluginInterfaceMap[v.Plugin], v)
		}
	}
	paramObjectBytes, xmlParamObjectMap, err := buildXmlParamObject(interfaceNameMap)
	if err != nil {
		return result, err
	}
	resultBuffer.Write(paramObjectBytes)
	resultBuffer.WriteString("\n\n")
	var parameterTable []*models.ParameterTable
	err = x.SQL("select name,`type`,multiple,interface,datatype,nullable,`sensitive` from `parameter` where object_name is null order by interface,`type`,name").Find(&parameterTable)
	if err != nil {
		return result, fmt.Errorf("Try to query paramether table fail,%s ", err.Error())
	}
	parameterMap := make(map[string][]*models.ParameterTable)
	for _, v := range parameterTable {
		if _, b := parameterMap[v.Interface]; !b {
			parameterMap[v.Interface] = []*models.ParameterTable{v}
		} else {
			parameterMap[v.Interface] = append(parameterMap[v.Interface], v)
		}
	}
	var xmlPlugins = models.XmlPlugins{Plugins: []*models.XmlPlugin{}}
	for _, plugin := range pluginTable {
		tmpPlugin := models.XmlPlugin{Name: plugin.Name, Interfaces: []*models.XmlInterface{}}
		for _, interfaceObj := range pluginInterfaceMap[plugin.Id] {
			tmpInterface := models.XmlInterface{Action: interfaceObj.Name, InputParameters: models.XmlInputParameters{Parameters: []*models.XmlParameter{}}, OutputParameters: models.XmlOutputParameters{Parameters: []*models.XmlParameter{}}}
			tmpInterface.Path = fmt.Sprintf("%s/api/v1/terraform/%s/%s", models.UrlPrefix, plugin.Name, interfaceObj.Name)
			for _, parameter := range parameterMap[interfaceObj.Id] {
				tmpParameter := models.XmlParameter{Datatype: parameter.DataType, Multiple: parameter.Multiple, SensitiveData: parameter.Sensitive, Required: "N", Value: parameter.Name}
				if parameter.Nullable == "N" {
					tmpParameter.Required = "Y"
				}
				if parameter.DataType == "object" {
					tmpParameter.RefObjectName = fmt.Sprintf("%s_%s_%s", interfaceNameMap[parameter.Interface], parameter.Type, parameter.Name)
					if _, b := xmlParamObjectMap[tmpParameter.RefObjectName]; !b {
						tmpParameter.RefObjectName = ""
					}
				}
				if parameter.Type == "input" {
					tmpInterface.InputParameters.Parameters = append(tmpInterface.InputParameters.Parameters, &tmpParameter)
				} else {
					tmpInterface.OutputParameters.Parameters = append(tmpInterface.OutputParameters.Parameters, &tmpParameter)
				}
			}
			tmpPlugin.Interfaces = append(tmpPlugin.Interfaces, &tmpInterface)
		}
		xmlPlugins.Plugins = append(xmlPlugins.Plugins, &tmpPlugin)
	}
	pluginXmlBytes, marshalErr := xml.MarshalIndent(xmlPlugins, "", "\t")
	if marshalErr != nil {
		return result, fmt.Errorf("Xml marshal plugins fail,%s ", marshalErr.Error())
	}
	resultBuffer.Write(pluginXmlBytes)
	return resultBuffer.Bytes(), nil
}

func buildXmlParamObject(interfaceNameMap map[string]string) (result []byte, paramObjectMap map[string]bool, err error) {
	var objectParams, objectPropertyParams []*models.ParameterTable
	paramObjectMap = make(map[string]bool)
	err = x.SQL("select * from `parameter` where id in (select distinct object_name from `parameter` where object_name is not null)").Find(&objectParams)
	if err != nil {
		err = fmt.Errorf("Try to query object paramether fail,%s ", err.Error())
		return
	}
	if len(objectParams) == 0 {
		result = []byte("<paramObjects></paramObjects>")
		return
	}
	var objectParamsNameMap = make(map[string]string)
	for _, v := range objectParams {
		objectParamsNameMap[v.Id] = fmt.Sprintf("%s_%s_%s", interfaceNameMap[v.Interface], v.Type, v.Name)
	}
	err = x.SQL("select * from `parameter` where object_name is not null order by object_name").Find(&objectPropertyParams)
	if err != nil {
		err = fmt.Errorf("Try to query object property paramether fail,%s ", err.Error())
		return
	}
	var objectPropertyMap = make(map[string][]*models.ParameterTable)
	for _, objectProperty := range objectPropertyParams {
		if _, b := objectPropertyMap[objectProperty.ObjectName]; !b {
			objectPropertyMap[objectProperty.ObjectName] = []*models.ParameterTable{objectProperty}
		} else {
			objectPropertyMap[objectProperty.ObjectName] = append(objectPropertyMap[objectProperty.ObjectName], objectProperty)
		}
	}
	var xmlParamObjects = models.XmlParamObjects{ParamObjects: []*models.XmlParamObject{}}
	for _, object := range objectParams {
		if _, b := objectPropertyMap[object.Id]; !b {
			continue
		}
		tmpParamObject := models.XmlParamObject{Name: fmt.Sprintf("%s_%s_%s", interfaceNameMap[object.Interface], object.Type, object.Name), Properties: []*models.XmlParamProperty{}}
		paramObjectMap[tmpParamObject.Name] = true
		for _, property := range objectPropertyMap[object.Id] {
			tmpProperty := models.XmlParamProperty{Name: property.Name, Multiple: property.Multiple, DataType: property.DataType, SensitiveData: property.Sensitive, Required: "N"}
			if property.DataType == "object" {
				if _, b := objectParamsNameMap[property.Id]; b {
					tmpProperty.RefObjectName = objectParamsNameMap[property.Id]
				}
			}
			if property.Nullable == "N" {
				tmpProperty.Required = "Y"
			}
			tmpParamObject.Properties = append(tmpParamObject.Properties, &tmpProperty)
		}
		xmlParamObjects.ParamObjects = append(xmlParamObjects.ParamObjects, &tmpParamObject)
	}
	result, err = xml.MarshalIndent(xmlParamObjects, "", "\t")
	if err != nil {
		err = fmt.Errorf("Xml marshal paramObjects fail,%s ", err.Error())
	}
	return
}
