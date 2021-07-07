package db

import (
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/cipher"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"os"
	"strings"
)

func GenProviderFile(providerName string, filePath string, region string) (err error) {
	file, err := os.OpenFile(filePath, os.O_CREATE, 0666)
	if err != nil {
		log.Logger.Error("open file error", log.String("file", filePath), log.Error(err))
		return
	}
	defer file.Close()
	return
}

func TerraformOperation(plugin string, action string, param map[string]interface{}) (rowData []*interface{}, err error) {
	// Get source list by plugin and action
	sqlCmd := `SELECT * FROM source WHERE plugin=? AND action=?`
	paramArgs := []interface{}{}
	paramArgs = append(paramArgs, plugin)
	paramArgs = append(paramArgs, action)
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

	// Get tf_argument_list by source_list
	sourceIdList := []string{}
	for i := range sourceList {
		sourceIdList = append(sourceIdList, sourceList[i].Id)
	}
	sourceIdStr := strings.Join(sourceIdList, "','")
	sqlCmd = "SELECT * FROM tf_argument WHERE source IN ('" + sourceIdStr + "')"
	var tfArgumentList []*models.TfArgumentTable
	err = x.SQL(sqlCmd).Find(&tfArgumentList)
	if err != nil {
		log.Logger.Error("Get tf_argument list error", log.Error(err))
		return
	}
	if len(tfArgumentList) == 0 {
		err = fmt.Errorf("tf_argument list can not be found by source:%s", sourceIdList)
		log.Logger.Warn("tf_argument list can not be found by source", log.String("source", sourceIdStr), log.Error(err))
		return
	}

	// Get providerInfo data
	sqlCmd = `SELECT * FROM provider_info WHERE id=?`
	paramArgs = []interface{}{}
	paramArgs = append(paramArgs, param["providerInfoId"])
	var providerInfoList []*models.ProviderInfoTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerInfoList)
	if err != nil {
		log.Logger.Error("Get providerInfo error", log.String("providerInfoId", param["providerInfoId"].(string)), log.Error(err))
		return
	}
	if len(providerInfoList) == 0 {
		err = fmt.Errorf("providerInfo can not be found by id:%s", param["providerInfoId"])
		log.Logger.Warn("providerInfo can not be found by id", log.String("id", param["providerInfoId"].(string)), log.Error(err))
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

	// Get provider data
	sqlCmd = `SELECT * FROM provider WHERE id=?`
	paramArgs = []interface{}{}
	paramArgs = append(paramArgs, providerInfoData.Provider)
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
	paramArgs = []interface{}{}
	paramArgs = append(paramArgs, param["regionId"])
	var regionList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&regionList)
	if err != nil {
		log.Logger.Error("Get region data error", log.String("regionId", param["regionId"].(string)), log.Error(err))
		return
	}
	if len(regionList) == 0 {
		err = fmt.Errorf("region can not be found by id:%s", param["regionId"])
		log.Logger.Warn("region can not be found by id", log.String("id", param["regionId"].(string)), log.Error(err))
		return
	}
	regionData := regionList[0]

	fmt.Printf("%v, %v, %v", providerSecretId, providerSecretKey, regionData)
	tfArguments := make(map[string]interface{})
	// 循环处理每一个 tf_argument
	for i := range tfArgumentList {
		convertWay := tfArgumentList[i].ConvertWay
		var arg interface{}
		switch convertWay {
		case "data":
			arg, err = convertData(tfArgumentList[i].Parameter, tfArgumentList[i].Source)
		case "template":
			arg, err = convertTemplate(tfArgumentList[i].Parameter, providerData.Name)
		case "context":
			arg, err = convertContext(tfArgumentList[i].Parameter, tfArgumentList[i].Name)
		case "pipe":
			sourceIdList := make(map[string]bool)
			for i := range sourceList {
				sourceIdList[sourceList[i].Id] = true
			}
			handlingSourceIds := make(map[string]bool)
			handlingSourceIds[tfArgumentList[i].Source] = true
			arg, err = convertPipe(tfArgumentList[i].TfstateAttribute, sourceIdList, handlingSourceIds, providerData.Name)
		case "default":
			arg, err = convertDefault(tfArgumentList[i].Parameter, tfArgumentList[i].DefaultValue)
		}
		if err != nil {
			log.Logger.Error("convert parameter:%s error", log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
			return
		}
		tfArguments[tfArgumentList[i].Name]	= arg
		if convertWay == "default" && arg.(string) == "null" {
			delete(tfArguments, tfArgumentList[i].Name)
		}
	}
	return
}


