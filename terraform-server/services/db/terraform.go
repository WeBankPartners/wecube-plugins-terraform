package db

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/cipher"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/guid"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
)

func GenFile(content []byte, filePath string) (err error) {
	// 覆盖写入需加：os.O_TRUNC
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
	if err != nil {
		log.Logger.Error("Open file error", log.String("file", filePath), log.Error(err))
		return
	}
	defer file.Close()

	_, err = file.Write(content)
	if err != nil {
		log.Logger.Error("Write file error", log.String("file", filePath), log.Error(err))
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
		log.Logger.Error("Open file error", log.String("file", filePath), log.Error(err))
		return
	}
	defer file.Close()
	content, err = ioutil.ReadAll(file)
	return
}

func DelFile(filePath string) (err error) {
	_, err = os.Stat(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			return
		} else {
			err = fmt.Errorf("Os stat filePath: %s error: %s", filePath, err.Error())
			log.Logger.Error("Os stat filePath error", log.String("filePath", filePath), log.Error(err))
			return
		}
	}
	err = os.Remove(filePath)
	if err != nil {
		err = fmt.Errorf("Delete file: %s error: %s", filePath, err.Error())
		log.Logger.Error("Delete file error", log.String("filePath", filePath), log.Error(err))
	}
	return
}

func TerraformImport(dirPath, address, resourceAssetId string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " import " + address + " " + resourceAssetId
	cmd := exec.Command("/bin/bash", "-c", cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		outPutStr := string(stderr.Bytes())
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\ ]*)`)
		errorMsg := errorMsgRegx.FindStringSubmatch(outPutStr)
		errMsg := "Error:"
		for i := 1; i < len(errorMsg); i++ {
			errMsg += " "
			errMsg += errorMsg[i]
		}
		colorsCharRegx := regexp.MustCompile(`\[\d+m`)
		outPutErrMsg := colorsCharRegx.ReplaceAllLiteralString(errMsg, "")
		err = fmt.Errorf("Cmd:%s run failed: %s, ErrorMsg: %s", cmdStr, cmdErr.Error(), outPutErrMsg)
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.String("Error: ", outPutErrMsg), log.Error(cmdErr))
		return
	}
	return
}

func TerraformPlan(dirPath string) (destroyCnt int, err error) {
	// cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " plan -input=false -out=" + dirPath + "/planfile"
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " plan -input=false"
	cmd := exec.Command("/bin/bash", "-c", cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		outPutStr := string(stderr.Bytes())
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\ ]*)`)
		errorMsg := errorMsgRegx.FindStringSubmatch(outPutStr)
		errMsg := "Error:"
		for i := 1; i < len(errorMsg); i++ {
			errMsg += " "
			errMsg += errorMsg[i]
		}
		colorsCharRegx := regexp.MustCompile(`\[\d+m`)
		outPutErrMsg := colorsCharRegx.ReplaceAllLiteralString(errMsg, "")
		err = fmt.Errorf("Cmd:%s run failed: %s, ErrorMsg: %s", cmdStr, cmdErr.Error(), outPutErrMsg)
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.String("Error: ", outPutErrMsg), log.Error(cmdErr))
		return
	}
	// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
	filePath := dirPath + "/planfile"
	err = GenFile(stdout.Bytes(), filePath)
	if err != nil {
		err = fmt.Errorf("Write planfile error:%s", err.Error())
		log.Logger.Error("Write planfile error", log.String("planfile", filePath), log.Error(err))
		return
	}

	planFile, err := os.Open(filePath)
	if err != nil {
		err = fmt.Errorf("Open planfile error:%s", err.Error())
		log.Logger.Error("Open planfile error", log.String("planfile", filePath), log.Error(err))
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
					err = fmt.Errorf("Plan text:%s error", planStr)
					log.Logger.Error("Plan text error", log.String("planText", planStr), log.Error(err))
				}
			} else {
				err = fmt.Errorf("Plan text:%s error", planStr)
				log.Logger.Error("Plan text error", log.String("planText", planStr), log.Error(err))
			}
			return
		}
	}
	return
}

func TerraformApply(dirPath string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " apply -auto-approve"
	cmd := exec.Command("/bin/bash", "-c", cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		outPutStr := string(stderr.Bytes())
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\ ]*)`)
		errorMsg := errorMsgRegx.FindStringSubmatch(outPutStr)
		errMsg := "Error:"
		for i := 1; i < len(errorMsg); i++ {
			errMsg += " "
			errMsg += errorMsg[i]
		}
		colorsCharRegx := regexp.MustCompile(`\[\d+m`)
		outPutErrMsg := colorsCharRegx.ReplaceAllLiteralString(errMsg, "")
		err = fmt.Errorf("Cmd:%s run failed: %s, ErrorMsg: %s", cmdStr, cmdErr.Error(), outPutErrMsg)
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.String("Error: ", outPutErrMsg), log.Error(cmdErr))
		return
	}
	return
}

func TerraformDestroy(dirPath string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " destroy -auto-approve"
	cmd := exec.Command("/bin/bash", "-c", cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		outPutStr := string(stderr.Bytes())
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\ ]*)`)
		errorMsg := errorMsgRegx.FindStringSubmatch(outPutStr)
		errMsg := "Error:"
		for i := 1; i < len(errorMsg); i++ {
			errMsg += " "
			errMsg += errorMsg[i]
		}
		colorsCharRegx := regexp.MustCompile(`\[\d+m`)
		outPutErrMsg := colorsCharRegx.ReplaceAllLiteralString(errMsg, "")
		err = fmt.Errorf("Cmd:%s run failed: %s, ErrorMsg: %s", cmdStr, cmdErr.Error(), outPutErrMsg)
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.String("Error: ", outPutErrMsg), log.Error(cmdErr))
		return
	}
	return
}

