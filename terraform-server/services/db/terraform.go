package db

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/cipher"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func GenFile(content []byte, filePath string) (err error) {
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		log.Logger.Error("open file error", log.String("file", filePath), log.Error(err))
		return
	}
	defer file.Close()

	_, err = file.Write(content)
	if err != nil {
		log.Logger.Error("write file error", log.String("file", filePath), log.Error(err))
	}
	return
	/*
		// test
		param["test1"] = "param"
		test2 := []int{1, 2, 3}
		param["test2"] = test2
		test3 := make(map[string]interface{})
		test3["aa"] = true
		test3["bb"] = false
		test3["cc"] = []int{11,22,33}
		param["test3"] = test3
		// ans, err := json.Marshal(param)
		ans, err := json.MarshalIndent(param, "", "    ")
		fmt.Printf("%v", string(ans))
	*/
	return
}

func ReadFile(filePath string) (content []byte, err error) {
	file, err := os.Open(filePath)
	if err != nil {
		log.Logger.Error("open file error", log.String("file", filePath), log.Error(err))
		return
	}
	defer file.Close()
	content, err = ioutil.ReadAll(file)
	return
}

func TerraformImport(dirPath, address, resourceId string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " import " + address + " " + resourceId
	cmd := exec.Command(cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		err = fmt.Errorf("cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
	}
	return
}

func TerraformPlan(dirPath string) (destroyCnt int, err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " plan -out=" + dirPath + "/planfile"
	cmd := exec.Command(cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		err = fmt.Errorf("cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
		return
	}
	//outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
	filePath := dirPath + "/planfile"
	planFile, err := os.Open(filePath)
	if err != nil {
		log.Logger.Error("open planfile error", log.String("planfile", filePath), log.Error(err))
		return
	}
	defer planFile.Close()

	// 每行读取
	scanner := bufio.NewScanner(planFile)
	for scanner.Scan() {
		if strings.Contains(scanner.Text(), "Plan:") && strings.Contains(scanner.Text(), "to add") && strings.Contains(scanner.Text(), "to change") && strings.Contains(scanner.Text(), "to destroy") {
			// 获取 to destroy 前面的数值
			planStr := scanner.Text()
			idx := strings.Index(planStr, "to destroy")
			sIdx, eIdx := -1, -1
			for idx >= 0 {
				if planStr[idx] >= '0' && planStr[idx] <= '9' {
					break
				}
				eIdx = idx
				idx--
			}
			for idx >= 0 {
				if planStr[idx] >= '0' && planStr[idx] <= '9' {
					sIdx = idx
					idx--
				} else {
					break
				}
			}
			if sIdx != -1 && eIdx != -1 {
				destroyNumStr := planStr[sIdx:eIdx]
				destroyCnt, err = strconv.Atoi(destroyNumStr)
				if err != nil {
					err = fmt.Errorf("plan text:%s error", planStr)
					log.Logger.Error("plan text error", log.String("planText", planStr), log.Error(err))
				}
			} else {
				err = fmt.Errorf("plan text:%s error", planStr)
				log.Logger.Error("plan text error", log.String("planText", planStr), log.Error(err))
			}
			return
		}
	}
	return
}

func TerraformApply(dirPath string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " apply -auto-approve"
	cmd := exec.Command(cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		err = fmt.Errorf("cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
	}
	return
}

func TerraformDestroy(dirPath string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " destroy -auto-approve"
	cmd := exec.Command(cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		err = fmt.Errorf("cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
	}
	return
}

func handleTerraformApplyOrQuery(plugin string,
	                             action string,
	                             reqParam map[string]interface{},
 								 sourceList []*models.SourceTable,
								 providerData *models.ProviderTable,
							     providerInfo *models.ProviderInfoTable,
  							     regionData *models.ResourceDataTable) (retData *models.PluginInterfaceResultOutputObj, err error) {
	retData = &models.PluginInterfaceResultOutputObj{}
	retData.CallbackParameter = reqParam["callbackParameter"].(string)
	retData.ErrorCode = "1"
	// Get tf_argument_list by source_list
	sourceIdList := []string{}
	for i := range sourceList {
		sourceIdList = append(sourceIdList, sourceList[i].Id)
	}
	sourceIdStr := strings.Join(sourceIdList, "','")
	sqlCmd := "SELECT * FROM tf_argument WHERE source IN ('" + sourceIdStr + "')"
	var tfArgumentList []*models.TfArgumentTable
	err = x.SQL(sqlCmd).Find(&tfArgumentList)
	if err != nil {
		err = fmt.Errorf("Get tf_argument list error:%s", err.Error())
		log.Logger.Error("Get tf_argument list error", log.Error(err))
		retData.ErrorMessage = err.Error()
		return
	}
	if len(tfArgumentList) == 0 {
		err = fmt.Errorf("tf_argument list can not be found by source:%s", sourceIdList)
		log.Logger.Warn("tf_argument list can not be found by source", log.String("source", sourceIdStr), log.Error(err))
		retData.ErrorMessage = err.Error()
		return
	}

	// Get tfstate_attribute by source_list
	sqlCmd = "SELECT * FROM tfstate_attribute WHERE source IN ('" + sourceIdStr + "')"
	var tfstateAttributeList []*models.TfstateAttributeTable
	err = x.SQL(sqlCmd).Find(&tfstateAttributeList)
	if err != nil {
		err = fmt.Errorf("Get tfstate_attribute list error:%s", err.Error())
		log.Logger.Error("Get tfstate_attribute list error", log.Error(err))
		retData.ErrorMessage = err.Error()
		return
	}
	if len(tfstateAttributeList) == 0 {
		err = fmt.Errorf("tfstate_attribute list can not be found by source:%s", sourceIdList)
		log.Logger.Warn("tfstate_attribute list can not be found by source", log.String("source", sourceIdStr), log.Error(err))
		retData.ErrorMessage = err.Error()
		return
	}

	tfArguments := make(map[string]interface{})
	// 循环处理每一个 tf_argument
	for i := range tfArgumentList {
		convertWay := tfArgumentList[i].ConvertWay
		var arg interface{}
		switch convertWay {
		case models.ConvertWay["Data"]:
			arg, err = convertData(tfArgumentList[i].Parameter, tfArgumentList[i].Source, reqParam)
		case models.ConvertWay["Template"]:
			arg, err = convertTemplate(tfArgumentList[i].Parameter, providerData.Name, reqParam)
		case models.ConvertWay["Context"]:
			arg, err = convertContext(tfArgumentList[i].RelativeParameter, tfArgumentList[i], reqParam)
		case models.ConvertWay["Attr"]:
			sourceIdList := make(map[string]bool)
			for i := range sourceList {
				sourceIdList[sourceList[i].Id] = true
			}
			handlingSourceIds := make(map[string]bool)
			handlingSourceIds[tfArgumentList[i].Source] = true
			arg, err = convertAttr(tfArgumentList[i].TfstateAttribute, sourceIdList, handlingSourceIds, providerData.Name, reqParam)
		case models.ConvertWay["Direct"]:
			arg, err = convertDirect(tfArgumentList[i].Parameter, tfArgumentList[i].DefaultValue, reqParam)
		}
		if err != nil {
			err = fmt.Errorf("convert parameter:%s error:%s", tfArgumentList[i].Parameter, err.Error())
			log.Logger.Error("convert parameter error", log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
			retData.ErrorMessage = err.Error()
			return
		}
		tfArguments[tfArgumentList[i].Name] = arg
		if convertWay == "direct" && arg.(string) == "null" {
			delete(tfArguments, tfArgumentList[i].Name)
		}
	}
	var dirPath, address, resourceId string
	// terraform import
	err = TerraformImport(dirPath, address, resourceId)
	if err != nil {
		err = fmt.Errorf("do TerraformImport error:%s", err.Error())
		retData.ErrorMessage = err.Error()
		return
	}
	// terraform plan
	destroyCnt, err := TerraformPlan(dirPath)
	if err != nil {
		err = fmt.Errorf("do TerraformPlan error:%s", err.Error())
		retData.ErrorMessage = err.Error()
		return
	}
	if destroyCnt > 0 && reqParam["confirmToken"] != "Y" {
		// 二次确认
		destroyCntStr := strconv.Itoa(destroyCnt)
		retData.ErrorMessage = destroyCntStr + "resource(s) will be destroy, please confirm again!"
		return
	}

	// terraform apply
	err = TerraformApply(dirPath)
	if err != nil {
		err = fmt.Errorf("do TerraformApply error:%s", err.Error())
		retData.ErrorMessage = err.Error()
		return
	}

	tfstateAttrNameMap := make(map[string]*models.TfstateAttributeTable)
	for _, v := range tfstateAttributeList {
		tfstateAttrNameMap[v.Name] = v
	}
	// 读取 tfstate.tf.json 文件
	tfstateFileData, err := ReadFile(dirPath+"/tfstate.tf.json")
	if err != nil {
		err = fmt.Errorf("read tfstate file error:%s", err.Error())
		retData.ErrorMessage = err.Error()
		return
	}
	var tfstateContent map[string]string
	err = json.Unmarshal(tfstateFileData, tfstateContent)
	if err != nil {
		err = fmt.Errorf("marshal tfstate file data error:%s", err.Error())
		retData.ErrorMessage = err.Error()
		return
	}
	outPutArgs := make(map[string]string)
	// 循环遍历每个 tfstateContent，进行 reverseConvert 生成输出参数
	for k, v := range tfstateContent {
		if tfstateAttr, ok := tfstateAttrNameMap[k]; ok {
			convertWay := tfstateAttr.ConvertWay
			var outArgKey, outArgVal string
			switch convertWay {
			case models.ConvertWay["Data"]:
				outArgKey, outArgVal, err = reverseConvertData(tfstateAttr.Parameter, tfstateAttr.Source, v)
			case models.ConvertWay["Template"]:
				outArgKey, outArgVal, err = reverseConvertTemplate(tfstateAttr.Parameter, providerData.Name, v)
			case models.ConvertWay["Context"]:
				outArgKey, outArgVal, err = reverseConvertContext(tfstateAttr.RelativeParameter, v)
			case models.ConvertWay["Direct"]:
				outArgKey, outArgVal, err = reverseConvertDirect(tfstateAttr.Parameter, v)
			}
			if err != nil {
				err = fmt.Errorf("reverse convert parameter:%s error:%s", tfstateAttr.Parameter, err.Error())
				log.Logger.Error("revese convert parameter error", log.String("parameterId", tfstateAttr.Parameter), log.Error(err))
				retData.ErrorMessage = err.Error()
				return
			}
			outPutArgs[outArgKey] = outArgVal
		}
	}
	retData.ErrorCode = "0"
	// TODO Add outPutArgs to retData, insertInto resource_data table
	return
}

func TerraformOperation(plugin string, action string, reqParam map[string]interface{}) (rowData *models.PluginInterfaceResultOutputObj, err error) {
	// Get source list by plugin and action
	sqlCmd := `SELECT * FROM source WHERE plugin=? AND action=?`
	paramArgs := []interface{}{plugin, action}
	var sourceList []*models.SourceTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&sourceList)
	if err != nil {
		log.Logger.Error("Get source list error", log.Error(err))
		return
	}
	if len(sourceList) == 0 {
		err = fmt.Errorf("source list can not be found by plugin:%s and action:%s", plugin, action)
		log.Logger.Warn("source list can not be found by plugin and action", log.String("plugin", plugin), log.String("action", action), log.Error(err))
		return
	}

	// Get providerInfo data
	sqlCmd = `SELECT * FROM provider_info WHERE id=?`
	paramArgs = []interface{}{reqParam["providerInfoId"]}
	var providerInfoList []*models.ProviderInfoTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerInfoList)
	if err != nil {
		log.Logger.Error("Get providerInfo error", log.String("providerInfoId", reqParam["providerInfoId"].(string)), log.Error(err))
		return
	}
	if len(providerInfoList) == 0 {
		err = fmt.Errorf("providerInfo can not be found by id:%s", reqParam["providerInfoId"])
		log.Logger.Warn("providerInfo can not be found by id", log.String("id", reqParam["providerInfoId"].(string)), log.Error(err))
		return
	}
	providerInfoData := providerInfoList[0]
	providerSecretId, decodeErr := cipher.AesDePassword(models.Config.Auth.PasswordSeed, providerInfoData.SecretId)
	if decodeErr != nil {
		log.Logger.Error("Try to decode secretId fail", log.Error(decodeErr))
		return
	}
	providerSecretKey, decodeErr := cipher.AesDePassword(models.Config.Auth.PasswordSeed, providerInfoData.SecretKey)
	if decodeErr != nil {
		log.Logger.Error("Try to decode secretKey fail", log.Error(decodeErr))
		return
	}
	providerInfoData.SecretId = providerSecretId
	providerInfoData.SecretKey = providerSecretKey

	// Get provider data
	sqlCmd = `SELECT * FROM provider WHERE id=?`
	paramArgs = []interface{}{providerInfoData.Provider}
	var providerList []*models.ProviderTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerList)
	if err != nil {
		log.Logger.Error("Get provider error", log.String("providerId", providerInfoData.Provider), log.Error(err))
		return
	}
	if len(providerList) == 0 {
		err = fmt.Errorf("provider can not be found by id:%s", providerInfoData.Provider)
		log.Logger.Warn("provider can not be found by id", log.String("id", providerInfoData.Provider), log.Error(err))
		return
	}
	providerData := providerList[0]
	// providerVersion := providerList[0].Version

	// Get region data
	sqlCmd = `SELECT * FROM resource_data WHERE id=?`
	paramArgs = []interface{}{reqParam["regionId"]}
	var regionList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&regionList)
	if err != nil {
		log.Logger.Error("Get region data error", log.String("regionId", reqParam["regionId"].(string)), log.Error(err))
		return
	}
	if len(regionList) == 0 {
		err = fmt.Errorf("region can not be found by id:%s", reqParam["regionId"])
		log.Logger.Warn("region can not be found by id", log.String("id", reqParam["regionId"].(string)), log.Error(err))
		return
	}
	regionData := regionList[0]

	if action == "apply" || action == "query" {
		rowData, err = handleTerraformApplyOrQuery(plugin, action, reqParam, sourceList, providerData, providerInfoData, regionData)
	} else if action == "destroy" {
		var dirPath string
		// terraform destroy
		err = TerraformDestroy(dirPath)
		if err != nil {

		}
	}
	return
}

func convertData(parameterId string, source string, reqParam map[string]interface{}) (arg interface{}, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, parameterId)
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	sqlCmd = `SELECT * FROM resource_data WHERE source=? AND resource_id=?`
	paramArgs = []interface{}{source, reqParam[parameterData.Name]}
	var resourceDataList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		log.Logger.Error("Get resource_data error", log.String("source", source), log.String("resource_id", reqParam[parameterData.Name].(string)), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		err = fmt.Errorf("resource_data can not be found by source:%s and resource_id:%s", source, reqParam[parameterData.Name])
		log.Logger.Warn("resource_data can not be found by source and resource_id", log.String("source", source), log.String("value", reqParam[parameterData.Name].(string)), log.Error(err))
		return
	}
	arg = resourceDataList[0].ResourceAssetId
	return
}

