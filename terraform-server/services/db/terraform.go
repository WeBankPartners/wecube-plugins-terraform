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
		err = fmt.Errorf("Cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
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
		err = fmt.Errorf("Cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
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
		err = fmt.Errorf("Cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
	}
	return
}

func TerraformDestroy(dirPath string, sourceData *models.SourceTable, providerData *models.ProviderTable, providerInfo *models.ProviderInfoTable, regionData *models.ResourceDataTable, resourceAssetId string) (err error) {
	sourceName := sourceData.Name
	// Gen .tf 文件, 然后执行 terraform import cmd
	uuid := "_" + guid.CreateGuid()
	tfFilePath := dirPath + "/" + sourceName + ".tf"
	tfFileContent := "resource " + sourceName + " " + uuid + " {}"

	_, err = os.Stat(dirPath)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.MkdirAll(dirPath, os.ModePerm)
			if err != nil {
				err = fmt.Errorf("Make dir: %s error: %s", dirPath, err.Error())
				log.Logger.Error("Make dir error", log.String("dirPath", dirPath), log.Error(err))
				//retOutput["errorMessage"] = err.Error()
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", dirPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("dirPath", dirPath), log.Error(err))
			// retOutput["errorMessage"] = err.Error()
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

	providerFileContent, err := json.Marshal(providerFileData)
	if err != nil {
		err = fmt.Errorf("Marshal providerFileData error: %s", err.Error())
		log.Logger.Error("Marshal providerFileData error", log.Error(err))
		return
	}
	providerFilePath := dirPath + "/provider.tf.json"
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
		versionTfFilePath := terraformFilePath + "version.tf"
		versionTfFileContent, tmpErr := ReadFile(versionTfFilePath)
		if tmpErr != nil {
			err = fmt.Errorf("Read versionTfFile: %s error: %s", versionTfFilePath, tmpErr.Error())
			log.Logger.Error("Read versionTfFile error", log.String("versionTfFilePath", versionTfFilePath), log.Error(err))
			return
		}

		genVersionTfFilePath := dirPath + "/version.tf"
		err = GenFile(versionTfFileContent, genVersionTfFilePath)
		if err != nil {
			err = fmt.Errorf("Gen versionTfFile: %s error: %s", genVersionTfFilePath, err.Error())
			log.Logger.Error("Gen versionTfFile error", log.String("genVersionTfFilePath", genVersionTfFilePath), log.Error(err))
			return
		}
	}

	GenFile([]byte(tfFileContent), tfFilePath)
	err = TerraformInit(dirPath)
	if err != nil {
		return
	}
	err = TerraformImport(dirPath, sourceName+"."+uuid, resourceAssetId)
	if err != nil {
		return
	}

	// clear tf file
	os.Truncate(tfFilePath, 0)

	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " destroy -auto-approve"
	cmd := exec.Command("/bin/bash", "-c", cmdStr)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmdErr := cmd.Run()
	if cmdErr != nil {
		err = fmt.Errorf("Cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
	}

	// Del provider file
	// TODO
	err = DelFile(providerFilePath)

	//
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
		err = fmt.Errorf("Cmd:%s run failed with %s", cmdStr, cmdErr.Error())
		log.Logger.Error("Cmd run failed", log.String("cmd", cmdStr), log.Error(cmdErr))
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
		convertWay := tfArgumentList[i].ConvertWay

		// 查询 tfArgument 对应的 parameter
		sqlCmd = `SELECT * FROM parameter WHERE id=?`
		paramArgs = []interface{}{tfArgumentList[i].Parameter}
		var parameterList []*models.ParameterTable
		err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
		if err != nil {
			err = fmt.Errorf("Get Parameter data error:%s", err.Error())
			log.Logger.Error("Get parameter data error", log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
			return
		}
		if len(parameterList) == 0 {
			err = fmt.Errorf("Parameter can not be found by id:%s", tfArgumentList[i].Parameter)
			log.Logger.Warn("Parameter can not be found by id", log.String("id", tfArgumentList[i].Parameter), log.Error(err))
			return
		}
		parameterData := parameterList[0]

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
			sourceIdList[sourceData.Id] = true
			handlingSourceIds := make(map[string]bool)
			handlingSourceIds[tfArgumentList[i].Source] = true
			arg, err = convertAttr(tfArgumentList[i].RelativeTfstateAttribute, sourceIdList, handlingSourceIds, providerData.Name, reqParam)
		case models.ConvertWay["Direct"]:
			arg, err = convertDirect(tfArgumentList[i].Parameter, tfArgumentList[i].DefaultValue, reqParam)
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
		if convertWay == "direct" && arg.(string) == "null" {
			delete(tfArguments, tfArgumentList[i].Name)
		}
		if parameterData.DataType == "object" || parameterData.DataType == "object_str" {
			var tmpVal map[string]interface{}
			err = json.Unmarshal([]byte(arg.(string)), &tmpVal)
			tfArguments[tfArgumentList[i].Name]	= tmpVal
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
		versionTfFilePath := terraformFilePath + "version.tf"
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

	/*
	// terraform import
	err = TerraformImport(dirPath, address, resourceId)
	if err != nil {
		err = fmt.Errorf("Do TerraformImport error:%s", err.Error())
	    retOutput["errorMessage"] = err.Error()
		return
	}
	*/

	// terraform init
	err = TerraformInit(dirPath)
	if err != nil {
		err = fmt.Errorf("Do TerraformInit error:%s", err.Error())
		log.Logger.Error("Do TerraformInit error", log.Error(err))
		retOutput["errorMessage"] = err.Error()
		return
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

	var tfstateObjectTypeAttribute *models.TfstateAttributeTable
	tfstateAttrParamMap := make(map[string]*models.TfstateAttributeTable)
	for _, v := range tfstateAttributeList {
		if v.Parameter == "" {
			tfstateObjectTypeAttribute = v
		} else {
			tfstateAttrParamMap[v.Parameter] = v
		}
	}

	outPutParameterNameMap := make(map[string]*models.ParameterTable)
	for _, v := range outPutParameterList {
		outPutParameterNameMap[v.Name] = v
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
		outPutArgs := make(map[string]interface{})
		// 循环遍历每个 outPutParameterName 进行 reverseConvert 生成输出参数
		for k, v := range outPutParameterNameMap {
			if tfstateAttr, okParam := tfstateAttrParamMap[v.Id]; okParam {
				if tfstateOutParamVal, ok := tfstateFileAttributes[tfstateAttr.Name]; ok {
					convertWay := tfstateAttr.ConvertWay
					var outArgKey string
					var outArgVal interface{}
					switch convertWay {
					case models.ConvertWay["Data"]:
						outArgKey, outArgVal, err = reverseConvertData(v, tfstateAttr.Source, tfstateOutParamVal)
					case models.ConvertWay["Template"]:
						outArgKey, outArgVal, err = reverseConvertTemplate(tfstateAttr.Parameter, providerData.Name, tfstateOutParamVal)
					case models.ConvertWay["Context"]:
						outArgKey, outArgVal, err = reverseConvertContext(tfstateAttr.RelativeParameter, tfstateOutParamVal)
					case models.ConvertWay["Direct"]:
						// outArgKey, outArgVal, err = reverseConvertDirect(tfstateAttr.Parameter, tfstateOutParamVal)
						outArgKey, outArgVal, err = k, tfstateOutParamVal, nil
					}
					if err != nil {
						err = fmt.Errorf("Reverse convert parameter:%s error:%s", tfstateAttr.Parameter, err.Error())
						log.Logger.Error("Revese convert parameter error", log.String("parameterId", tfstateAttr.Parameter), log.Error(err))
						retOutput["errorMessage"] = err.Error()
						return
					}
					outPutArgs[outArgKey] = outArgVal
				} else {
					outPutArgs[k] = ""
				}
			} else {
				outPutArgs[k] = reqParam[k]
			}
		}
		for k, v := range outPutArgs {
			retOutput[k] = v
		}
	} else {
		// 处理结果字段为 object 的情况
		//retOutput["##result_list"] = []interface{}
		outPutResultList := []map[string]interface{}{}
		var tfstateResult []map[string]interface{}
		if tfstateObjectTypeAttribute.IsMulti == "Y" {
			// var result []map[string]interface{}
			var tmpData []map[string]interface{}
			tmpMarshal, _ := json.Marshal(tfstateFileAttributes[tfstateObjectTypeAttribute.Name])
			json.Unmarshal(tmpMarshal, &tmpData)
			//tmpData := tfstateFileAttributes[tfstateObjectTypeAttribute.Name].([]map[string]interface{})
			for i := range tmpData {
				tfstateResult = append(tfstateResult, tmpData[i])
			}
		} else {
			var tmpData map[string]interface{}
			tmpMarshal, _ := json.Marshal(tfstateFileAttributes[tfstateObjectTypeAttribute.Name])
			//tmpData := tfstateFileAttributes[tfstateObjectTypeAttribute.Name]
			json.Unmarshal(tmpMarshal, &tmpData)
			tfstateResult = append(tfstateResult, tmpData)
		}
		for i := range tfstateResult {
			outPutArgs := make(map[string]interface{})
			// 循环遍历每个 outPutParameterName 进行 reverseConvert 生成输出参数
			for k, v := range outPutParameterNameMap {
				if tfstateAttr, okParam := tfstateAttrParamMap[v.Id]; okParam {
					if tfstateOutParamVal, ok := tfstateResult[i][tfstateAttr.Name]; ok {
						convertWay := tfstateAttr.ConvertWay
						var outArgKey string
						var outArgVal interface{}
						switch convertWay {
						case models.ConvertWay["Data"]:
							outArgKey, outArgVal, err = reverseConvertData(v, tfstateAttr.Source, tfstateOutParamVal)
						case models.ConvertWay["Template"]:
							outArgKey, outArgVal, err = reverseConvertTemplate(tfstateAttr.Parameter, providerData.Name, tfstateOutParamVal)
						case models.ConvertWay["Context"]:
							outArgKey, outArgVal, err = reverseConvertContext(tfstateAttr.RelativeParameter, tfstateOutParamVal)
						case models.ConvertWay["Direct"]:
							// outArgKey, outArgVal, err = reverseConvertDirect(tfstateAttr.Parameter, tfstateOutParamVal)
							outArgKey, outArgVal, err = k, tfstateOutParamVal, nil
						}

						if action == "query" {
							if outArgVal == nil || outArgVal == "" {
								// continue
								err = nil
							}
							if outArgKey == "" {
								continue
							}
						}

						if err != nil {
							err = fmt.Errorf("Reverse convert parameter:%s error:%s", tfstateAttr.Parameter, err.Error())
							log.Logger.Error("Revese convert parameter error", log.String("parameterId", tfstateAttr.Parameter), log.Error(err))
							retOutput["errorMessage"] = err.Error()
							return
						}
						outPutArgs[outArgKey] = outArgVal
					} else {
						outPutArgs[k] = ""
					}
				} else {
					outPutArgs[k] = reqParam[k]
				}
			}
			//for k, v := range outPutArgs {
			//	retOutput[k] = v
			//}
			outPutResultList = append(outPutResultList, outPutArgs)
			retOutput["_result_list"] = outPutResultList
		}
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
		err = fmt.Errorf("Get providerInfo error:%s", err.Error())
		log.Logger.Error("Get providerInfo error", log.String("providerInfoId", providerInfoId), log.Error(err))
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
	/*
	providerSecretId, decodeErr := cipher.AesDePassword(models.Config.Auth.PasswordSeed, providerInfoData.SecretId)
	if decodeErr != nil {
		err = fmt.Errorf("Try to decode secretId fail: %s", decodeErr.Error())
		log.Logger.Error("Try to decode secretId fail", log.Error(decodeErr))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerSecretKey, decodeErr := cipher.AesDePassword(models.Config.Auth.PasswordSeed, providerInfoData.SecretKey)
	if decodeErr != nil {
		err = fmt.Errorf("Try to decode secretId fail: %s", decodeErr.Error())
		log.Logger.Error("Try to decode secretKey fail", log.Error(decodeErr))
		rowData["errorMessage"] = err.Error()
		return
	}
	*/
	// providerSecretId := providerInfoData.SecretId
	// providerSecretKey := providerInfoData.SecretKey

	// Get provider data
	sqlCmd = `SELECT * FROM provider WHERE id=?`
	paramArgs = []interface{}{providerInfoData.Provider}
	var providerList []*models.ProviderTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerList)
	if err != nil {
		err = fmt.Errorf("Get provider error:%s", err.Error())
		log.Logger.Error("Get provider error", log.String("providerId", providerInfoData.Provider), log.Error(err))
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
	/*
	regionProviderInfo := models.RegionProviderData{}
	regionProviderInfo.ProviderInfoId = providerInfoId
	regionProviderInfo.ProviderName = providerData.Name
	regionProviderInfo.ProviderVersion = providerData.Version
	regionProviderInfo.SecretId = providerSecretId
	regionProviderInfo.SecretKey = providerSecretKey
	regionProviderInfo.SecretIdAttrName = providerData.SecretIdAttrName
	regionProviderInfo.SecretKeyAttrName = providerData.SecretKeyAttrName
	regionProviderInfo.RegionAttrName = providerData.RegionAttrName

	regionProviderInfoByte, err := json.Marshal(regionProviderInfo)
	if err != nil {
		err = fmt.Errorf("Try to marshal regionProviderInfo fail: %s", err.Error())
		log.Logger.Error("Try to marshal regionProviderInfo fail", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerTfContent := string(regionProviderInfoByte)
	*/
	/*
	providerTfContent := "provider + \"" + providerData.Name + "\" {"
	providerTfContent += providerData.SecretIdAttrName + " = \"" + providerSecretId + "\","
	providerTfContent += providerData.SecretKeyAttrName + " = \"" + providerSecretKey + "\","
	providerTfContent += providerData.RegionAttrName + " = \"" + reqParam["asset_id"].(string)
	providerTfContent += "}"
	 */

	/*
	enCodeproviderTfContent, encodeErr := cipher.AesEnPassword(models.Config.Auth.PasswordSeed, providerTfContent)
	if encodeErr != nil {
		err = fmt.Errorf("Try to encode enCodeproviderTfContent fail,%s ", encodeErr.Error())
		log.Logger.Error("Try to encode enCodeproviderTfContent fail", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	*/
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

func TerraformOperation(plugin string, action string, reqParam map[string]interface{}) (rowData map[string]interface{}, err error) {
	rowData = make(map[string]interface{})
	rowData["callbackParameter"] = reqParam["callbackParameter"].(string)
	rowData["errorCode"] = "1"
	rowData["errorMessage"] = ""

	defer func(){
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
		err = fmt.Errorf("Get interfaceInfo error:%s", err.Error())
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
	sqlCmd = `SELECT * FROM resource_data WHERE region_id=?`
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
	resourceData := resourceDataInfoList[0]
	/*
	decodeProviderInfoStr, decodeErr := cipher.AesDePassword(models.Config.Auth.PasswordSeed, resourceData.TfFile)
	if decodeErr != nil {
		err = fmt.Errorf("Try to decode resourceData tfFile fail: %s", decodeErr.Error())
		log.Logger.Error("Try to decode resourceData tfFile fail", log.Error(decodeErr))
		rowData["errorMessage"] = err.Error()
		return
	}

	var regionProviderData models.RegionProviderData
	err = json.Unmarshal([]byte(decodeProviderInfoStr), &regionProviderData)
	if err != nil {
		err = fmt.Errorf("Unmarshal decodeProviderInfoStr fail: %s", err.Error())
		log.Logger.Error("Unmarshal decodeProviderInfoStr fail", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	*/
	/*
	providerInfoData := models.ProviderInfoTable{Id: regionProviderData.ProviderInfoId, SecretId: regionProviderData.SecretId, SecretKey: regionProviderData.SecretKey}
	providerData := models.ProviderTable{Name:regionProviderData.ProviderName, Version: regionProviderData.ProviderVersion,
		SecretIdAttrName: regionProviderData.SecretIdAttrName, SecretKeyAttrName: regionProviderData.SecretKeyAttrName,
		RegionAttrName: regionProviderData.RegionAttrName}
	*/

	// Get providerInfo data
	// providerInfoId := regionProviderData.ProviderInfoId
	providerInfoId := reqParam["provider_info"].(string)
	sqlCmd = `SELECT * FROM provider_info WHERE id=?`
	paramArgs = []interface{}{providerInfoId}
	var providerInfoList []*models.ProviderInfoTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&providerInfoList)
	if err != nil {
		err = fmt.Errorf("Get providerInfo error:%s", err.Error())
		log.Logger.Error("Get providerInfo error", log.String("providerInfoId", providerInfoId), log.Error(err))
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
		err = fmt.Errorf("Try to decode secretId fail: %s", decodeErr.Error())
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
		err = fmt.Errorf("Get provider error:%s", err.Error())
		log.Logger.Error("Get provider error", log.String("providerId", providerId), log.Error(err))
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
	// providerVersion := providerList[0].Version

	// Get source list by interfaceId and provider
	sqlCmd = `SELECT * FROM source WHERE interface=? AND provider=?`
	paramArgs = []interface{}{interfaceData.Id, providerData.Id}
	var sourceList []*models.SourceTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&sourceList)
	if err != nil {
		err = fmt.Errorf("Get source list by interface:%s and provider:%s error:%s", interfaceData.Id, providerData.Id, err.Error())
		log.Logger.Error("Get source list by interface and provider error", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	if len(sourceList) == 0 {
		err = fmt.Errorf("Source list can not be found by interface:%s and provider:%s", interfaceData.Id, providerData.Id)
		log.Logger.Warn("Source list can not be found by interface and provider", log.String("interface", interfaceData.Id), log.String("provider", providerData.Id), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	sourceData := sourceList[0]

	// Get region data
	regionData := resourceData

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

	//workDirPath := terraformFilePath + providerData.Name + "/" + regionData.ResourceAssetId + "/" + plugin + "/" +
	//	reqParam["requestId"].(string) + "/" + dirPathResourceId
	//if action != "destroy" {
	//	workDirPath += "/" + sourceData.Name
	//}

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
		// init version
		// Get resource_asset_id by resourceId
		resourceId := reqParam["id"].(string)
		sqlCmd = `SELECT * FROM resource_data WHERE resource_id=?`
		paramArgs = []interface{}{resourceId}
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
		err = TerraformDestroy(workDirPath, sourceData, providerData, providerInfoData, regionData, resourceData.ResourceAssetId)
		if err != nil {
			err = fmt.Errorf("Handle TerraformDestroy error: %s", err.Error())
			log.Logger.Error("Handle TerraformDestroy error", log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
		// TODO del item in resource_data
		_, err = x.Exec("DELETE FROM resource_data WHERE id=?", resourceData.Id)
		rowData["errorCode"] = "0"
	} else {
		err = fmt.Errorf("Action: %s is inValid", action)
		log.Logger.Error("Action is inValid", log.String("action", action), log.Error(err))
		rowData["errorMessage"] = err.Error()
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
		err = fmt.Errorf("Parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	sqlCmd = `SELECT * FROM resource_data WHERE resource=? AND resource_id=?`
	paramArgs = []interface{}{source, reqParam[parameterData.Name]}
	var resourceDataList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		err = fmt.Errorf("Get resource_data error: %s", err.Error())
		log.Logger.Error("Get resource_data error", log.String("source", source), log.String("resource_id", reqParam[parameterData.Name].(string)), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		err = fmt.Errorf("Resource_data can not be found by source:%s and resource_id:%s", source, reqParam[parameterData.Name])
		log.Logger.Warn("Resource_data can not be found by source and resource_id", log.String("source", source), log.String("value", reqParam[parameterData.Name].(string)), log.Error(err))
		return
	}
	arg = resourceDataList[0].ResourceAssetId
	return
}

func reverseConvertData(parameterData *models.ParameterTable, source string, tfstateVal interface{}) (argKey string, argVal string, err error) {
	/*
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
		err = fmt.Errorf("Parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	 */

	sqlCmd := `SELECT * FROM resource_data WHERE resource=? AND resource_asset_id=?`
	paramArgs := []interface{}{source, tfstateVal}
	var resourceDataList []*models.ResourceDataTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		err = fmt.Errorf("Get resource_data by source:%s and resource_asset_id:%s error:%s", source, tfstateVal, err.Error())
		log.Logger.Error("Get resource_data error", log.String("source", source), log.String("resource_asset_id", tfstateVal.(string)), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		err = fmt.Errorf("Resource_data can not be found by source:%s and resource_asset_id:%s", source, tfstateVal)
		log.Logger.Warn("Resource_data can not be found by source and resource_asset_id", log.String("source", source), log.String("value", tfstateVal.(string)), log.Error(err))
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
		err = fmt.Errorf("Parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", parameterId), log.Error(err))
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
		err = fmt.Errorf("Template_value can not be found by template:%s and value:%s", parameterData.Template, reqParam[parameterData.Name])
		log.Logger.Warn("Template_value can not be found by template and value", log.String("template", parameterData.Template), log.String("value", reqParam[parameterData.Name].(string)), log.Error(err))
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
		err = fmt.Errorf("Provider_template_value can not be found by template_value:%s and provider:%s", parameterData.Template)
		log.Logger.Warn("Provider_template_value can not be found by template_value and provider", log.String("template_value", templateValueData.Id), log.String("provider", providerName), log.Error(err))
		return
	}
	arg = providerTemplateValueList[0].Value
	return
}

func reverseConvertTemplate(parameterId string, providerName string, tfstateVal interface{}) (argKey string, argVal string, err error) {
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
		err = fmt.Errorf("Parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	sqlCmd = `SELECT t1.* FROM template_value AS t1 LEFT JOIN provider_template_value AS t2 ON t1.id=t2.template_value WHERE t2.provider=? AND t2.value=?`
	paramArgs = []interface{}{providerName, tfstateVal}
	var templateValueList []*models.TemplateValueTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&templateValueList)
	if err != nil {
		log.Logger.Error("Get tempalte_value data error", log.String("provider", providerName), log.String("tfstateVal", tfstateVal.(string)), log.Error(err))
		return
	}
	if len(templateValueList) == 0 {
		err = fmt.Errorf("Template_value can not be found by provider:%s and tfstateValue:%s", providerName, tfstateVal)
		log.Logger.Warn("Template_value can not be found by provider and tfstateValue", log.String("provider", providerName), log.String("tfstateValue", tfstateVal.(string)), log.Error(err))
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
		err = fmt.Errorf("Tfstate_attribute can not be found by id:%s", tfstateAttributeId)
		log.Logger.Warn("Tfstate_attribute can not be found by id", log.String("id", tfstateAttributeId), log.Error(err))
		return
	}

	tfStateAttributeData := tfStateAttributeList[0]
	if _, ok := sourceIdList[tfStateAttributeData.Source]; !ok {
		err = fmt.Errorf("Tfstate_attribute's source:%s is config error", tfStateAttributeData.Source)
		log.Logger.Error("Tfstate_attribute's source is config error", log.String("tfstate_attribute_source", tfStateAttributeData.Source), log.Error(err))
		return
	}
	if _, ok := handlingSourceIds[tfStateAttributeData.Source]; !ok {
		err = fmt.Errorf("Tfstate_attribute's source:%s is config error, dead loop", tfStateAttributeData.Source)
		log.Logger.Error("Tfstate_attribute's source is config error, dead loop", log.String("tfstate_attribute_source", tfStateAttributeData.Source), log.Error(err))
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
		err = fmt.Errorf("Tf_argument list can not be found by tfstate_attribute source:%s", tfStateAttributeData.Source)
		log.Logger.Warn("Tf_argument list can not be found by tfstate_attribute source", log.String("tfstate_attribute_source", tfStateAttributeData.Source), log.Error(err))
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
			arg, err = convertAttr(tfArgumentList[i].RelativeTfstateAttribute, sourceIdList, handlingSourceIds, providerName, reqParam)
		case models.ConvertWay["Direct"]:
			arg, err = convertDirect(tfArgumentList[i].Parameter, tfArgumentList[i].DefaultValue, reqParam)
		}
		if err != nil {
			log.Logger.Error("Convert parameter:%s error", log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
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
		err = fmt.Errorf("Parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	if reqParam[parameterData.Name] == tfArgument.RelativeParameterValue {
		arg = reqParam[parameterData.Name]
	}
	return
}

func reverseConvertContext(parameterId string, tfstateVal interface{}) (argKey string, argVal interface{}, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{parameterId}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", parameterId), log.Error(err))
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
		err = fmt.Errorf("Parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", parameterId), log.Error(err))
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

func reverseConvertDirect(parameterId string, tfstateVal interface{}) (argKey string, argVal interface{}, err error) {
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{parameterId}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		log.Logger.Error("Get parameter data error", log.String("parameterId", parameterId), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter can not be found by id:%s", parameterId)
		log.Logger.Warn("Parameter can not be found by id", log.String("id", parameterId), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	argKey = parameterData.Name
	argVal = tfstateVal
	return
}