func convertData(parameterId string, source string) (arg interface{}, err error) {
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
	paramArgs = []interface{}{}
	paramArgs = append(paramArgs, source)
	paramArgs = append(paramArgs, parameterData.Value)
	var resourceDataList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		log.Logger.Error("Get resource_data error", log.String("source", source), log.String("resource_id", parameterData.Value), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		err = fmt.Errorf("resource_data can not be found by source:%s and resource_id:%s", source, parameterData.Value)
		log.Logger.Warn("resource_data can not be found by source and resource_id", log.String("source", source), log.String("value", parameterData.Value), log.Error(err))
		return
	}
	arg = resourceDataList[0].ResourceAssetId
	return
}

func convertTemplate(parameterId string, provider string) (arg interface{}, err error) {
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
	paramArgs = append(paramArgs, parameterData.Value)
	var templateValueList []*models.TemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&templateValueList)
	if err != nil {
		log.Logger.Error("Get tempalte_value data error", log.String("template", parameterData.Template), log.Error(err))
		return
	}
	if len(templateValueList) == 0 {
		err = fmt.Errorf("template_value can not be found by template:%s and value:%s", parameterData.Template, parameterData.Value)
		log.Logger.Warn("template_value can not be found by template and value", log.String("template", parameterData.Template), log.String("value", parameterData.Value), log.Error(err))
		return
	}
	templateValueData := templateValueList[0]

	sqlCmd = `SELECT * FROM provider_template_value WHERE template_value=? AND provider=?`
	paramArgs = []interface{}{}
	paramArgs = append(paramArgs, templateValueData.Id, provider)
	var providerTemplateValueList []*models.ProviderTemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerTemplateValueList)
	if err != nil {
		log.Logger.Error("Get provider_tempalte_value data error", log.String("template_value", templateValueData.Id), log.String("provider", provider), log.Error(err))
		return
	}
	if len(providerTemplateValueList) == 0 {
		err = fmt.Errorf("provider_template_value can not be found by template_value:%s and provider:%s", parameterData.Template)
		log.Logger.Warn("provider_template_value can not be found by template_value and provider", log.String("template_value", templateValueData.Id), log.String("provider", provider), log.Error(err))
		return
	}
	arg = providerTemplateValueList[0].Value
	return
}

func convertPipe(tfstateAttributeId string, sourceIdList map[string]bool, handlingSourceIds map[string]bool, providerName string) (tfArguments map[string]interface{}, err error) {
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
		case "data":
			arg, err = convertData(tfArgumentList[i].Parameter, tfArgumentList[i].Source)
		case "template":
			arg, err = convertTemplate(tfArgumentList[i].Parameter, providerName)
		case "context":
			arg, err = convertContext(tfArgumentList[i].Parameter, tfArgumentList[i].Name)
		case "pipe":
			handlingSourceIds[tfArgumentList[i].Source] = true
			arg, err = convertPipe(tfArgumentList[i].TfstateAttribute, sourceIdList, handlingSourceIds, providerName)
		case "default":
			arg, err = convertDefault(tfArgumentList[i].Parameter, tfArgumentList[i].DefaultValue)
		}
		if err != nil {
			log.Logger.Error("convert parameter:%s error", log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
			return
		}
		tfArguments[tfArgumentList[i].Name]	= arg
		if convertWay == "default" && arg.(string) == "null" {
			delete(tfArguments, tfArgumentList[i].Name)
		}
	}
	return
}

func convertContext(parameterId string, tfArgumentName string) (arg interface{}, err error) {
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
	if parameterData.Name == tfArgumentName {
		arg = parameterData.Value
	}
	return
}

func convertDefault(parameterId string, defaultValue string) (arg interface{}, err error) {
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
	if parameterData.Value == "null" {
		arg = "null"
	} else if parameterData.Value == "" || parameterData.Value == "0" || parameterData.Value == "[]" {
		arg = defaultValue
	} else {
		arg = parameterData.Value
	}
	return
}