func reverseConvertData(parameterId string, source string, tfstateVal string) (argKey string, argVal string, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, parameterId)
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	sqlCmd = `SELECT * FROM resource_data WHERE source=? AND resource_asset_id=?`
	paramArgs = []interface{}{source, tfstateVal}
	var resourceDataList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		log.Logger.Error("Get resource_data error", log.String("source", source), log.String("resource_asset_id", tfstateVal), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		err = fmt.Errorf("resource_data can not be found by source:%s and resource_asset_id:%s", source, tfstateVal)
		log.Logger.Warn("resource_data can not be found by source and resource_asset_id", log.String("source", source), log.String("value", tfstateVal), log.Error(err))
		return
	}
	argKey = parameterData.Name
	argVal = resourceDataList[0].ResourceId
	return
}

func convertTemplate(parameterId string, providerName string, reqParam map[string]interface{}) (arg interface{}, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, parameterId)
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	sqlCmd = `SELECT * FROM template_value WHERE template=? AND value=?`
	paramArgs = []interface{}{}
	paramArgs = append(paramArgs, parameterData.Template)
	paramArgs = append(paramArgs, reqParam[parameterData.Name])
	var templateValueList []*models.TemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&templateValueList)
	if err != nil {
		log.Logger.Error("Get tempalte_value data error", log.String("template", parameterData.Template), log.Error(err))
		return
	}
	if len(templateValueList) == 0 {
		err = fmt.Errorf("template_value can not be found by template:%s and value:%s", parameterData.Template, reqParam[parameterData.Name])
		log.Logger.Warn("template_value can not be found by template and value", log.String("template", parameterData.Template), log.String("value", reqParam[parameterData.Name].(string)), log.Error(err))
		return
	}
	templateValueData := templateValueList[0]

	sqlCmd = `SELECT * FROM provider_template_value WHERE template_value=? AND provider=?`
	paramArgs = []interface{}{}
	paramArgs = append(paramArgs, templateValueData.Id, providerName)
	var providerTemplateValueList []*models.ProviderTemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerTemplateValueList)
	if err != nil {
		log.Logger.Error("Get provider_tempalte_value data error", log.String("template_value", templateValueData.Id), log.String("provider", providerName), log.Error(err))
		return
	}
	if len(providerTemplateValueList) == 0 {
		err = fmt.Errorf("provider_template_value can not be found by template_value:%s and provider:%s", parameterData.Template)
		log.Logger.Warn("provider_template_value can not be found by template_value and provider", log.String("template_value", templateValueData.Id), log.String("provider", providerName), log.Error(err))
		return
	}
	arg = providerTemplateValueList[0].Value
	return
}