func TerraformInit(dirPath string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " init"
	cmd := exec.Command("/bin/bash", "-c", cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		outPutStr := string(stderr.Bytes())
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\ ]*)`)
		errorMsg := errorMsgRegx.FindStringSubmatch(outPutStr)
		errMsg := "Error:"
		for i := 1; i < len(errorMsg); i++ {
			errMsg += " "
			errMsg += errorMsg[i]
		}
		colorsCharRegx := regexp.MustCompile(`\[\d+m`)
		outPutErrMsg := colorsCharRegx.ReplaceAllLiteralString(errMsg, "")
		err = fmt.Errorf("Cmd:%s run failed: %s, ErrorMsg: %s", cmdStr, cmdErr.Error(), outPutErrMsg)
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.String("Error: ", outPutErrMsg), log.Error(cmdErr))
		return
	}
	return
}

func handleTerraformApplyOrQuery(reqParam map[string]interface{},
	sourceData *models.SourceTable,
	providerData *models.ProviderTable,
	providerInfo *models.ProviderInfoTable,
	regionData *models.ResourceDataTable,
	action string, plugin string, dirPath string,
	interfaceData *models.InterfaceTable) (retOutput map[string]interface{}, err error) {
	retOutput = make(map[string]interface{})
	retOutput["callbackParameter"] = reqParam["callbackParameter"].(string)
	retOutput["errorCode"] = "1"
	retOutput["errorMessage"] = ""

	if plugin == "az" {
		retData, tmpErr := handleAzQuery(reqParam, dirPath, providerData, providerInfo, regionData, sourceData)
		if tmpErr != nil {
			err = fmt.Errorf("Handle Az query error:%s", tmpErr.Error())
			log.Logger.Warn("Handle Az query error", log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}
		for k, v := range retData {
			retOutput[k] = v
		}
		retOutput["errorCode"] = "0"
		return
	}

	// Get tf_argument_list by sourceId
	sourceIdStr := sourceData.Id
	sqlCmd := "SELECT * FROM tf_argument WHERE source IN ('" + sourceIdStr + "')"
	var tfArgumentList []*models.TfArgumentTable
	err = x.SQL(sqlCmd).Find(&tfArgumentList)
	if err != nil {
		err = fmt.Errorf("Get tf_argument list error:%s", err.Error())
		log.Logger.Error("Get tf_argument list error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	if len(tfArgumentList) == 0 {
		err = fmt.Errorf("Tf_argument list can not be found by source:%s", sourceIdStr)
		log.Logger.Warn("Tf_argument list can not be found by source", log.String("source", sourceIdStr), log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}

	// Get tfstate_attribute by sourceId
	sqlCmd = "SELECT * FROM tfstate_attribute WHERE source IN ('" + sourceIdStr + "')"
	var tfstateAttributeList []*models.TfstateAttributeTable
	err = x.SQL(sqlCmd).Find(&tfstateAttributeList)
	if err != nil {
		err = fmt.Errorf("Get tfstate_attribute list error:%s", err.Error())
		log.Logger.Error("Get tfstate_attribute list error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	if len(tfstateAttributeList) == 0 {
		err = fmt.Errorf("Tfstate_attribute list can not be found by source:%s", sourceIdStr)
		log.Logger.Warn("Tfstate_attribute list can not be found by source", log.String("source", sourceIdStr), log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}

	// Get parameter by interfaceId and type=out
	sqlCmd = "SELECT * FROM parameter WHERE interface=? and type=?"
	paramArgs := []interface{}{interfaceData.Id, "output"}
	var outPutParameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&outPutParameterList)
	if err != nil {
		err = fmt.Errorf("Get outPutParameter list error:%s", err.Error())
		log.Logger.Error("Get outPutParameter list error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	if len(outPutParameterList) == 0 {
		err = fmt.Errorf("OutPutParameter can not be found by interface:%s and type=out", interfaceData.Id)
		log.Logger.Warn("OutPutParameter can not be found by interface and type", log.String("interface", interfaceData.Id), log.String("type", "out"), log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}

	resourceId := reqParam["id"].(string)
	resourceAssetId := reqParam["asset_id"].(string)

	tfArguments := make(map[string]interface{})
	// 循环处理每一个 tf_argument
	for i := range tfArgumentList {
		if tfArgumentList[i].Parameter == "" {
			tfArguments[tfArgumentList[i].Name] = tfArgumentList[i].DefaultValue
			continue
		}
		// 查询 tfArgument 对应的 parameter
		sqlCmd = `SELECT * FROM parameter WHERE id=?`
		paramArgs = []interface{}{tfArgumentList[i].Parameter}
		var parameterList []*models.ParameterTable
		err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
		if err != nil {
			err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgumentList[i].Parameter, err.Error())
			log.Logger.Error("Get parameter data by id error", log.String("id", tfArgumentList[i].Parameter), log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}
		if len(parameterList) == 0 {
			err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgumentList[i].Parameter)
			log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgumentList[i].Parameter), log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}
		parameterData := parameterList[0]

		if _, ok := reqParam[parameterData.Name]; !ok {
			continue
		}

		convertWay := tfArgumentList[i].ConvertWay
		var arg interface{}
		var isDiscard = false
		switch convertWay {
		case models.ConvertWay["Data"]:
			// search resource_data table，get resource_asset_id by resource_id and resource(which is relative_source column in tf_argument table )
			arg, err = convertData(parameterData, tfArgumentList[i].RelativeSource, reqParam)
		case models.ConvertWay["Template"]:
			arg, err = convertTemplate(parameterData, providerData, reqParam)
		case models.ConvertWay["ContextData"]:
			arg, isDiscard, err = convertContextData(parameterData, tfArgumentList[i], reqParam)
		case models.ConvertWay["Attr"]:
			// search resouce_data table by relative_source and 输入的值, 获取 tfstat_file 字段内容,找到relative_tfstate_attribute id(search tfstate_attribute table) 对应的 name, 获取其在 tfstate_file 中的值
			arg, err = convertAttr(parameterData, tfArgumentList[i], reqParam)
		case models.ConvertWay["Direct"]:
			arg, err = convertDirect(parameterData, tfArgumentList[i].DefaultValue, reqParam)
		case models.ConvertWay["Function"]:
			arg, err = convertFunction(parameterData, tfArgumentList[i], reqParam)
		default:
			err = fmt.Errorf("The convertWay:%s of tfArgument:%s is invalid", convertWay, tfArgumentList[i].Name)
			log.Logger.Error("The convertWay of tfArgument is invalid", log.String("convertWay", convertWay), log.String("tfArgument", tfArgumentList[i].Name), log.Error(err))
			return
		}

		if isDiscard {
			continue
		}

		// handle tfArgument that is not in tf.json file
		if action == "apply" {
			if tfArgumentList[i].Name == sourceData.AssetIdAttribute {
				if parameterData.Name == "id" {
					if arg != nil {
						resourceId = arg.(string)
					}
				} else if parameterData.Name == "asset_id" {
					if arg != nil {
						resourceAssetId = arg.(string)
					}
				}
				continue
			}
		}

		if action == "query" {
			if arg == nil || arg == "" {
				continue
			}
		}

		if err != nil {
			err = fmt.Errorf("Convert parameter:%s error:%s", tfArgumentList[i].Parameter, err.Error())
			log.Logger.Error("Convert parameter error", log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}
		tfArguments[tfArgumentList[i].Name] = arg
		if arg != nil && convertWay == "direct" && parameterData.DataType == "string" && arg.(string) == "null" {
			delete(tfArguments, tfArgumentList[i].Name)
		}
		if parameterData.DataType == "object" || parameterData.DataType == "object_str" {
			var tmpVal map[string]interface{}
			err = json.Unmarshal([]byte(arg.(string)), &tmpVal)
			tfArguments[tfArgumentList[i].Name] = tmpVal
			if err != nil {
				err = fmt.Errorf("Unmarshal arg error:%s", err.Error())
				log.Logger.Error("Unmarshal arg error", log.Error(err))
				retOutput["errorMessage"] = err.Error()
				return
			}
		}
	}

	if action == "apply" {
		if resourceId == "" && resourceAssetId == "" {
			err = fmt.Errorf("ResourceId and resourceAssetId can not be all empty")
			log.Logger.Error("ResourceId and resourceAssetId can not be all empty")
			retOutput["errorMessage"] = err.Error()
			return
		}
		if resourceId == "" {
			resourceId = resourceAssetId
		}
	}

	_, err = os.Stat(dirPath)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.MkdirAll(dirPath, os.ModePerm)
			if err != nil {
				err = fmt.Errorf("Make dir: %s error: %s", dirPath, err.Error())
				log.Logger.Error("Make dir error", log.String("dirPath", dirPath), log.Error(err))
				retOutput["errorMessage"] = err.Error()
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", dirPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("dirPath", dirPath), log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}
	}

	// Gen tf.json file
	var tfFilePath, tfFileContentStr string
	tfFilePath = dirPath + "/" + sourceData.Name + ".tf.json"

	tfFileData := make(map[string]map[string]map[string]map[string]interface{})
	if action == "apply" {
		tfFileData["resource"] = make(map[string]map[string]map[string]interface{})
		tfFileData["resource"][sourceData.Name] = make(map[string]map[string]interface{})
		tfFileData["resource"][sourceData.Name][resourceId] = tfArguments
	} else {
		tfFileData["data"] = make(map[string]map[string]map[string]interface{})
		tfFileData["data"][sourceData.Name] = make(map[string]map[string]interface{})
		if resourceId == "" {
			resourceId = "_" + guid.CreateGuid()
		}
		tfFileData["data"][sourceData.Name][resourceId] = tfArguments
	}

	tfFileContent, err := json.Marshal(tfFileData)
	err = GenFile((tfFileContent), tfFilePath)
	if err != nil {
		err = fmt.Errorf("Gen tfFile: %s error: %s", tfFilePath, err.Error())
		log.Logger.Error("Gen tfFile error", log.String("tfFilePath", tfFilePath), log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	tfFileContentStr = string(tfFileContent)

	// Gen provider.tf.json
	providerFileData := make(map[string]map[string]map[string]interface{})
	providerFileData["provider"] = make(map[string]map[string]interface{})
	providerFileData["provider"][providerData.Name] = make(map[string]interface{})
	providerFileData["provider"][providerData.Name][providerData.SecretIdAttrName] = providerInfo.SecretId
	providerFileData["provider"][providerData.Name][providerData.SecretKeyAttrName] = providerInfo.SecretKey
	providerFileData["provider"][providerData.Name][providerData.RegionAttrName] = regionData.ResourceAssetId

	providerFileContent, err := json.Marshal(providerFileData)
	if err != nil {
		err = fmt.Errorf("Marshal providerFileData error: %s", err.Error())
		log.Logger.Error("Marshal providerFileData error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	providerFilePath := dirPath + "/provider.tf.json"
	err = GenFile(providerFileContent, providerFilePath)
	if err != nil {
		err = fmt.Errorf("Gen providerFile: %s error: %s", providerFilePath, err.Error())
		log.Logger.Error("Gen providerFile error", log.String("providerFilePath", providerFilePath), log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}

	// Gen version.tf
	terraformFilePath := models.Config.TerraformFilePath
	if terraformFilePath[len(terraformFilePath)-1] != '/' {
		terraformFilePath += "/"
	}
	if providerData.Name == "tencentcloud" {
		versionTfFilePath := terraformFilePath + "versiontf/" + providerData.Name + "/version.tf"
		versionTfFileContent, tmpErr := ReadFile(versionTfFilePath)
		if tmpErr != nil {
			err = fmt.Errorf("Read versionTfFile: %s error: %s", versionTfFilePath, tmpErr.Error())
			log.Logger.Error("Read versionTfFile error", log.String("versionTfFilePath", versionTfFilePath), log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}

		genVersionTfFilePath := dirPath + "/version.tf"
		err = GenFile(versionTfFileContent, genVersionTfFilePath)
		if err != nil {
			err = fmt.Errorf("Gen versionTfFile: %s error: %s", genVersionTfFilePath, err.Error())
			log.Logger.Error("Gen versionTfFile error", log.String("genVersionTfFilePath", genVersionTfFilePath), log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}
	}

	// Gen softlink of terraform provider file
	// targetTerraformProviderPath := dirPath + "/" + models.TerraformProviderPathDiffMap[providerData.Name] + providerData.Version + "/" + models.Config.TerraformProviderOsArch
	targetTerraformProviderPath := dirPath + "/" + models.TerraformProviderPathDiffMap[providerData.Name] + providerData.Version

	_, err = os.Stat(targetTerraformProviderPath)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.MkdirAll(targetTerraformProviderPath, os.ModePerm)
			if err != nil {
				err = fmt.Errorf("Make dir: %s error: %s", dirPath, err.Error())
				log.Logger.Error("Make dir error", log.String("dirPath", dirPath), log.Error(err))
				retOutput["errorMessage"] = err.Error()
				return
			}
			terraformProviderPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version + "/" + models.Config.TerraformProviderOsArch
			err = os.Symlink(terraformProviderPath, targetTerraformProviderPath+"/"+models.Config.TerraformProviderOsArch)
			if err != nil {
				err = fmt.Errorf("Make soft link : %s error: %s", targetTerraformProviderPath, err.Error())
				log.Logger.Error("Make soft link error", log.String("softLink", targetTerraformProviderPath), log.Error(err))
				retOutput["errorMessage"] = err.Error()
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", targetTerraformProviderPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("targetTerraformProviderPath", targetTerraformProviderPath), log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}
	}

	// Gen soft link for .terraform.lock.hcl
	targetTerraformLockHclPath := dirPath + "/.terraform.lock.hcl"
	_, err = os.Stat(targetTerraformLockHclPath)
	if err != nil {
		if os.IsNotExist(err) {
			terraformLockHclPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version + "/.terraform.lock.hcl"
			err = os.Symlink(terraformLockHclPath, targetTerraformLockHclPath)
			if err != nil {
				err = fmt.Errorf("Make soft link : %s error: %s", targetTerraformLockHclPath, err.Error())
				log.Logger.Error("Make soft link error", log.String("softLink", targetTerraformLockHclPath), log.Error(err))
				retOutput["errorMessage"] = err.Error()
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", targetTerraformLockHclPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("targetTerraformLockHclPath", targetTerraformLockHclPath), log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}
	}

	// test
	///*
	// terraform init
	err = TerraformInit(dirPath)
	if err != nil {
		err = fmt.Errorf("Do TerraformInit error:%s", err.Error())
		log.Logger.Error("Do TerraformInit error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}

	if resourceAssetId != "" && action == "apply" && plugin != "security_rule" {
		// terraform import when assetId has value
		err = TerraformImport(dirPath, sourceData.Name+"."+resourceId, resourceAssetId)
		if err != nil {
			err = fmt.Errorf("Do TerraformImport error:%s", err.Error())
			retOutput["errorMessage"] = err.Error()
			return
		}
	}

	// terraform plan
	destroyCnt, err := TerraformPlan(dirPath)
	if err != nil {
		err = fmt.Errorf("Do TerraformPlan error:%s", err.Error())
		log.Logger.Error("Do TerraformPlan error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	if destroyCnt > 0 && reqParam["confirmToken"] != "Y" {
		// 二次确认
		destroyCntStr := strconv.Itoa(destroyCnt)
		retOutput["errorMessage"] = destroyCntStr + "resource(s) will be destroy, please confirm again!"
		return
	}

	// terraform apply
	err = TerraformApply(dirPath)
	if err != nil {
		err = fmt.Errorf("Do TerraformApply error:%s", err.Error())
		log.Logger.Error("Do TerraformApply error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	//*/

	var tfstateObjectTypeAttribute *models.TfstateAttributeTable
	tfstateAttrParamMap := make(map[string]*models.TfstateAttributeTable)
	tfstateAttrNameMap := make(map[string]*models.TfstateAttributeTable)
	for _, v := range tfstateAttributeList {
		if v.Parameter == "" && v.ObjectName == "" {
			tfstateObjectTypeAttribute = v
		} else {
			tfstateAttrParamMap[v.Parameter] = v
		}
		tfstateAttrNameMap[v.Name] = v
	}

	sortTfstateAttributesList := []*models.SortTfstateAttributes{}
	sortTfstateAttrParamMap := make(map[string]*models.SortTfstateAttributes)
	for i := range tfstateAttributeList {
		curSortTfstateAttr := &models.SortTfstateAttributes{TfstateAttr: tfstateAttributeList[i], Point: 1000, IsExist: false}
		sortTfstateAttributesList = append(sortTfstateAttributesList, curSortTfstateAttr)
		sortTfstateAttrParamMap[tfstateAttributeList[i].Parameter] = curSortTfstateAttr
	}

	for _, v := range sortTfstateAttributesList {
		relativeParam := v.TfstateAttr.RelativeParameter
		if relativeParam != "" {
			maxPoint := sortTfstateAttrParamMap[relativeParam].Point
			if v.Point > maxPoint {
				maxPoint = v.Point
			}
			if sortTfstateAttrParamMap[relativeParam].IsExist {
				sortTfstateAttrParamMap[relativeParam].Point = maxPoint + 1
			} else {
				sortTfstateAttrParamMap[relativeParam].Point = maxPoint + 10
			}
			sortTfstateAttrParamMap[relativeParam].IsExist = true
		}
	}

	// sort sortTfstateAttributesList
	sort.Slice(sortTfstateAttributesList, func(i int, j int) bool {
		return sortTfstateAttributesList[i].Point > sortTfstateAttributesList[j].Point
	})

	orderTfstateAttrList := []*models.TfstateAttributeTable{}
	for _, v := range sortTfstateAttributesList {
		orderTfstateAttrList = append(orderTfstateAttrList, v.TfstateAttr)
	}

	outPutParameterNameMap := make(map[string]*models.ParameterTable)
	outPutParameterIdMap := make(map[string]*models.ParameterTable)
	for _, v := range outPutParameterList {
		outPutParameterNameMap[v.Name] = v
		outPutParameterIdMap[v.Id] = v
	}

	// Read terraform.tfstate 文件
	var tfstateFilePath string
	tfstateFilePath = dirPath + "/terraform.tfstate"
	tfstateFileData, err := ReadFile(tfstateFilePath)
	if err != nil {
		err = fmt.Errorf("Read tfstate file error:%s", err.Error())
		log.Logger.Error("Read tfstate file error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	tfstateFileContentStr := string(tfstateFileData)
	var unmarshalTfstateFileData models.TfstateFileData
	err = json.Unmarshal(tfstateFileData, &unmarshalTfstateFileData)
	if err != nil {
		err = fmt.Errorf("Unmarshal tfstate file data error:%s", err.Error())
		log.Logger.Error("Unmarshal tfstate file data error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}
	var tfstateFileAttributes map[string]interface{}
	tfstateFileAttributes = unmarshalTfstateFileData.Resources[0].Instances[0].Attributes

	if action == "apply" {
		// 记录到 resource_data table
		resourceDataId := guid.CreateGuid()
		resourceDataSourceId := sourceData.Id
		resourceDataResourceId := resourceId
		resourceDataResourceAssetId := tfstateFileAttributes[sourceData.AssetIdAttribute]
		createTime := time.Now().Format(models.DateTimeFormat)
		createUser := reqParam["operator_user"].(string)

		_, err = x.Exec("INSERT INTO resource_data(id,resource,resource_id,resource_asset_id,tf_file,tf_state_file,region_id,create_time,create_user,update_time) VALUE (?,?,?,?,?,?,?,?,?,?)",
			resourceDataId, resourceDataSourceId, resourceDataResourceId, resourceDataResourceAssetId, tfFileContentStr, tfstateFileContentStr, regionData.RegionId, createTime, createUser, createTime)
		if err != nil {
			err = fmt.Errorf("Try to create resource_data fail,%s ", err.Error())
			log.Logger.Error("Try to create resource_data fail", log.Error(err))
			retOutput["errorMessage"] = err.Error()
		}
	}

	if tfstateObjectTypeAttribute == nil {
		var outPutArgs map[string]interface{}
		parentObjectName := ""
		paramCnt := 0
		outPutArgs, err = handleReverseConvert(outPutParameterNameMap,
			outPutParameterIdMap,
			tfstateAttrParamMap,
			tfstateAttrNameMap,
			reqParam,
			providerData,
			tfstateFileAttributes,
			action,
			parentObjectName,
			orderTfstateAttrList,
			&paramCnt)
		if err != nil {
			err = fmt.Errorf("Handle reverse convert error:%s", err.Error())
			log.Logger.Error("Handle revese convert  error", log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}

		// handle outPutArgs
		outPutResultList, _ := handleOutPutArgs(outPutArgs, outPutParameterNameMap, tfstateAttrParamMap, reqParam)
		/*
		outPutResultList := []map[string]interface{}{}
		// flat outPutParam data
		flatOutPutArgs, _ := handleFlatOutPutParam(outPutArgs)

		// delete the item that id is nil or nil []interface{}
		tmpOutPutResultList := []map[string]interface{}{}
		for i := range flatOutPutArgs {
			if isResultIdValid(flatOutPutArgs[i]["id"]) == false {
				continue
			}
			tmpOutPutResultList = append(tmpOutPutResultList, flatOutPutArgs[i])
		}

		// 将数组类型的值进行一一映射
		mapOutPutArgs, _ := handleSliceMapOutPutParam(tmpOutPutResultList)

		// outPutParam 不在 tfstateFile 返回结果中的字段，用输入传进来的值
		for i := range mapOutPutArgs {
			for k, v := range outPutParameterNameMap {
				if _, okParam := tfstateAttrParamMap[v.Id]; !okParam {
					mapOutPutArgs[i][k] = reqParam[k]
				}
			}
			outPutResultList = append(outPutResultList, mapOutPutArgs[i])
		}

		 */
		retOutput[models.TerraformOutPutPrefix] = outPutResultList
	} else {
		// 处理结果字段为 object 的情况
		var tfstateResult []map[string]interface{}
		if tfstateObjectTypeAttribute.IsMulti == "Y" {
			var tmpData []map[string]interface{}
			tmpMarshal, _ := json.Marshal(tfstateFileAttributes[tfstateObjectTypeAttribute.Name])
			json.Unmarshal(tmpMarshal, &tmpData)
			for i := range tmpData {
				tfstateResult = append(tfstateResult, tmpData[i])
			}
		} else {
			var tmpData map[string]interface{}
			tmpMarshal, _ := json.Marshal(tfstateFileAttributes[tfstateObjectTypeAttribute.Name])
			json.Unmarshal(tmpMarshal, &tmpData)
			tfstateResult = append(tfstateResult, tmpData)
		}
		outPutResultList := []map[string]interface{}{}
		for i := range tfstateResult {
			var outPutArgs map[string]interface{}
			parentObjectName := tfstateObjectTypeAttribute.Id
			paramCnt := 0
			outPutArgs, err = handleReverseConvert(outPutParameterNameMap,
				outPutParameterIdMap,
				tfstateAttrParamMap,
				tfstateAttrNameMap,
				reqParam,
				providerData,
				tfstateResult[i],
				action,
				parentObjectName,
				orderTfstateAttrList,
				&paramCnt)

			if err != nil {
				err = fmt.Errorf("Handle reverse convert error:%s", err.Error())
				log.Logger.Error("Handle revese convert  error", log.Error(err))
				retOutput["errorMessage"] = err.Error()
				return
			}

			// handle outPutArgs
			tmpOutPutResult, _ := handleOutPutArgs(outPutArgs, outPutParameterNameMap, tfstateAttrParamMap, reqParam)
			/*
			outPutResultList := []map[string]interface{}{}
			// flat outPutParam data
			flatOutPutArgs, _ := handleFlatOutPutParam(outPutArgs)

			for i := range flatOutPutArgs {
				// outPutParam 不在 tfstateFile 返回结果中的字段，用输入传进来的值
				for k, v := range outPutParameterNameMap {
					if _, okParam := tfstateAttrParamMap[v.Id]; !okParam {
						flatOutPutArgs[i][k] = reqParam[k]
					}
				}
				outPutResultList = append(outPutResultList, flatOutPutArgs[i])
			}
			 */
			outPutResultList = append(outPutResultList, tmpOutPutResult...)
			//retOutput[models.TerraformOutPutPrefix] = outPutResultList
		}
		retOutput[models.TerraformOutPutPrefix] = outPutResultList
	}

	// delete provider.tf.json
	err = DelFile(providerFilePath)
	if err != nil {
		err = fmt.Errorf("Delete provider.tf.json file:%s error:%s", providerFilePath, err.Error())
		log.Logger.Error("Delete provider.tf.json file error", log.String("providerFilePath", providerFilePath), log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
	}

	retOutput["errorCode"] = "0"
	return
}

func handleOutPutArgs(outPutArgs map[string]interface{},
					  outPutParameterNameMap map[string]*models.ParameterTable,
					  tfstateAttrParamMap map[string]*models.TfstateAttributeTable,
					  reqParam map[string]interface{}) (outPutResultList []map[string]interface{}, err error) {
	outPutResultList = []map[string]interface{}{}
	// flat outPutParam data
	flatOutPutArgs, _ := handleFlatOutPutParam(outPutArgs)

	// delete the item that id is nil or nil []interface{}
	tmpOutPutResultList := []map[string]interface{}{}
	for i := range flatOutPutArgs {
		if isResultIdValid(flatOutPutArgs[i]["id"]) == false {
			continue
		}
		tmpOutPutResultList = append(tmpOutPutResultList, flatOutPutArgs[i])
	}

	// 将数组类型的值进行一一映射
	mapOutPutArgs, _ := handleSliceMapOutPutParam(tmpOutPutResultList)

	// outPutParam 不在 tfstateFile 返回结果中的字段，用输入传进来的值
	for i := range mapOutPutArgs {
		for k, v := range outPutParameterNameMap {
			if _, okParam := tfstateAttrParamMap[v.Id]; !okParam {
				mapOutPutArgs[i][k] = reqParam[k]
			}
		}
		outPutResultList = append(outPutResultList, mapOutPutArgs[i])
	}
	return
}

func isResultIdValid(outPutIdVal interface{}) bool {
	if outPutIdVal == nil {
		return false
	}
	if _, ok := outPutIdVal.([]interface{}); ok {
		tmpVal := outPutIdVal.([]interface{})
		if len(tmpVal) == 0 {
			return false
		}
		for i := range tmpVal {
			if isResultIdValid(tmpVal[i]) == false {
				return false
			}
		}
	}
	return true
}

func handleFlatOutPutParam(outPutArgs map[string]interface{}) (retOutPutArgs []map[string]interface{}, err error) {
	flatParams := make(map[string]interface{})
	for k := range outPutArgs {
		if strings.Contains(k, models.TerraformOutPutPrefix) == false {
			flatParams[k] = outPutArgs[k]
		}
	}
	hasResultList := false
	for k, v := range outPutArgs {
		if strings.Contains(k, models.TerraformOutPutPrefix) {
			hasResultList = true
			var tmpData []map[string]interface{}
			tmpMarshal, _ := json.Marshal(v)
			json.Unmarshal(tmpMarshal, &tmpData)
			for i := range tmpData {
				ret, _ := handleFlatOutPutParam(tmpData[i])
				for j := range ret {
					for fp := range flatParams {
						ret[j][fp] = flatParams[fp]
					}
					retOutPutArgs = append(retOutPutArgs, ret[j])
				}
			}
		}
	}
	if !hasResultList {
		retOutPutArgs = append(retOutPutArgs, flatParams)
	}
	return
}

func handleSliceMapOutPutParam(outPutArgs []map[string]interface{}) (retOutPutArgs []map[string]interface{}, err error) {
	for _, retArg := range outPutArgs {
		sliceKeys := make(map[string]interface{})
		nonSliceKeys := make(map[string]interface{})

		cnt := 0
		for k, v := range retArg {
			if _, ok := v.([]interface{}); ok /*&& len(v.([]interface{})) > 0*/ {
				sliceKeys[k] = v
				cnt = len(v.([]interface{}))
			} else {
				nonSliceKeys[k] = v
			}
		}

		if cnt == 0 {
			retOutPutArgs = append(retOutPutArgs, nonSliceKeys)
			continue
		}

		for i := 0; i < cnt; i++ {
			curResult := make(map[string]interface{})
			hasSliceVal := false
			for k1, v1 := range sliceKeys {
				curResult[k1] = v1.([]interface{})[i]
				if _, ok := curResult[k1].([]interface{}); ok /*&& len(curResult[k1].([]interface{})) > 0*/ {
					hasSliceVal = true
				}
			}
			for k1, v1 := range nonSliceKeys {
				curResult[k1] = v1
			}
			if hasSliceVal {
				tmpInput := []map[string]interface{}{curResult}
				tmpRet, _ := handleSliceMapOutPutParam(tmpInput)
				retOutPutArgs = append(retOutPutArgs, tmpRet...)
			} else {
				retOutPutArgs = append(retOutPutArgs, curResult)
			}
		}
	}
	return
}

func handleAzQuery(reqParam map[string]interface{},
	workDirPath string,
	providerData *models.ProviderTable,
	providerInfo *models.ProviderInfoTable,
	regionData *models.ResourceDataTable,
	sourceData *models.SourceTable) (rowData map[string]interface{}, err error) {
	rowData = make(map[string]interface{})
	_, err = os.Stat(workDirPath)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.MkdirAll(workDirPath, os.ModePerm)
			if err != nil {
				err = fmt.Errorf("Make dir: %s error: %s", workDirPath, err.Error())
				log.Logger.Error("Make dir error", log.String("workDirPath", workDirPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", workDirPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("workDirPath", workDirPath), log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
	}

	// Gen provider.tf.json
	providerFileData := make(map[string]map[string]map[string]interface{})
	providerFileData["provider"] = make(map[string]map[string]interface{})
	providerFileData["provider"][providerData.Name] = make(map[string]interface{})
	providerFileData["provider"][providerData.Name][providerData.SecretIdAttrName] = providerInfo.SecretId
	providerFileData["provider"][providerData.Name][providerData.SecretKeyAttrName] = providerInfo.SecretKey
	providerFileData["provider"][providerData.Name][providerData.RegionAttrName] = regionData.ResourceAssetId

	providerFileContent, tmpErr := json.Marshal(providerFileData)
	if tmpErr != nil {
		err = fmt.Errorf("Marshal providerFileData error: %s", tmpErr.Error())
		log.Logger.Error("Marshal providerFileData error", log.Error(err))
		return
	}
	providerFilePath := workDirPath + "/provider.tf.json"
	err = GenFile(providerFileContent, providerFilePath)
	if err != nil {
		err = fmt.Errorf("Gen providerFile: %s error: %s", providerFilePath, err.Error())
		log.Logger.Error("Gen providerFile error", log.String("providerFilePath", providerFilePath), log.Error(err))
		return
	}

	// Gen version.tf
	terraformFilePath := models.Config.TerraformFilePath
	if terraformFilePath[len(terraformFilePath)-1] != '/' {
		terraformFilePath += "/"
	}
	if providerData.Name == "tencentcloud" {
		versionTfFilePath := terraformFilePath + "versiontf/" + providerData.Name + "/version.tf"
		versionTfFileContent, tmpErr := ReadFile(versionTfFilePath)
		if tmpErr != nil {
			err = fmt.Errorf("Read versionTfFile: %s error: %s", versionTfFilePath, tmpErr.Error())
			log.Logger.Error("Read versionTfFile error", log.String("versionTfFilePath", versionTfFilePath), log.Error(err))
			return
		}

		genVersionTfFilePath := workDirPath + "/version.tf"
		err = GenFile(versionTfFileContent, genVersionTfFilePath)
		if err != nil {
			err = fmt.Errorf("Gen versionTfFile: %s error: %s", genVersionTfFilePath, err.Error())
			log.Logger.Error("Gen versionTfFile error", log.String("genVersionTfFilePath", genVersionTfFilePath), log.Error(err))
			return
		}
	}

	// Gen softlink of terraform provider file
	// targetTerraformProviderPath := workDirPath + "/" + models.TerraformProviderPathDiffMap[providerData.Name] + providerData.Version + "/" + models.Config.TerraformProviderOsArch
	targetTerraformProviderPath := workDirPath + "/" + models.TerraformProviderPathDiffMap[providerData.Name] + providerData.Version

	_, err = os.Stat(targetTerraformProviderPath)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.MkdirAll(targetTerraformProviderPath, os.ModePerm)
			if err != nil {
				err = fmt.Errorf("Make dir: %s error: %s", workDirPath, err.Error())
				log.Logger.Error("Make dir error", log.String("dirPath", workDirPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
			terraformProviderPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version + "/" + models.Config.TerraformProviderOsArch
			err = os.Symlink(terraformProviderPath, targetTerraformProviderPath+"/"+models.Config.TerraformProviderOsArch)
			if err != nil {
				err = fmt.Errorf("Make soft link : %s error: %s", targetTerraformProviderPath, err.Error())
				log.Logger.Error("Make soft link error", log.String("softLink", targetTerraformProviderPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", targetTerraformProviderPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("targetTerraformProviderPath", targetTerraformProviderPath), log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
	}
	// Gen soft link for .terraform.lock.hcl
	targetTerraformLockHclPath := workDirPath + "/.terraform.lock.hcl"
	_, err = os.Stat(targetTerraformLockHclPath)
	if err != nil {
		if os.IsNotExist(err) {
			terraformLockHclPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version + "/.terraform.lock.hcl"
			err = os.Symlink(terraformLockHclPath, targetTerraformLockHclPath)
			if err != nil {
				err = fmt.Errorf("Make soft link : %s error: %s", targetTerraformLockHclPath, err.Error())
				log.Logger.Error("Make soft link error", log.String("softLink", targetTerraformLockHclPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", targetTerraformLockHclPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("targetTerraformLockHclPath", targetTerraformLockHclPath), log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
	}

	sourceName := sourceData.Name
	// Gen .tf 文件, 然后执行 terraform import cmd
	uuid := "_" + guid.CreateGuid()
	tfFilePath := workDirPath + "/" + sourceName + ".tf"
	tfFileContent := "data " + sourceName + " " + uuid + " {}"

	GenFile([]byte(tfFileContent), tfFilePath)
	err = TerraformInit(workDirPath)
	if err != nil {
		err = fmt.Errorf("Do TerraformInit error:%s", err.Error())
		log.Logger.Error("Do TerraformInit error", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}

	err = TerraformApply(workDirPath)
	if err != nil {
		err = fmt.Errorf("Do TerraformApply error:%s", err.Error())
		log.Logger.Error("Do TerraformApply error", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}

	// Read terraform.tfstate 文件
	var tfstateFilePath string
	tfstateFilePath = workDirPath + "/terraform.tfstate"
	tfstateFileData, err := ReadFile(tfstateFilePath)
	if err != nil {
		err = fmt.Errorf("Read tfstate file error:%s", err.Error())
		log.Logger.Error("Read tfstate file error", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	//tfstateFileContentStr := string(tfstateFileData)
	var unmarshalTfstateFileData models.TfstateFileData
	err = json.Unmarshal(tfstateFileData, &unmarshalTfstateFileData)
	if err != nil {
		err = fmt.Errorf("Unmarshal tfstate file data error:%s", err.Error())
		log.Logger.Error("Unmarshal tfstate file data error", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	var tfstateFileAttributes map[string]interface{}
	tfstateFileAttributes = unmarshalTfstateFileData.Resources[0].Instances[0].Attributes
	rowData["az"] = tfstateFileAttributes["zones"]

	// Del provider file
	err = DelFile(providerFilePath)
	if err != nil {
		err = fmt.Errorf("Do delete provider file error: %s", err.Error())
		log.Logger.Error("Do delete provider file error", log.Error(err))
		rowData["errorMessage"] = err.Error()
	}
	return
}

func RegionApply(reqParam map[string]interface{}, interfaceData *models.InterfaceTable) (rowData map[string]interface{}, err error) {
	rowData = make(map[string]interface{})
	rowData["callbackParameter"] = reqParam["callbackParameter"].(string)
	rowData["errorCode"] = "1"
	rowData["errorMessage"] = ""

	providerInfoId := reqParam["provider_info"].(string)
	// Get providerInfo data
	sqlCmd := `SELECT * FROM provider_info WHERE id=?`
	paramArgs := []interface{}{providerInfoId}
	var providerInfoList []*models.ProviderInfoTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerInfoList)
	if err != nil {
		err = fmt.Errorf("Get providerInfo by id:%s error:%s", providerInfoId, err.Error())
		log.Logger.Error("Get providerInfo by id error", log.String("id", providerInfoId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(providerInfoList) == 0 {
		err = fmt.Errorf("ProviderInfo can not be found by id:%s", providerInfoId)
		log.Logger.Warn("ProviderInfo can not be found by id", log.String("id", providerInfoId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerInfoData := providerInfoList[0]

	// Get provider data
	sqlCmd = `SELECT * FROM provider WHERE id=?`
	paramArgs = []interface{}{providerInfoData.Provider}
	var providerList []*models.ProviderTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerList)
	if err != nil {
		err = fmt.Errorf("Get provider by id:%s error:%s", providerInfoData.Provider, err.Error())
		log.Logger.Error("Get provider by id error", log.String("id", providerInfoData.Provider), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(providerList) == 0 {
		err = fmt.Errorf("Provider can not be found by id:%s", providerInfoData.Provider)
		log.Logger.Warn("Provider can not be found by id", log.String("id", providerInfoData.Provider), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerData := providerList[0]

	enCodeproviderTfContent := ""

	// get source data by interfaceId and providerId
	sqlCmd = `SELECT * FROM source WHERE interface=? AND provider=?`
	paramArgs = []interface{}{interfaceData.Id, providerData.Id}
	var sourceList []*models.SourceTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&sourceList)
	if err != nil {
		err = fmt.Errorf("Get source by interface:%s and provider:%s error:%s", interfaceData.Id, providerData.Id, err.Error())
		log.Logger.Error("Get source by interface and provider error", log.String("interface", interfaceData.Id), log.String("provider", providerData.Id), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(sourceList) == 0 {
		err = fmt.Errorf("Provider can not be found by interface:%s and provider:%s", interfaceData.Id, providerData.Id)
		log.Logger.Warn("Provider can not be found by interface and provider", log.String("interface", interfaceData.Id), log.String("provider", providerData.Id), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	sourceData := sourceList[0]

	uuid := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	resourceId := reqParam["id"].(string)
	resourceAssetId := reqParam["asset_id"].(string)
	createUser := reqParam["operator_user"].(string)

	_, err = x.Exec("INSERT INTO resource_data(id,resource,resource_id,resource_asset_id,tf_file,region_id,create_time,create_user,update_time) VALUE (?,?,?,?,?,?,?,?,?)",
		uuid, sourceData.Id, resourceId, resourceAssetId, enCodeproviderTfContent, resourceId, createTime, createUser, createTime)
	if err != nil {
		err = fmt.Errorf("Try to create resource_data fail,%s ", err.Error())
		log.Logger.Error("Try to create resource_data fail", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}

	rowData["errorCode"] = "0"
	rowData["asset_id"] = resourceAssetId
	rowData["id"] = resourceId
	return
}

func handleApplyOrQuery(action string, reqParam map[string]interface{}, sourceData *models.SourceTable) (rowData map[string]interface{}, err error) {
	rowData = make(map[string]interface{})
	rowData["callbackParameter"] = reqParam["callbackParameter"].(string)
	rowData["errorCode"] = "1"
	rowData["errorMessage"] = ""

	if action == "apply" {
		uuid := guid.CreateGuid()
		createTime := time.Now().Format(models.DateTimeFormat)
		resourceId := reqParam["id"].(string)
		resourceAssetId := reqParam["asset_id"].(string)
		createUser := reqParam["operator_user"].(string)
		regionId := reqParam["region_id"].(string)

		_, err = x.Exec("INSERT INTO resource_data(id,resource,resource_id,resource_asset_id,region_id,create_time,create_user,update_time) VALUE (?,?,?,?,?,?,?,?)",
			uuid, sourceData.Id, resourceId, resourceAssetId, regionId, createTime, createUser, createTime)
		if err != nil {
			err = fmt.Errorf("Try to create resource_data fail,%s ", err.Error())
			log.Logger.Error("Try to create resource_data fail", log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
		rowData["errorCode"] = "0"
		rowData["asset_id"] = resourceAssetId
		rowData["id"] = resourceId
	} else if action == "query" {
		resourceId := reqParam["id"].(string)
		sqlCmd := `SELECT * FROM resource_data WHERE resource_id=?`
		paramArgs := []interface{}{resourceId}
		var resourceDataList []*models.ResourceDataTable
		err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
		if err != nil {
			err = fmt.Errorf("Get resource_data by resourceId:%s error:%s", resourceId, err.Error())
			log.Logger.Error("Get resource_data by resourceId error", log.String("resourceId", resourceId), log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
		if len(resourceDataList) == 0 {
			err = fmt.Errorf("ResourceData can not be found by resourceId:%s", resourceId)
			log.Logger.Warn("ResourceData can not be found by resourceId", log.String("resourceId", resourceId), log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
		resourceData := resourceDataList[0]
		rowData["errorCode"] = "0"
		rowData["asset_id"] = resourceData.ResourceAssetId
		rowData["id"] = resourceId
		rowData["region_id"] = resourceData.RegionId
	}
	return
}

func handleDestroy(workDirPath string,
	sourceData *models.SourceTable,
	providerData *models.ProviderTable,
	providerInfo *models.ProviderInfoTable,
	regionData *models.ResourceDataTable,
	reqParam map[string]interface{},
	plugin string) (rowData map[string]interface{}, err error) {
	rowData = make(map[string]interface{})
	rowData["callbackParameter"] = reqParam["callbackParameter"].(string)
	rowData["errorCode"] = "1"
	rowData["errorMessage"] = ""

	// Get resource_asset_id by resourceId
	resourceId := reqParam["id"].(string)
	sqlCmd := `SELECT * FROM resource_data WHERE resource_id=?`
	paramArgs := []interface{}{resourceId}
	var resourceDataInfoList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataInfoList)
	if err != nil {
		err = fmt.Errorf("Get resourceDataInfo by resource_id:%s error:%s", resourceId, err.Error())
		log.Logger.Error("Get resourceDataInfo by resource_id error", log.String("resource_id", resourceId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(resourceDataInfoList) == 0 {
		err = fmt.Errorf("ResourceDataInfo can not be found by resource_id:%s", resourceId)
		log.Logger.Warn("ResourceDataInfo can not be found by resource_id", log.String("resource_id", resourceId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	resourceData := resourceDataInfoList[0]
	rowData["id"] = resourceId

	if sourceData.TerraformUsed == "Y" {
		_, err = os.Stat(workDirPath)
		if err != nil {
			if os.IsNotExist(err) {
				err = os.MkdirAll(workDirPath, os.ModePerm)
				if err != nil {
					err = fmt.Errorf("Make dir: %s error: %s", workDirPath, err.Error())
					log.Logger.Error("Make dir error", log.String("workDirPath", workDirPath), log.Error(err))
					rowData["errorMessage"] = err.Error()
					return
				}
			} else {
				err = fmt.Errorf("Os stat dir: %s error: %s", workDirPath, err.Error())
				log.Logger.Error("Os stat dir error", log.String("workDirPath", workDirPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
		}

		// Gen provider.tf.json
		providerFileData := make(map[string]map[string]map[string]interface{})
		providerFileData["provider"] = make(map[string]map[string]interface{})
		providerFileData["provider"][providerData.Name] = make(map[string]interface{})
		providerFileData["provider"][providerData.Name][providerData.SecretIdAttrName] = providerInfo.SecretId
		providerFileData["provider"][providerData.Name][providerData.SecretKeyAttrName] = providerInfo.SecretKey
		providerFileData["provider"][providerData.Name][providerData.RegionAttrName] = regionData.ResourceAssetId

		providerFileContent, tmpErr := json.Marshal(providerFileData)
		if tmpErr != nil {
			err = fmt.Errorf("Marshal providerFileData error: %s", tmpErr.Error())
			log.Logger.Error("Marshal providerFileData error", log.Error(err))
			return
		}
		providerFilePath := workDirPath + "/provider.tf.json"
		err = GenFile(providerFileContent, providerFilePath)
		if err != nil {
			err = fmt.Errorf("Gen providerFile: %s error: %s", providerFilePath, err.Error())
			log.Logger.Error("Gen providerFile error", log.String("providerFilePath", providerFilePath), log.Error(err))
			return
		}

		// Gen version.tf
		terraformFilePath := models.Config.TerraformFilePath
		if terraformFilePath[len(terraformFilePath)-1] != '/' {
			terraformFilePath += "/"
		}
		if providerData.Name == "tencentcloud" {
			versionTfFilePath := terraformFilePath + "versiontf/" + providerData.Name + "/version.tf"
			versionTfFileContent, tmpErr := ReadFile(versionTfFilePath)
			if tmpErr != nil {
				err = fmt.Errorf("Read versionTfFile: %s error: %s", versionTfFilePath, tmpErr.Error())
				log.Logger.Error("Read versionTfFile error", log.String("versionTfFilePath", versionTfFilePath), log.Error(err))
				return
			}

			genVersionTfFilePath := workDirPath + "/version.tf"
			err = GenFile(versionTfFileContent, genVersionTfFilePath)
			if err != nil {
				err = fmt.Errorf("Gen versionTfFile: %s error: %s", genVersionTfFilePath, err.Error())
				log.Logger.Error("Gen versionTfFile error", log.String("genVersionTfFilePath", genVersionTfFilePath), log.Error(err))
				return
			}
		}

		// Gen softlink of terraform provider file
		// targetTerraformProviderPath := workDirPath + "/" + models.TerraformProviderPathDiffMap[providerData.Name] + providerData.Version + "/" + models.Config.TerraformProviderOsArch
		targetTerraformProviderPath := workDirPath + "/" + models.TerraformProviderPathDiffMap[providerData.Name] + providerData.Version

		_, err = os.Stat(targetTerraformProviderPath)
		if err != nil {
			if os.IsNotExist(err) {
				err = os.MkdirAll(targetTerraformProviderPath, os.ModePerm)
				if err != nil {
					err = fmt.Errorf("Make dir: %s error: %s", workDirPath, err.Error())
					log.Logger.Error("Make dir error", log.String("dirPath", workDirPath), log.Error(err))
					rowData["errorMessage"] = err.Error()
					return
				}
				terraformProviderPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version + "/" + models.Config.TerraformProviderOsArch
				err = os.Symlink(terraformProviderPath, targetTerraformProviderPath+"/"+models.Config.TerraformProviderOsArch)
				if err != nil {
					err = fmt.Errorf("Make soft link : %s error: %s", targetTerraformProviderPath, err.Error())
					log.Logger.Error("Make soft link error", log.String("softLink", targetTerraformProviderPath), log.Error(err))
					rowData["errorMessage"] = err.Error()
					return
				}
			} else {
				err = fmt.Errorf("Os stat dir: %s error: %s", targetTerraformProviderPath, err.Error())
				log.Logger.Error("Os stat dir error", log.String("targetTerraformProviderPath", targetTerraformProviderPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
		}
		// Gen soft link for .terraform.lock.hcl
		targetTerraformLockHclPath := workDirPath + "/.terraform.lock.hcl"
		_, err = os.Stat(targetTerraformLockHclPath)
		if err != nil {
			if os.IsNotExist(err) {
				terraformLockHclPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version + "/.terraform.lock.hcl"
				err = os.Symlink(terraformLockHclPath, targetTerraformLockHclPath)
				if err != nil {
					err = fmt.Errorf("Make soft link : %s error: %s", targetTerraformLockHclPath, err.Error())
					log.Logger.Error("Make soft link error", log.String("softLink", targetTerraformLockHclPath), log.Error(err))
					rowData["errorMessage"] = err.Error()
					return
				}
			} else {
				err = fmt.Errorf("Os stat dir: %s error: %s", targetTerraformLockHclPath, err.Error())
				log.Logger.Error("Os stat dir error", log.String("targetTerraformLockHclPath", targetTerraformLockHclPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
		}

		sourceName := sourceData.Name
		// Gen .tf 文件, 然后执行 terraform import cmd
		uuid := "_" + guid.CreateGuid()
		tfFilePath := workDirPath + "/" + sourceName + ".tf"
		tfFileContent := "resource " + sourceName + " " + uuid + " {}"

		GenFile([]byte(tfFileContent), tfFilePath)
		err = TerraformInit(workDirPath)
		if err != nil {
			err = fmt.Errorf("Do TerraformInit error:%s", err.Error())
			log.Logger.Error("Do TerraformInit error", log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
		resourceAssetId := resourceData.ResourceAssetId
		if plugin != "security_rule" {
			err = TerraformImport(workDirPath, sourceName+"."+uuid, resourceAssetId)
			if err != nil {
				err = fmt.Errorf("Do TerraformImport error:%s", err.Error())
				log.Logger.Error("Do TerraformImport error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
		}

		// clear tf file
		os.Truncate(tfFilePath, 0)

		err = TerraformDestroy(workDirPath)
		if err != nil {
			err = fmt.Errorf("Do TerraformDestroy error: %s", err.Error())
			log.Logger.Error("Do TerraformDestroy error", log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}

		// Del provider file
		err = DelFile(providerFilePath)
		if err != nil {
			err = fmt.Errorf("Do delete provider file error: %s", err.Error())
			log.Logger.Error("Do delete provider file error", log.Error(err))
			rowData["errorMessage"] = err.Error()
		}
	}

	// delet resource_data item
	_, err = x.Exec("DELETE FROM resource_data WHERE id=?", resourceData.Id)
	if err != nil {
		err = fmt.Errorf("Delete resource data by id:%s error: %s", resourceData.Id, err.Error())
		log.Logger.Error("Delete resource data by id error", log.String("id", resourceData.Id), log.Error(err))
		rowData["errorMessage"] = err.Error()
	}

	rowData["errorCode"] = "0"
	return
}

func TerraformOperation(plugin string, action string, reqParam map[string]interface{}) (rowData map[string]interface{}, err error) {
	rowData = make(map[string]interface{})
	rowData["callbackParameter"] = reqParam["callbackParameter"].(string)
	rowData["errorCode"] = "1"
	rowData["errorMessage"] = ""

	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("TerraformOperation error: %v", r)
			rowData["errorMessage"] = err.Error()
		}
	}()

	// Get interface by plugin and action
	var actionName string
	actionName = action
	if actionName == "destroy" {
		actionName = "apply"
	}
	sqlCmd := `SELECT * FROM interface WHERE plugin=? AND name=?`
	paramArgs := []interface{}{plugin, actionName}
	var interfaceInfoList []*models.InterfaceTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&interfaceInfoList)
	if err != nil {
		err = fmt.Errorf("Get interfaceInfo by plugin:%s and name:%s error:%s", plugin, action, err.Error())
		log.Logger.Error("Get interfaceInfo error", log.String("plugin", plugin), log.String("name", action), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(interfaceInfoList) == 0 {
		err = fmt.Errorf("InterfaceInfo can not be found by plugin:%s and name:%s", plugin, action)
		log.Logger.Warn("InterfaceInfo can not be found by plugin and name", log.String("plugin", plugin), log.String("name", action), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	interfaceData := interfaceInfoList[0]

	if plugin == "region" && action == "apply" {
		rowData, err = RegionApply(reqParam, interfaceData)
		return
	}

	// Get regionInfo by regionId
	regionId := reqParam["region_id"].(string)
	sqlCmd = `SELECT * FROM resource_data WHERE resource_id=?`
	paramArgs = []interface{}{regionId}
	var resourceDataInfoList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataInfoList)
	if err != nil {
		err = fmt.Errorf("Get resourceDataInfo by regionId:%s error:%s", regionId, err.Error())
		log.Logger.Error("Get resourceDataInfo by regionId error", log.String("regionId", regionId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(resourceDataInfoList) == 0 {
		err = fmt.Errorf("ResourceDataInfo can not be found by regionId:%s", regionId)
		log.Logger.Warn("ResourceDataInfo can not be found by regionId", log.String("regionId", regionId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	regionData := resourceDataInfoList[0]

	// Get providerInfo data
	providerInfoId := reqParam["provider_info"].(string)
	sqlCmd = `SELECT * FROM provider_info WHERE id=?`
	paramArgs = []interface{}{providerInfoId}
	var providerInfoList []*models.ProviderInfoTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerInfoList)
	if err != nil {
		err = fmt.Errorf("Get providerInfo by id:%s error:%s", providerInfoId, err.Error())
		log.Logger.Error("Get providerInfo by id error", log.String("id", providerInfoId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(providerInfoList) == 0 {
		err = fmt.Errorf("ProviderInfo can not be found by id:%s", providerInfoId)
		log.Logger.Warn("ProviderInfo can not be found by id", log.String("id", providerInfoId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerInfoData := providerInfoList[0]
	providerSecretId, decodeErr := cipher.AesDePassword(models.Config.Auth.PasswordSeed, providerInfoData.SecretId)
	if decodeErr != nil {
		err = fmt.Errorf("Try to decode secretId fail: %s", decodeErr.Error())
		log.Logger.Error("Try to decode secretId fail", log.Error(decodeErr))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerSecretKey, decodeErr := cipher.AesDePassword(models.Config.Auth.PasswordSeed, providerInfoData.SecretKey)
	if decodeErr != nil {
		err = fmt.Errorf("Try to decode secretKey fail: %s", decodeErr.Error())
		log.Logger.Error("Try to decode secretKey fail", log.Error(decodeErr))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerInfoData.SecretId = providerSecretId
	providerInfoData.SecretKey = providerSecretKey

	// Get provider data
	providerId := providerInfoData.Provider
	sqlCmd = `SELECT * FROM provider WHERE id=?`
	paramArgs = []interface{}{providerId}
	var providerList []*models.ProviderTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerList)
	if err != nil {
		err = fmt.Errorf("Get provider by id:%s error:%s", providerId, err.Error())
		log.Logger.Error("Get provider by id error", log.String("id", providerId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(providerList) == 0 {
		err = fmt.Errorf("Provider can not be found by id:%s", providerId)
		log.Logger.Warn("Provider can not be found by id", log.String("id", providerId), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerData := providerList[0]

	// Get sourceData by interface and provider
	sqlCmd = `SELECT * FROM source WHERE interface=? AND provider=?`
	paramArgs = []interface{}{interfaceData.Id, providerData.Id}
	var sourceList []*models.SourceTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&sourceList)
	if err != nil {
		err = fmt.Errorf("Get source data by interface:%s and provider:%s error:%s", interfaceData.Id, providerData.Id, err.Error())
		log.Logger.Error("Get source data by interface and provider error", log.String("interface", interfaceData.Id), log.String("provider", providerData.Id), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(sourceList) == 0 {
		err = fmt.Errorf("Source data can not be found by interface:%s and provider:%s", interfaceData.Id, providerData.Id)
		log.Logger.Warn("Source data can not be found by interface and provider", log.String("interface", interfaceData.Id), log.String("provider", providerData.Id), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	sourceData := sourceList[0]

	terraformFilePath := models.Config.TerraformFilePath
	if terraformFilePath[len(terraformFilePath)-1] != '/' {
		terraformFilePath += "/"
	}
	dirPathResourceId := reqParam["id"].(string)
	if dirPathResourceId == "" {
		dirPathResourceId = reqParam["requestSn"].(string)
	}
	workDirPath := terraformFilePath + providerData.Name + "/" + regionData.ResourceAssetId + "/" + plugin + "/" +
		reqParam["requestId"].(string) + "/" + dirPathResourceId + "/" + sourceData.Name

	if action == "apply" || action == "query" {
		var retOutput map[string]interface{}
		var tmpErr error
		if sourceData.TerraformUsed == "Y" {
			retOutput, tmpErr = handleTerraformApplyOrQuery(reqParam, sourceData, providerData, providerInfoData, regionData, action, plugin, workDirPath, interfaceData)
		} else {
			retOutput, tmpErr = handleApplyOrQuery(action, reqParam, sourceData)
		}
		if tmpErr != nil {
			err = fmt.Errorf("Handle ApplyOrQuery error: %s", tmpErr.Error())
			log.Logger.Error("Handle ApplyOrQuery error", log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
		rowData["errorCode"] = "0"

		for k, v := range retOutput {
			rowData[k] = v
		}
	} else if action == "destroy" {
		retOutput, tmpErr := handleDestroy(workDirPath, sourceData, providerData, providerInfoData, regionData, reqParam, plugin)
		if tmpErr != nil {
			err = fmt.Errorf("Handle Destroy error: %s", tmpErr.Error())
			log.Logger.Error("Handle Destroy error", log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
		for k, v := range retOutput {
			rowData[k] = v
		}
		rowData["errorCode"] = "0"
	} else {
		err = fmt.Errorf("Action: %s is inValid", action)
		log.Logger.Error("Action is inValid", log.String("action", action), log.Error(err))
		rowData["errorMessage"] = err.Error()
	}
	return
}

func convertData(parameterData *models.ParameterTable, relativeSourceId string, reqParam map[string]interface{}) (arg interface{}, err error) {
	if _, ok := reqParam[parameterData.Name]; !ok {
		return
	}
	var resourceIdList []string
	if parameterData.Multiple == "Y" {
		reqParamResourceIds := reqParam[parameterData.Name].([]interface{})
		for _, v := range reqParamResourceIds {
			resourceIdList = append(resourceIdList, v.(string))
		}
	} else {
		resourceIdList = append(resourceIdList, reqParam[parameterData.Name].(string))
	}

	resourceIdsStr := strings.Join(resourceIdList, "','")
	sqlCmd := "SELECT * FROM resource_data WHERE resource=? AND resource_id IN ('" + resourceIdsStr + "')"
	var resourceDataList []*models.ResourceDataTable
	paramArgs := []interface{}{relativeSourceId}
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		err = fmt.Errorf("Get resource data by resource:%s and resource_id:%s error: %s", relativeSourceId, resourceIdsStr, err.Error())
		log.Logger.Error("Get resource data by resource and resource_id error", log.String("resource", relativeSourceId), log.String("resource_id", resourceIdsStr), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		err = fmt.Errorf("Resource_data can not be found by resource:%s and resource_id:%s", relativeSourceId, resourceIdsStr)
		log.Logger.Warn("Resource_data can not be found by resource and resource_id", log.String("resource", relativeSourceId), log.String("resource_id", resourceIdsStr), log.Error(err))
		return
	}

	if parameterData.Multiple == "Y" {
		tmpRes := []string{}
		for i := range resourceDataList {
			tmpRes = append(tmpRes, resourceDataList[i].ResourceAssetId)
		}
		arg = tmpRes
	} else {
		arg = resourceDataList[0].ResourceAssetId
	}
	return
}

func reverseConvertData(parameterData *models.ParameterTable, tfstateAttributeData *models.TfstateAttributeTable, tfstateVal interface{}) (argKey string, argVal interface{}, err error) {
	argKey = parameterData.Name
	if tfstateVal == nil {
		return
	}
	relativeSourceId := tfstateAttributeData.RelativeSource
	var resourceAssetIds []string
	if tfstateAttributeData.IsMulti == "Y" {
		tfstateAssetIds := tfstateVal.([]interface{})
		for _, v := range tfstateAssetIds {
			resourceAssetIds = append(resourceAssetIds, v.(string))
		}
	} else {
		resourceAssetIds = append(resourceAssetIds, tfstateVal.(string))
	}
	resourceAssetIdsStr := strings.Join(resourceAssetIds, "','")
	sqlCmd := "SELECT * FROM resource_data WHERE resource=? AND resource_asset_id IN ('" + resourceAssetIdsStr + "')"
	paramArgs := []interface{}{relativeSourceId}
	var resourceDataList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		err = fmt.Errorf("Get resource data by resource:%s and resource_asset_id:%s error:%s", relativeSourceId, resourceAssetIdsStr, err.Error())
		log.Logger.Error("Get resource data by resource and resource_asset_id error", log.String("resource", relativeSourceId), log.String("resource_asset_id", resourceAssetIdsStr), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		err = fmt.Errorf("Resource data can not be found by resource:%s and resource_asset_id:%s", relativeSourceId, resourceAssetIdsStr)
		log.Logger.Warn("Resource data can not be found by resource and resource_asset_id", log.String("resource", relativeSourceId), log.String("resource_asset_id", resourceAssetIdsStr), log.Error(err))
		return
	}
	argKey = parameterData.Name

	if tfstateAttributeData.IsMulti == "Y" {
		tmpRes := []string{}
		for i := range resourceDataList {
			tmpRes = append(tmpRes, resourceDataList[i].ResourceId)
		}
		argVal = tmpRes
	} else {
		argVal = resourceDataList[0].ResourceId
	}
	return
}

func convertTemplate(parameterData *models.ParameterTable, providerData *models.ProviderTable, reqParam map[string]interface{}) (arg interface{}, err error) {
	sqlCmd := `SELECT * FROM template_value WHERE template=? AND value=?`
	templateId := parameterData.Template
	paramVal := reqParam[parameterData.Name].(string)
	paramArgs := []interface{}{templateId, paramVal}
	var templateValueList []*models.TemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&templateValueList)
	if err != nil {
		err = fmt.Errorf("Get template_value data by template:%s and value:%s error:%s", templateId, paramVal)
		log.Logger.Error("Get tempalte_value data by template and value error", log.String("template", templateId), log.String("value", paramVal), log.Error(err))
		return
	}
	if len(templateValueList) == 0 {
		err = fmt.Errorf("Template_value can not be found by template:%s and value:%s", templateId, paramVal)
		log.Logger.Warn("Template_value can not be found by template and value", log.String("template", templateId), log.String("value", paramVal), log.Error(err))
		return
	}
	templateValueData := templateValueList[0]

	sqlCmd = `SELECT * FROM provider_template_value WHERE template_value=? AND provider=?`
	paramArgs = []interface{}{templateValueData.Id, providerData.Id}
	var providerTemplateValueList []*models.ProviderTemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerTemplateValueList)
	if err != nil {
		err = fmt.Errorf("Get provider_template_value data by template_value:%s and provider:%s error:%s", templateValueData.Id, providerData.Id)
		log.Logger.Error("Get provider_tempalte_value data by template_value and provider error", log.String("template_value", templateValueData.Id), log.String("provider", providerData.Id), log.Error(err))
		return
	}
	if len(providerTemplateValueList) == 0 {
		err = fmt.Errorf("Provider_template_value can not be found by template_value:%s and provider:%s", templateValueData.Id, providerData.Id)
		log.Logger.Warn("Provider_template_value can not be found by template_value and provider", log.String("template_value", templateValueData.Id), log.String("provider", providerData.Id), log.Error(err))
		return
	}
	arg = providerTemplateValueList[0].Value
	return
}

func reverseConvertTemplate(parameterData *models.ParameterTable, providerData *models.ProviderTable, tfstateVal interface{}) (argKey string, argVal string, err error) {
	argKey = parameterData.Name
	if tfstateVal == nil {
		return
	}
	sqlCmd := `SELECT t1.* FROM template_value AS t1 LEFT JOIN provider_template_value AS t2 ON t1.id=t2.template_value WHERE t2.provider=? AND t2.value=?`
	paramArgs := []interface{}{providerData.Id, tfstateVal}
	var templateValueList []*models.TemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&templateValueList)
	if err != nil {
		err = fmt.Errorf("Get template_value data by provider:%s and tfstateValue:%s error:%s", providerData.Id, tfstateVal)
		log.Logger.Error("Get tempalte_value data by provider and tfstateValue error", log.String("provider", providerData.Id), log.String("tfstateValue", tfstateVal.(string)), log.Error(err))
		return
	}
	if len(templateValueList) == 0 {
		err = fmt.Errorf("Template_value can not be found by provider:%s and tfstateValue:%s", providerData.Id, tfstateVal)
		log.Logger.Warn("Template_value can not be found by provider and tfstateValue", log.String("provider", providerData.Id), log.String("tfstateValue", tfstateVal.(string)), log.Error(err))
		return
	}
	templateValueData := templateValueList[0]
	argKey = parameterData.Name
	argVal = templateValueData.Value
	return
}

func convertAttr(parameterData *models.ParameterTable, tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}) (arg interface{}, err error) {
	relativeResourceIds := []string{}
	if parameterData.Multiple == "Y" {
		tmpData := reqParam[parameterData.Name].([]interface{})
		for i := range tmpData {
			relativeResourceIds = append(relativeResourceIds, tmpData[i].(string))
		}
	} else {
		relativeResourceIds = append(relativeResourceIds, reqParam[parameterData.Name].(string))
	}

	sqlCmd := `SELECT * FROM tfstate_attribute WHERE id=?`
	paramArgs := []interface{}{tfArgumentData.RelativeTfstateAttribute}
	var tfstateAttirbuteList []*models.TfstateAttributeTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&tfstateAttirbuteList)
	if err != nil {
		err = fmt.Errorf("Get tfstateAttribute data by id:%s error: %s", tfArgumentData.RelativeTfstateAttribute, err.Error())
		log.Logger.Error("Get tfstateAttribute data by id error", log.String("id", tfArgumentData.RelativeTfstateAttribute), log.Error(err))
		return
	}
	if len(tfstateAttirbuteList) == 0 {
		err = fmt.Errorf("TfstateAttribute data can not be found by id:%s", tfArgumentData.RelativeTfstateAttribute)
		log.Logger.Warn("TfstateAttribute data can not be found by id", log.String("id", tfArgumentData.RelativeTfstateAttribute), log.Error(err))
		return
	}
	tfstateAttirbuteData := tfstateAttirbuteList[0]

	result := []interface{}{}
	for i := range relativeResourceIds {
		sqlCmd := `SELECT * FROM resource_data WHERE resource=? AND resource_id=?`
		paramArgs := []interface{}{tfArgumentData.RelativeSource, relativeResourceIds[i]}
		var resourceDataList []*models.ResourceDataTable
		err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
		if err != nil {
			err = fmt.Errorf("Get resource data by source:%s and resource_id:%s error: %s", tfArgumentData.RelativeSource, relativeResourceIds[i], err.Error())
			log.Logger.Error("Get resource data by source and resource_id error", log.String("source", tfArgumentData.RelativeSource), log.String("resource_id", relativeResourceIds[i]), log.Error(err))
			return
		}
		if len(resourceDataList) == 0 {
			err = fmt.Errorf("ResourceData can not be found by source:%s and resource_id:%s", tfArgumentData.RelativeSource, relativeResourceIds[i])
			log.Logger.Warn("ResourceData can not be found by source and resource_id", log.String("source", tfArgumentData.RelativeSource), log.String("resource_id", relativeResourceIds[i]), log.Error(err))
			return
		}
		resourceData := resourceDataList[0]

		tfstateFileData := resourceData.TfStateFile
		var unmarshalTfstateFileData models.TfstateFileData
		err = json.Unmarshal([]byte(tfstateFileData), &unmarshalTfstateFileData)
		if err != nil {
			err = fmt.Errorf("Unmarshal tfstate file data error:%s", err.Error())
			log.Logger.Error("Unmarshal tfstate file data error", log.Error(err))
			return
		}
		var tfstateFileAttributes map[string]interface{}
		tfstateFileAttributes = unmarshalTfstateFileData.Resources[0].Instances[0].Attributes
		result = append(result, tfstateFileAttributes[tfstateAttirbuteData.Name])
	}

	if parameterData.Multiple == "Y" {
		tmpRes := []string{}
		for i := range result {
			tmpRes = append(tmpRes, result[i].(string))
		}
		arg = tmpRes
	} else {
		arg = result[0].(string)
	}
	return
}

func reverseConvertAttr(parameterData *models.ParameterTable, tfstateAttributeData *models.TfstateAttributeTable, tfstateVal interface{}) (argKey string, argVal interface{}, err error) {
	argKey = parameterData.Name
	if tfstateVal == nil {
		return
	}
	relativeAssetVals := []string{}
	if tfstateAttributeData.IsMulti == "Y" {
		tmpData := tfstateVal.([]interface{})
		for i := range tmpData {
			relativeAssetVals = append(relativeAssetVals, tmpData[i].(string))
		}
	} else {
		relativeAssetVals = append(relativeAssetVals, tfstateVal.(string))
	}

	relativeAssetValMap := make(map[string]bool)
	for _, v := range relativeAssetVals {
		relativeAssetValMap[v] = true
	}

	sqlCmd := `SELECT * FROM tfstate_attribute WHERE id=?`
	paramArgs := []interface{}{tfstateAttributeData.RelativeTfstateAttribute}
	var tfstateAttirbuteList []*models.TfstateAttributeTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&tfstateAttirbuteList)
	if err != nil {
		err = fmt.Errorf("Get tfstateAttribute data by id:%s error: %s", tfstateAttributeData.RelativeTfstateAttribute, err.Error())
		log.Logger.Error("Get tfstateAttribute data by id error", log.String("id", tfstateAttributeData.RelativeTfstateAttribute), log.Error(err))
		return
	}
	if len(tfstateAttirbuteList) == 0 {
		err = fmt.Errorf("TfstateAttribute data can not be found by id:%s", tfstateAttributeData.RelativeTfstateAttribute)
		log.Logger.Warn("TfstateAttribute data can not be found by id", log.String("id", tfstateAttributeData.RelativeTfstateAttribute), log.Error(err))
		return
	}
	relativeTfstateAttirbuteData := tfstateAttirbuteList[0]

	result := []interface{}{}
	sqlCmd = `SELECT * FROM resource_data WHERE resource=?`
	paramArgs = []interface{}{tfstateAttributeData.RelativeSource}
	var resourceDataList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		err = fmt.Errorf("Get resource data by source:%s error: %s", tfstateAttributeData.RelativeSource, err.Error())
		log.Logger.Error("Get resource data by source error", log.String("source", tfstateAttributeData.RelativeSource), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		err = fmt.Errorf("ResourceData can not be found by source:%s", tfstateAttributeData.RelativeSource)
		log.Logger.Warn("ResourceData can not be found by source", log.String("source", tfstateAttributeData.RelativeSource), log.Error(err))
		return
	}

	for _, resourceData := range resourceDataList {
		tfstateFileData := resourceData.TfStateFile
		var unmarshalTfstateFileData models.TfstateFileData
		err = json.Unmarshal([]byte(tfstateFileData), &unmarshalTfstateFileData)
		if err != nil {
			err = fmt.Errorf("Unmarshal tfstate file data error:%s", err.Error())
			log.Logger.Error("Unmarshal tfstate file data error", log.Error(err))
			continue
		}
		var tfstateFileAttributes map[string]interface{}
		tfstateFileAttributes = unmarshalTfstateFileData.Resources[0].Instances[0].Attributes
		if _, ok := relativeAssetValMap[tfstateFileAttributes[relativeTfstateAttirbuteData.Name].(string)]; ok {
			result = append(result, resourceData.ResourceId)
			delete(relativeAssetValMap, tfstateFileAttributes[relativeTfstateAttirbuteData.Name].(string))
		}
	}

	argKey = parameterData.Name
	if tfstateAttributeData.IsMulti == "Y" {
		tmpRes := []string{}
		for i := range result {
			tmpRes = append(tmpRes, result[i].(string))
		}
		argVal = tmpRes
	} else {
		argVal = result[0]
	}
	return
}

func convertContextData(parameterData *models.ParameterTable, tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}) (arg interface{}, isDiscard bool, err error) {
	isDiscard = false

	// Get relative parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	relativeParameterId := tfArgumentData.RelativeParameter
	paramArgs := []interface{}{relativeParameterId}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		err = fmt.Errorf("Get parameter data by id:%s error:%s", relativeParameterId)
		log.Logger.Error("Get parameter data by id error", log.String("id", relativeParameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter can not be found by id:%s", relativeParameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", relativeParameterId), log.Error(err))
		return
	}
	relativeParameterData := parameterList[0]
	if reqParam[relativeParameterData.Name].(string) == tfArgumentData.RelativeParameterValue {
		arg, err = convertData(parameterData, tfArgumentData.RelativeSource, reqParam)
	} else {
		isDiscard = true
	}
	return
}

func reverseConvertContextData(parameterData *models.ParameterTable,
	tfstateAttributeData *models.TfstateAttributeTable,
	tfstateVal interface{},
	outPutArgs map[string]interface{}) (argKey string, argVal interface{}, isDiscard bool, err error) {

	argKey = parameterData.Name
	if tfstateVal == nil {
		return
	}
	isDiscard = false

	// Get relative parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	relativeParameterId := tfstateAttributeData.RelativeParameter
	paramArgs := []interface{}{relativeParameterId}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		err = fmt.Errorf("Get parameter data by id:%s error:%s", relativeParameterId)
		log.Logger.Error("Get parameter data by id error", log.String("id", relativeParameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter can not be found by id:%s", relativeParameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", relativeParameterId), log.Error(err))
		return
	}
	relativeParameterData := parameterList[0]
	if outPutArgs[relativeParameterData.Name] == nil {
		return
	}
	if outPutArgs[relativeParameterData.Name].(string) == tfstateAttributeData.RelativeParameterValue {
		argKey, argVal, err = reverseConvertData(parameterData, tfstateAttributeData, tfstateVal)
	} else {
		isDiscard = true
	}
	return
}

func convertDirect(parameterData *models.ParameterTable, defaultValue string, reqParam map[string]interface{}) (arg interface{}, err error) {
	reqArg := reqParam[parameterData.Name]
	if reqArg == nil {
		return
	}

	if parameterData.DataType == "string" && reqArg.(string) == "null" {
		arg = "null"
	} else if parameterData.DataType == "string" && reqArg.(string) == "" || parameterData.DataType == "int" && reqArg.(float64) == 0 {
		arg = defaultValue
	} else {
		arg = reqParam[parameterData.Name]
	}
	return
}

func convertFunction(parameterData *models.ParameterTable, tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}) (arg interface{}, err error) {
	return
}

func reverseConvertFunction(parameterData *models.ParameterTable, tfstateAttributeData *models.TfstateAttributeTable, tfstateVal interface{}) (argKey string, argVal interface{}, err error) {
	argKey = parameterData.Name
	if tfstateVal == nil {
		return
	}
	functionDefine := tfstateAttributeData.FunctionDefine
	var functionDefineData models.FunctionDefine
	json.Unmarshal([]byte(functionDefine), &functionDefineData)

	resultIdx := -1
	if functionDefineData.Return != "result" {
		idxStrStart := strings.Index(functionDefineData.Return, "[")
		idxStrEnd := strings.Index(functionDefineData.Return, "]")
		if idxStrStart == -1 || idxStrEnd == -1 || idxStrStart >= idxStrEnd {
			argKey = parameterData.Name
			err = fmt.Errorf("The function_define return_value: %s of tfstateAttribute:%s config error", functionDefineData.Return, tfstateAttributeData.Name)
			log.Logger.Error("The function_define return_value of tfstateAttribute config error", log.String("return_value", functionDefineData.Return), log.String("tfstateAttribute", tfstateAttributeData.Name), log.Error(err))
			return
		}
		resultIdx, _ = strconv.Atoi(functionDefineData.Return[idxStrStart+1 : idxStrEnd])
	}

	handleTfstateVals := []string{}
	if tfstateAttributeData.IsMulti == "Y" {
		tmpData := tfstateVal.([]interface{})
		for i := range tmpData {
			handleTfstateVals = append(handleTfstateVals, tmpData[i].(string))
		}
	} else {
		handleTfstateVals = append(handleTfstateVals, tfstateVal.(string))
	}
	var result []interface{}
	if functionDefineData.Function == models.FunctionConvertFunctionDefineName["Split"] {
		for _, tfstateValStr := range handleTfstateVals {
			splitResult := [][]string{}
			splitChars := functionDefineData.Args.SplitChar
			for i := range splitChars {
				curResult := strings.Split(tfstateValStr, splitChars[i])
				if len(curResult) < 2 || curResult[1] == "" {
					curResult = append(curResult, curResult[0])
				}
				splitResult = append(splitResult, curResult)
			}
			if resultIdx == -1 {
				result = append(result, splitResult[0])
			} else {
				result = append(result, splitResult[0][resultIdx])
			}
		}
	} else if functionDefineData.Function == models.FunctionConvertFunctionDefineName["Replace"] {
		for _, tfstateValStr := range handleTfstateVals {
			replaceResult := []string{}
			replaceVals := functionDefineData.Args.ReplaceVal
			for i := range replaceVals {
				for old, new := range replaceVals[i] {
					curResult := strings.Replace(tfstateValStr, old, new, -1)
					replaceResult = append(replaceResult, curResult)
				}
			}
			if resultIdx == -1 {
				result = append(result, replaceResult[0])
			} else {
				result = append(result, replaceResult[0][resultIdx])
			}
		}
	} else if functionDefineData.Function == models.FunctionConvertFunctionDefineName["Regx"] {
		for _, tfstateValStr := range handleTfstateVals {
			regxResult := [][]string{}
			regExprs := functionDefineData.Args.RegExp
			for i := range regExprs {
				regExp := regexp.MustCompile(regExprs[i])
				curResult := regExp.FindStringSubmatch(tfstateValStr)
				// the first one is the original str
				curResult = curResult[1:]
				regxResult = append(regxResult, curResult)
			}
			if resultIdx == -1 {
				result = append(result, regxResult[0])
			} else {
				result = append(result, regxResult[0][resultIdx])
			}
		}
	} else {
		err = fmt.Errorf("The function_define:%s of tfstateAttribute:%s config error", functionDefine, tfstateAttributeData.Name)
		log.Logger.Error("The function_define of tfstateAttribute config error", log.String("function_define", functionDefine), log.String("tfstateAttribute", tfstateAttributeData.Name), log.Error(err))
		return
	}
	argKey = parameterData.Name
	if tfstateAttributeData.IsMulti == "Y" {
		tmpRes := []string{}
		for i := range result {
			tmpRes = append(tmpRes, result[i].(string))
		}
		argVal = tmpRes
	} else {
		argVal = result[0]
	}
	return
}

func reverseConvertDirect(parameterData *models.ParameterTable, tfstateAttributeData *models.TfstateAttributeTable, tfstateVal interface{}) (argKey string, argVal interface{}, err error) {
	argKey = parameterData.Name
	if tfstateVal == nil {
		return
	}
	if tfstateAttributeData.IsMulti == "Y" {
		tmpRes := []interface{}{}
		result := tfstateVal.([]interface{})
		for i := range result {
			tmpRes = append(tmpRes, result[i])
		}
		argVal = tmpRes
	} else {
		argVal = tfstateVal
	}
	return
}

func handleReverseConvert(outPutParameterNameMap map[string]*models.ParameterTable,
	outPutParameterIdMap map[string]*models.ParameterTable,
	tfstateAttrParamMap map[string]*models.TfstateAttributeTable,
	tfstateAttrNameMap map[string]*models.TfstateAttributeTable,
	reqParam map[string]interface{},
	providerData *models.ProviderTable,
	tfstateFileAttributes map[string]interface{},
	action string,
	parentObjectName string,
	tfstateAttributeList []*models.TfstateAttributeTable,
	paramCnt *int) (outPutArgs map[string]interface{}, err error) {

	outPutArgs = make(map[string]interface{})
	curLevelResult := make(map[string]interface{})

	// 循环遍历每个 tfstateAttribute 进行 reverseConvert 生成输出参数
	for _, tfstateAttr := range tfstateAttributeList {
		if tfstateAttr.ObjectName == parentObjectName {
			// handle current level tfstateAttribute
			if tfstateAttr.Type == "object" {
				// go into next level
				var curTfstateFileAttributes []interface{}
				var curAttributesRet []interface{}
				if tfstateAttr.IsMulti == "Y" {
					tmpData := tfstateFileAttributes[tfstateAttr.Name].([]interface{})
					for _, v := range tmpData {
						curTfstateFileAttributes = append(curTfstateFileAttributes, v)
					}
				} else {
					curTfstateFileAttributes = append(curTfstateFileAttributes, tfstateFileAttributes[tfstateAttr.Name])
				}
				for i := range curTfstateFileAttributes {
					var tmpCurTfstateFileAttributes map[string]interface{}
					tmpMarshal, _ := json.Marshal(curTfstateFileAttributes[i])
					json.Unmarshal(tmpMarshal, &tmpCurTfstateFileAttributes)
					ret, tmpErr := handleReverseConvert(outPutParameterNameMap,
						outPutParameterIdMap,
						tfstateAttrParamMap,
						tfstateAttrNameMap,
						reqParam,
						providerData,
						tmpCurTfstateFileAttributes,
						action,
						tfstateAttr.Id,
						tfstateAttributeList,
						paramCnt)
					if tmpErr != nil {
						err = fmt.Errorf("Reverse convert tfstateAttr:%s error:%s", tfstateAttr.Name, err.Error())
						log.Logger.Error("Revese convert tfstateAttr error", log.String("tfstateAttr", tfstateAttr.Name), log.Error(err))
						return
					}
					curAttributesRet = append(curAttributesRet, ret)
				}
				/*
					if tfstateAttr.ConvertWay == "" {
						*paramCnt += 1
						outPutArgs[models.TerraformOutPutPrefix+strconv.Itoa(*paramCnt)] = curAttributesRet
					} else {
						outPutArgs[outPutParameterIdMap[tfstateAttr.Parameter].Name] = curAttributesRet
					}
				*/
				*paramCnt += 1
				outPutArgs[models.TerraformOutPutPrefix+strconv.Itoa(*paramCnt)] = curAttributesRet
			} else {
				curParamData := outPutParameterIdMap[tfstateAttr.Parameter]
				if tfstateOutParamVal, ok := tfstateFileAttributes[tfstateAttr.Name]; ok {
					convertWay := tfstateAttr.ConvertWay
					var outArgKey string
					var outArgVal interface{}
					var isDiscard = false
					switch convertWay {
					case models.ConvertWay["Data"]:
						outArgKey, outArgVal, err = reverseConvertData(curParamData, tfstateAttr, tfstateOutParamVal)
					case models.ConvertWay["Template"]:
						if tfstateAttr.DefaultValue != "" {
							tfstateOutParamVal = tfstateAttr.DefaultValue
						}
						outArgKey, outArgVal, err = reverseConvertTemplate(curParamData, providerData, tfstateOutParamVal)
					case models.ConvertWay["Attr"]:
						outArgKey, outArgVal, err = reverseConvertAttr(curParamData, tfstateAttr, tfstateOutParamVal)
					case models.ConvertWay["ContextData"]:
						outArgKey, outArgVal, isDiscard, err = reverseConvertContextData(curParamData, tfstateAttr, tfstateOutParamVal, curLevelResult)
					case models.ConvertWay["Direct"]:
						// outArgKey, outArgVal, err = reverseConvertDirect(curParamData, tfstateAttr, tfstateOutParamVal)
						outArgKey, outArgVal, err = curParamData.Name, tfstateOutParamVal, nil
					case models.ConvertWay["Function"]:
						outArgKey, outArgVal, err = reverseConvertFunction(curParamData, tfstateAttr, tfstateOutParamVal)
					default:
						err = fmt.Errorf("The convertWay:%s of tfstateAttribute:%s is invalid", convertWay, tfstateAttr.Name)
						log.Logger.Error("The convertWay of tfstateAttribute is invalid", log.String("convertWay", convertWay), log.String("tfstateAttribute", tfstateAttr.Name), log.Error(err))
						return
					}
					if isDiscard {
						continue
					}

					if action == "query" {
						if outArgVal == nil || outArgVal == "" {
							err = nil
						}
						if outArgKey == "" {
							continue
						}
					}

					if err != nil {
						err = fmt.Errorf("Reverse convert parameter:%s error:%s", tfstateAttr.Parameter, err.Error())
						log.Logger.Error("Revese convert parameter error", log.String("parameterId", tfstateAttr.Parameter), log.Error(err))
						return
					}
					// merger the tfstateAttributeVal if they have the same name
					if _, ok := outPutArgs[outArgKey]; ok {
						if _, ok := outPutArgs[outArgKey].([]interface{}); ok {
							tmpData := outPutArgs[outArgKey].([]interface{})
							tmpData = append(tmpData, outArgVal)
							outPutArgs[outArgKey] = tmpData
						} else {
							tmpData := []interface{}{outPutArgs[outArgKey]}
							tmpData = append(tmpData, outArgVal)
							outPutArgs[outArgKey] = tmpData
						}
					} else {
						outPutArgs[outArgKey] = outArgVal
					}
					curLevelResult[outArgKey] = outArgVal
				} else {
					outPutArgs[curParamData.Name] = ""
				}
			}
		} else {
			continue
		}
	}
	return
}
