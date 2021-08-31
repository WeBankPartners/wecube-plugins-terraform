package db

import (
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
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
			SecretKeyAttrName: param[i].SecretKeyAttrName, RegionAttrName: param[i].RegionAttrName, CreateUser: user, CreateTime: createTime,
			UpdateUser: user, UpdateTime: createTime, NameSpace: param[i].NameSpace}
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

func ProviderPluginExport(providerNameList, pluginNameList []string) (result models.ProviderPluginImportObj, err error) {
	result = models.ProviderPluginImportObj{Provider: []*models.ProviderTable{}, Plugin: []*models.PluginTable{}}
	result.ProviderTemplateValue = []*models.ProviderTemplateValueTable{}
	result.Template = []*models.TemplateTable{}
	result.TemplateValue = []*models.TemplateValueTable{}
	result.Interface = []*models.InterfaceTable{}
	result.Parameter = []*models.ParameterTable{}
	result.Source = []*models.SourceTable{}
	result.TfArgument = []*models.TfArgumentTable{}
	result.TfstateAttribute = []*models.TfstateAttributeTable{}
	specSql, paramList := createListParams(providerNameList, "")
	err = x.SQL("select * from provider where name in ("+specSql+")", paramList...).Find(&result.Provider)
	if err != nil {
		err = fmt.Errorf("Query database provider table fail,%s ", err.Error())
		return
	}
	if len(result.Provider) == 0 {
		err = fmt.Errorf("Can not find any provider with name:%s ", providerNameList)
		return
	}
	var providerIdList, pluginIdList []string
	var providerIdFilterSql, pluginIdFilterSql string
	for _, v := range result.Provider {
		providerIdList = append(providerIdList, v.Id)
	}
	providerIdFilterSql = fmt.Sprintf("('%s')", strings.Join(providerIdList, "','"))
	specSql, paramList = createListParams(pluginNameList, "")
	err = x.SQL("select * from plugin where name in ("+specSql+")", paramList...).Find(&result.Plugin)
	if err == nil && len(result.Plugin) == 0 {
		err = fmt.Errorf("Can not find any plugin with name:%s ", pluginNameList)
		return
	}
	for _, v := range result.Plugin {
		pluginIdList = append(pluginIdList, v.Id)
	}
	pluginIdFilterSql = fmt.Sprintf("('%s')", strings.Join(pluginIdList, "','"))
	x.SQL("select * from interface where plugin in " + pluginIdFilterSql).Find(&result.Interface)
	x.SQL("select * from `parameter` where interface in (select id from interface where plugin in " + pluginIdFilterSql + ")").Find(&result.Parameter)
	templateSql := "select * from template where id in (select template_value from provider_template_value where provider in " + providerIdFilterSql + ")"
	templateSql += " union "
	templateSql += "select * from template where id in (select template from `parameter` where interface in (select id from interface where plugin in " + pluginIdFilterSql + "))"
	x.SQL(templateSql).Find(&result.Template)
	x.SQL("select * from template_value where template in (" + strings.ReplaceAll(templateSql, "*", "id") + ")").Find(&result.TemplateValue)
	sourceSql := "select * from source where interface in (select id from interface where plugin in " + pluginIdFilterSql + ") and provider in " + providerIdFilterSql
	x.SQL(sourceSql).Find(&result.Source)
	x.SQL("select * from tf_argument where source in (" + strings.ReplaceAll(sourceSql, "*", "id") + ")").Find(&result.TfArgument)
	x.SQL("select * from tfstate_attribute where source in (" + strings.ReplaceAll(sourceSql, "*", "id") + ")").Find(&result.TfstateAttribute)
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
		tmpAction := execAction{Sql: "replace into provider(id,name,`version`,secret_id_attr_name,secret_key_attr_name,region_attr_name,Initialized,create_time,create_user,update_time,update_user,name_space) values (?,?,?,?,?,?,?,?,?,?,?,?)"}
		tmpAction.Param = []interface{}{v.Id, v.Name, v.Version, v.SecretIdAttrName, v.SecretKeyAttrName, v.RegionAttrName, v.Initialized, v.CreateTime, v.CreateUser, updateTime, updateUser, v.NameSpace}
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

func ProviderDownload(providerId string) (err error) {
	sqlCmd := "SELECT * FROM provider WHERE id=?"
	paramArgs := []interface{}{providerId}
	var rowData []*models.ProviderTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get provider by id error", log.String("id", providerId), log.Error(err))
		err = fmt.Errorf("Get provider by id:%s error:%s", providerId, err.Error())
		return
	}
	if len(rowData) == 0 {
		log.Logger.Error("Can not get provider by id", log.String("id", providerId), log.Error(err))
		err = fmt.Errorf("Can not get provider by id:%s", providerId)
		return
	}
	providerData := rowData[0]

	terraformFilePath := models.Config.TerraformFilePath
	if terraformFilePath[len(terraformFilePath)-1] != '/' {
		terraformFilePath += "/"
	}
	terraformProviderCommonPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version
	// terraformProviderPath := terraformProviderCommonPath + "/" + models.Config.TerraformProviderOsArch
	terraformLockHclPath :=  terraformProviderCommonPath + "/" + models.Config.TerraformProviderOsArch + "_hcl"

	/*
	err = GenDir(terraformProviderPath)
	if err != nil {
		err = fmt.Errorf("Gen terraformProviderPath : %s error: %s", terraformProviderPath, err.Error())
		log.Logger.Error("Gen terraformProviderPath error", log.String("terraformProviderPath", terraformProviderPath), log.Error(err))
		return
	}
	*/

	err = GenDir(terraformLockHclPath)
	if err != nil {
		err = fmt.Errorf("Gen terraformLockHclPath: %s error: %s", terraformLockHclPath, err.Error())
		log.Logger.Error("Gen terraformLockHclPath error", log.String("terraformLockHclPath", terraformLockHclPath), log.Error(err))
		return
	}
	GenTerraformConfigFile(terraformProviderCommonPath, providerData)
	err = DownloadProviderByTerraformInit(terraformProviderCommonPath)
	if err != nil {
		err = fmt.Errorf("Download provider file error: %s", err.Error())
		log.Logger.Error("Download provider file error", log.Error(err))
		return
	}

	downloadProviderFilePath := terraformProviderCommonPath + "/.terraform/providers/registry.terraform.io/" + providerData.NameSpace + "/" + providerData.Name + "/" + providerData.Version + "/" + models.Config.TerraformProviderOsArch
	cmdStr := "cp -R " + downloadProviderFilePath + " " + terraformProviderCommonPath
	cmd := exec.Command(models.BashCmd, "-c", cmdStr)
	err = cmd.Run()
	if err != nil {
		err = fmt.Errorf("Move provider file error: %s", err.Error())
		log.Logger.Error("Move provider file error", log.Error(err))
		return
	}

	downloadProviderHclFilePath := terraformProviderCommonPath + "/.terraform.lock.hcl"
	cmdStr = "cp " + downloadProviderHclFilePath + " " + terraformLockHclPath + "/"
	cmd = exec.Command(models.BashCmd, "-c", cmdStr)
	err = cmd.Run()
	if err != nil {
		err = fmt.Errorf("Move provider hcl file error: %s", err.Error())
		log.Logger.Error("Move provider hcl file error", log.Error(err))
		return
	}

	err = DelDir(terraformProviderCommonPath + "/.terraform")
	if err != nil {
		err = fmt.Errorf("Del .terraform dir error: %s", err.Error())
		log.Logger.Error("Del .terraform dir error", log.Error(err))
		return
	}

	err = DelFile(downloadProviderHclFilePath)
	if err != nil {
		err = fmt.Errorf("Del downloaded provider hcl file error: %s", err.Error())
		log.Logger.Error("Del downloaded provider hcl file error", log.Error(err))
		return
	}
	return
}