func reverseConvertTemplate(parameterId string, providerName string, tfstateVal string) (argKey string, argVal string, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, parameterId)
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	sqlCmd = `SELECT t1.* FROM template_value AS t1 LEFT JOIN provider_template_value AS t2 ON t1.id=t2.template_value WHERE t2.provider=? AND t2.value=?`
	paramArgs = []interface{}{providerName, tfstateVal}
	var templateValueList []*models.TemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&templateValueList)
	if err != nil {
		log.Logger.Error("Get tempalte_value data error", log.String("provider", providerName), log.String("tfstateVal", tfstateVal), log.Error(err))
		return
	}
	if len(templateValueList) == 0 {
		err = fmt.Errorf("template_value can not be found by provider:%s and tfstateValue:%s", providerName, tfstateVal)
		log.Logger.Warn("template_value can not be found by provider and tfstateValue", log.String("provider", providerName), log.String("tfstateValue", tfstateVal), log.Error(err))
		return
	}
	templateValueData := templateValueList[0]
	argKey = parameterData.Name
	argVal = templateValueData.Value
	return
}

func convertAttr(tfstateAttributeId string, sourceIdList map[string]bool, handlingSourceIds map[string]bool, providerName string, reqParam map[string]interface{}) (tfArguments map[string]interface{}, err error) {
	sqlCmd := `SELECT * FROM tfstate_attribute WHERE id=?`
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, tfstateAttributeId)
	var tfStateAttributeList []*models.TfstateAttributeTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&tfStateAttributeList)
	if err != nil {
		log.Logger.Error("Get tfstate_attribute data error", log.String("id", tfstateAttributeId), log.Error(err))
		return
	}
	if len(tfStateAttributeList) == 0 {
		err = fmt.Errorf("tfstate_attribute can not be found by id:%s", tfstateAttributeId)
		log.Logger.Warn("tfstate_attribute can not be found by id", log.String("id", tfstateAttributeId), log.Error(err))
		return
	}

	tfStateAttributeData := tfStateAttributeList[0]
	if _, ok := sourceIdList[tfStateAttributeData.Source]; !ok {
		err = fmt.Errorf("tfstate_attribute's source:%s is config error", tfStateAttributeData.Source)
		log.Logger.Error("tfstate_attribute's source is config error", log.String("tfstate_attribute_source", tfStateAttributeData.Source), log.Error(err))
		return
	}
	if _, ok := handlingSourceIds[tfStateAttributeData.Source]; !ok {
		err = fmt.Errorf("tfstate_attribute's source:%s is config error, dead loop", tfStateAttributeData.Source)
		log.Logger.Error("tfstate_attribute's source is config error, dead loop", log.String("tfstate_attribute_source", tfStateAttributeData.Source), log.Error(err))
		return
	}

	sqlCmd = "SELECT * FROM tf_argument WHERE source=?"
	var tfArgumentList []*models.TfArgumentTable
	paramArgs = []interface{}{}
	paramArgs = append(paramArgs, tfStateAttributeData.Source)
	err = x.SQL(sqlCmd, paramArgs...).Find(&tfArgumentList)
	if err != nil {
		log.Logger.Error("Get tf_argument list error", log.Error(err))
		return
	}
	if len(tfArgumentList) == 0 {
		err = fmt.Errorf("tf_argument list can not be found by tfstate_attribute source:%s", tfStateAttributeData.Source)
		log.Logger.Warn("tf_argument list can not be found by tfstate_attribute source", log.String("tfstate_attribute_source", tfStateAttributeData.Source), log.Error(err))
		return
	}

	tfArguments = make(map[string]interface{})
	// 循环处理每一个 tf_argument
	for i := range tfArgumentList {
		convertWay := tfArgumentList[i].ConvertWay
		var arg interface{}
		switch convertWay {
		case models.ConvertWay["Data"]:
			arg, err = convertData(tfArgumentList[i].Parameter, tfArgumentList[i].Source, reqParam)
		case models.ConvertWay["Template"]:
			arg, err = convertTemplate(tfArgumentList[i].Parameter, providerName, reqParam)
		case models.ConvertWay["Context"]:
			arg, err = convertContext(tfArgumentList[i].RelativeParameter, tfArgumentList[i], reqParam)
		case models.ConvertWay["Attr"]:
			handlingSourceIds[tfArgumentList[i].Source] = true
			arg, err = convertAttr(tfArgumentList[i].TfstateAttribute, sourceIdList, handlingSourceIds, providerName, reqParam)
		case models.ConvertWay["Direct"]:
			arg, err = convertDirect(tfArgumentList[i].Parameter, tfArgumentList[i].DefaultValue, reqParam)
		}
		if err != nil {
			log.Logger.Error("convert parameter:%s error", log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
			return
		}
		tfArguments[tfArgumentList[i].Name] = arg
		if convertWay == "default" && arg.(string) == "null" {
			delete(tfArguments, tfArgumentList[i].Name)
		}
	}
	return
}

func convertContext(parameterId string, tfArgument *models.TfArgumentTable, reqParam map[string]interface{}) (arg interface{}, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, parameterId)
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	if reqParam[parameterData.Name] == tfArgument.RelativeValue {
		arg = reqParam[parameterData.Name]
	}
	return
}

func reverseConvertContext(parameterId string, tfstateVal string) (argKey string, argVal string, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{parameterId}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	argKey = parameterData.Name
	argVal = tfstateVal
	return
}

func convertDirect(parameterId string, defaultValue string, reqParam map[string]interface{}) (arg interface{}, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, parameterId)
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	if reqParam[parameterData.Name] == "null" {
		arg = "null"
	} else if reqParam[parameterData.Name] == "" || reqParam[parameterData.Name] == "0" || reqParam[parameterData.Name] == "[]" {
		arg = defaultValue
	} else {
		arg = reqParam[parameterData.Name]
	}
	return
}

func reverseConvertDirect(parameterId string, tfstateVal string) (argKey string, argVal string, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{parameterId}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	argKey = parameterData.Name
	argVal = tfstateVal
	return
}