func ProviderUpload(providerId string, r *http.Request) (err error) {
	sqlCmd := "SELECT * FROM provider WHERE id=?"
	paramArgs := []interface{}{providerId}
	var rowData []*models.ProviderTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&rowData)
	if err != nil {
		log.Logger.Error("Get provider by id error", log.String("id", providerId), log.Error(err))
		err = fmt.Errorf("Get provider by id:%s error:%s", providerId, err.Error())
		return
	}
	if len(rowData) == 0 {
		log.Logger.Error("Can not get provider by id", log.String("id", providerId), log.Error(err))
		err = fmt.Errorf("Can not get provider by id:%s", providerId)
		return
	}
	providerData := rowData[0]

	terraformFilePath := models.Config.TerraformFilePath
	if terraformFilePath[len(terraformFilePath)-1] != '/' {
		terraformFilePath += "/"
	}
	terraformProviderCommonPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version
	terraformLockHclPath :=  terraformProviderCommonPath + "/" + models.Config.TerraformProviderOsArch + "_hcl"

	err = GenDir(terraformLockHclPath)
	if err != nil {
		err = fmt.Errorf("Gen terraformLockHclPath: %s error: %s", terraformLockHclPath, err.Error())
		log.Logger.Error("Gen terraformLockHclPath error", log.String("terraformLockHclPath", terraformLockHclPath), log.Error(err))
		return
	}

	var reader *multipart.Reader
	reader, err = r.MultipartReader()
	if err != nil {
		err = fmt.Errorf("Get multipartReader error: %s", err.Error())
		log.Logger.Error("Get multipartReader error", log.Error(err))
		return
	}

	part, tmpErr := reader.NextPart()
	if tmpErr != nil {
		err = fmt.Errorf("Upload file failed:%s", tmpErr.Error())
		log.Logger.Error("Upload file failed", log.Error(err))
		return
	}
	filePath := terraformProviderCommonPath + "/" + part.FileName()
	fileName := part.FileName()
	if !strings.Contains(fileName, ".tar.gz") && !strings.Contains(fileName, ".zip") {
		err = fmt.Errorf("Upload file only supports tar.gz and zip")
		log.Logger.Error("Upload file only supports tar.gz and zip")
		return
	}

	file, tmpErr := os.Create(filePath)
	if tmpErr != nil {
		err = fmt.Errorf("Create file:%s error: %s", filePath, tmpErr.Error())
		log.Logger.Error("Create file error", log.String("file", filePath), log.Error(err))
		return
	}
	_, tmpErr = io.Copy(file, part)
	file.Close()

	// Gen the upload file tmp dir
	uploadFileTmpDir := terraformProviderCommonPath + "/tmp"
	err = GenDir(uploadFileTmpDir)
	if err != nil {
		err = fmt.Errorf("Gen the upload file tmp dir: %s error: %s", uploadFileTmpDir, err.Error())
		log.Logger.Error("Gen the upload file tmp dir error", log.String("uploadFileTmpDir", uploadFileTmpDir), log.Error(err))
		return
	}

	// decompress the upload file
	var cmdStr string
	if strings.Contains(fileName, ".tar.gz") {
		cmdStr = "tar -xzf " + filePath + " -C " + uploadFileTmpDir
	} else {
		cmdStr = "unzip " + "-d " + uploadFileTmpDir + " " + filePath
	}
	cmd := exec.Command(models.BashCmd, "-c", cmdStr)
	err = cmd.Run()
	if err != nil {
		err = fmt.Errorf("Decompress file:%s error: %s", fileName, err.Error())
		log.Logger.Error("Decompress file error", log.String("file", fileName), log.Error(err))
		return
	}

	// move the upload file to specificied dir
	uploadProviderFilePath := uploadFileTmpDir + "/.terraform/providers/registry.terraform.io/" + providerData.NameSpace + "/" + providerData.Name + "/" + providerData.Version + "/" + models.Config.TerraformProviderOsArch
	_, err = os.Stat(uploadProviderFilePath)
	if err != nil {
		if os.IsNotExist(err) {
			err = fmt.Errorf("Check dir: %s error: %s", uploadProviderFilePath, err.Error())
			log.Logger.Error("Check dir error", log.String("dirPath", uploadProviderFilePath), log.Error(err))
			return
		}
		err = fmt.Errorf("Os stat dir: %s error: %s", uploadProviderFilePath, err.Error())
		log.Logger.Error("Os stat dir error", log.String("dirPath", uploadProviderFilePath), log.Error(err))
		return
	}
	cmdStr = "cp -R " + uploadProviderFilePath + " " + terraformProviderCommonPath
	cmd = exec.Command(models.BashCmd, "-c", cmdStr)
	err = cmd.Run()
	if err != nil {
		err = fmt.Errorf("Move provider file error: %s", err.Error())
		log.Logger.Error("Move provider file error", log.Error(err))
		return
	}

	uploadProviderHclFilePath := uploadFileTmpDir + "/.terraform.lock.hcl"
	_, err = os.Stat(uploadProviderHclFilePath)
	if err != nil {
		if os.IsNotExist(err) {
			err = fmt.Errorf("Check file: %s error: %s", uploadProviderHclFilePath, err.Error())
			log.Logger.Error("Check file error", log.String("file", uploadProviderHclFilePath), log.Error(err))
			return
		}
		err = fmt.Errorf("Os stat file: %s error: %s", uploadProviderHclFilePath, err.Error())
		log.Logger.Error("Os stat file error", log.String("file", uploadProviderHclFilePath), log.Error(err))
		return
	}
	cmdStr = "cp " + uploadProviderHclFilePath + " " + terraformLockHclPath + "/"
	cmd = exec.Command(models.BashCmd, "-c", cmdStr)
	err = cmd.Run()
	if err != nil {
		err = fmt.Errorf("Move provider hcl file error: %s", err.Error())
		log.Logger.Error("Move provider hcl file error", log.Error(err))
		return
	}

	err = DelDir(uploadFileTmpDir)
	if err != nil {
		err = fmt.Errorf("Del upload file tmp dir error: %s", err.Error())
		log.Logger.Error("Del upload file tmp dir error", log.Error(err))
		return
	}

	err = DelFile(filePath)
	if err != nil {
		err = fmt.Errorf("Del uploaded  file error: %s", err.Error())
		log.Logger.Error("Del uploaded file error", log.Error(err))
		return
	}
	return
}