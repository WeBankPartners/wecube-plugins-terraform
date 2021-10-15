package db

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"path"
	"reflect"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"syscall"
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

func GenDir(dirPath string) (err error) {
	_, err = os.Stat(dirPath)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.MkdirAll(dirPath, os.ModePerm)
			if err != nil {
				err = fmt.Errorf("Make dir: %s error: %s", dirPath, err.Error())
				log.Logger.Error("Make dir error", log.String("dirPath", dirPath), log.Error(err))
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", dirPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("dirPath", dirPath), log.Error(err))
			return
		}
	}
	return
}

func DelDir(dirPath string) (err error) {
	_, err = os.Stat(dirPath)
	if err != nil {
		if os.IsNotExist(err) == false {
			err = fmt.Errorf("Os stat dir: %s error: %s", dirPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("dirPath", dirPath), log.Error(err))
			return
		}
		return
	}
	if dirPath == "" {
		return
	}
	// clear dir
	if dirPath[len(dirPath)-1] == '/' {
		dirPath = dirPath[:len(dirPath)-1]
	}
	dir, err := ioutil.ReadDir(dirPath)
	for _, d := range dir {
		tmpPath := path.Join([]string{dirPath, d.Name()}...)
		os.RemoveAll(tmpPath)
	}
	return
}

func GenTfFile(dirPath string, sourceData *models.SourceTable, action string, resourceId string, tfArguments map[string]interface{}) (tfFileContentStr string, err error) {
	var tfFilePath string
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
		return
	}
	tfFileContentStr = string(tfFileContent)
	return
}

func GenProviderFile(dirPath string, providerData *models.ProviderTable, providerInfo *models.ProviderInfoTable, regionData *models.ResourceDataTable) (err error) {
	// provider
	providerContentData := make(map[string]map[string]interface{})
	providerContentData[providerData.Name] = make(map[string]interface{})
	providerContentData[providerData.Name][providerData.SecretIdAttrName] = providerInfo.SecretId
	providerContentData[providerData.Name][providerData.SecretKeyAttrName] = providerInfo.SecretKey
	providerContentData[providerData.Name][providerData.RegionAttrName] = regionData.ResourceAssetId

	// terraform
	terraformData := make(map[string]map[string]map[string]interface{})
	terraformData["required_providers"] = make(map[string]map[string]interface{})
	terraformData["required_providers"][providerData.Name] = make(map[string]interface{})
	terraformData["required_providers"][providerData.Name]["source"] = providerData.NameSpace + "/" + providerData.Name
	terraformData["required_providers"][providerData.Name]["version"] = providerData.Version

	providerFileData := make(map[string]interface{})
	providerFileData["terraform"] = terraformData
	providerFileData["provider"] = providerContentData

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
	return
}

func GenVersionFile(dirPath string, providerData *models.ProviderTable) (err error) {
	return
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

		genVersionTfFilePath := dirPath + "/version.tf"
		err = GenFile(versionTfFileContent, genVersionTfFilePath)
		if err != nil {
			err = fmt.Errorf("Gen versionTfFile: %s error: %s", genVersionTfFilePath, err.Error())
			log.Logger.Error("Gen versionTfFile error", log.String("genVersionTfFilePath", genVersionTfFilePath), log.Error(err))
			return
		}
	}
	return
}

func GenTerraformProviderSoftLink(dirPath string, providerData *models.ProviderTable) (err error) {
	targetTerraformProviderPath := dirPath + "/.terraform/providers/registry.terraform.io/" + providerData.NameSpace + "/" + providerData.Name + "/" + providerData.Version

	terraformFilePath := models.Config.TerraformFilePath
	if terraformFilePath[len(terraformFilePath)-1] != '/' {
		terraformFilePath += "/"
	}

	_, err = os.Stat(targetTerraformProviderPath)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.MkdirAll(targetTerraformProviderPath, os.ModePerm)
			if err != nil {
				err = fmt.Errorf("Make dir: %s error: %s", dirPath, err.Error())
				log.Logger.Error("Make dir error", log.String("dirPath", dirPath), log.Error(err))
				return
			}
			terraformProviderPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version + "/" + models.Config.TerraformProviderOsArch
			err = os.Symlink(terraformProviderPath, targetTerraformProviderPath+"/"+models.Config.TerraformProviderOsArch)
			if err != nil {
				err = fmt.Errorf("Make soft link : %s error: %s", targetTerraformProviderPath, err.Error())
				log.Logger.Error("Make soft link error", log.String("softLink", targetTerraformProviderPath), log.Error(err))
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", targetTerraformProviderPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("targetTerraformProviderPath", targetTerraformProviderPath), log.Error(err))
			return
		}
	}
	return
}

func GenTerraformLockHclSoftLink(dirPath string, providerData *models.ProviderTable) (err error) {
	targetTerraformLockHclPath := dirPath + "/.terraform.lock.hcl"
	terraformFilePath := models.Config.TerraformFilePath
	if terraformFilePath[len(terraformFilePath)-1] != '/' {
		terraformFilePath += "/"
	}
	_, err = os.Stat(targetTerraformLockHclPath)
	if err != nil {
		if os.IsNotExist(err) {
			terraformLockHclPath := terraformFilePath + "providers/" + providerData.Name + "/" + providerData.Version + "/" + models.Config.TerraformProviderOsArch + "_hcl" + "/.terraform.lock.hcl"
			err = os.Symlink(terraformLockHclPath, targetTerraformLockHclPath)
			if err != nil {
				err = fmt.Errorf("Make soft link : %s error: %s", targetTerraformLockHclPath, err.Error())
				log.Logger.Error("Make soft link error", log.String("softLink", targetTerraformLockHclPath), log.Error(err))
				return
			}
		} else {
			err = fmt.Errorf("Os stat dir: %s error: %s", targetTerraformLockHclPath, err.Error())
			log.Logger.Error("Os stat dir error", log.String("targetTerraformLockHclPath", targetTerraformLockHclPath), log.Error(err))
			return
		}
	}
	return
}

func DelProviderFile(dirPath string) (err error) {
	providerFilePath := dirPath + "/provider.tf.json"
	err = DelFile(providerFilePath)
	if err != nil {
		err = fmt.Errorf("Delete provider.tf.json file:%s error:%s", providerFilePath, err.Error())
		log.Logger.Error("Delete provider.tf.json file error", log.String("providerFilePath", providerFilePath), log.Error(err))
		return
	}
	return
}

func DelTfstateFile(dirPath string) (err error) {
	tfstateFilePath := dirPath + "/terraform.tfstate"
	err = DelFile(tfstateFilePath)
	if err != nil {
		err = fmt.Errorf("Delete terraform.tfstate file:%s error:%s", tfstateFilePath, err.Error())
		log.Logger.Error("Delete terraform.tfstate file error", log.String("providerFilePath", tfstateFilePath), log.Error(err))
		return
	}
	// delete the terraform.tfstate.backup
	tfstateFilePath = dirPath + "/terraform.tfstate.backup"
	err = DelFile(tfstateFilePath)
	if err != nil {
		err = fmt.Errorf("Delete terraform.tfstate.backup file:%s error:%s", tfstateFilePath, err.Error())
		log.Logger.Error("Delete terraform.tfstate.backup file error", log.String("providerFilePath", tfstateFilePath), log.Error(err))
		return
	}
	return
}

func GenWorkDirPath(resourceId string,
	requestSn string,
	requestId string,
	providerData *models.ProviderTable,
	regionData *models.ResourceDataTable,
	plugin string,
	sourceData *models.SourceTable) (workDirPath string) {

	terraformFilePath := models.Config.TerraformFilePath
	if terraformFilePath[len(terraformFilePath)-1] != '/' {
		terraformFilePath += "/"
	}
	dirPathResourceId := resourceId
	if dirPathResourceId == "" {
		dirPathResourceId = requestSn
	}
	workDirPath = terraformFilePath + providerData.Name + "/" + regionData.ResourceAssetId + "/" + plugin + "/" +
		requestId + "/" + dirPathResourceId + "/" + sourceData.Name
	return
}

func execRemoteWithTimeout(cmdStr []string, timeOut int) (out string, err error) {
	if len(cmdStr) == 0 {
		err = fmt.Errorf("cmdStr can not be empty")
		return
	}
	cmdStr = append([]string{"-c"}, cmdStr...)
	doneChan := make(chan string)
	// defer close(doneChan)

	tmpCmd := exec.Command(models.BashCmd, cmdStr...)
	tmpCmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	go func(a chan string, ct *exec.Cmd) {
		/*
			b, err := ct.Output()
			if err != nil {
				a <- "error:" + err.Error()
			}
			a <- string(b)
		*/
		var stdout, stderr bytes.Buffer
		ct.Stdout = &stdout
		ct.Stderr = &stderr
		cmdErr := ct.Run()
		if cmdErr != nil {
			a <- "error:" + string(stderr.Bytes())
		} else {
			a <- string(stdout.Bytes())
		}
	}(doneChan, tmpCmd)
	select {
	case tmpVal := <-doneChan:
		out = tmpVal
	case <-time.After(time.Duration(timeOut) * time.Second):
		out = fmt.Sprintf("error: %s timeout %d(s)", cmdStr, timeOut)
		syscall.Kill(-tmpCmd.Process.Pid, syscall.SIGKILL)
	}
	if strings.HasPrefix(out, "error:") {
		err = fmt.Errorf(out)
	}
	return
}

func TerraformImport(dirPath, address, resourceAssetId string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " import -no-color " + address + " " + resourceAssetId
	/*
		cmd := exec.Command(models.BashCmd, "-c", cmdStr)
		var stdout, stderr bytes.Buffer
		cmd.Stdout = &stdout
		cmd.Stderr = &stderr
		cmdErr := cmd.Run()
	*/
	_, cmdErr := execRemoteWithTimeout([]string{cmdStr}, models.CommandTimeOut)
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		// outPutStr := string(stderr.Bytes())
		outPutStr := cmdErr.Error()
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\s]*)`)
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
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " plan -input=false -no-color"
	/*
		cmd := exec.Command(models.BashCmd, "-c", cmdStr)
		var stdout, stderr bytes.Buffer
		cmd.Stdout = &stdout
		cmd.Stderr = &stderr
		cmdErr := cmd.Run()
	*/
	output, cmdErr := execRemoteWithTimeout([]string{cmdStr}, models.CommandTimeOut)
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		// outPutStr := string(stderr.Bytes())
		outPutStr := cmdErr.Error()
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\s]*)`)
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
	err = GenFile([]byte(output), filePath)
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
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " apply -auto-approve -no-color"
	/*
		cmd := exec.Command(models.BashCmd, "-c", cmdStr)
		var stdout, stderr bytes.Buffer
		cmd.Stdout = &stdout
		cmd.Stderr = &stderr
		cmdErr := cmd.Run()
	*/
	_, cmdErr := execRemoteWithTimeout([]string{cmdStr}, models.CommandTimeOut)
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		// outPutStr := string(stderr.Bytes())
		outPutStr := cmdErr.Error()
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\s]*)`)
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
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " destroy -auto-approve -no-color"
	/*
		cmd := exec.Command(models.BashCmd, "-c", cmdStr)
		var stdout, stderr bytes.Buffer
		cmd.Stdout = &stdout
		cmd.Stderr = &stderr
		cmdErr := cmd.Run()
	*/
	_, cmdErr := execRemoteWithTimeout([]string{cmdStr}, models.CommandTimeOut)
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		// outPutStr := string(stderr.Bytes())
		outPutStr := cmdErr.Error()
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\s]*)`)
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
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " init -no-color" + " -plugin-dir=" + dirPath + "/.terraform/providers"
	/*
		cmd := exec.Command(models.BashCmd, "-c", cmdStr)
		var stdout, stderr bytes.Buffer
		cmd.Stdout = &stdout
		cmd.Stderr = &stderr
		cmdErr := cmd.Run()
	*/
	_, cmdErr := execRemoteWithTimeout([]string{cmdStr}, models.CommandTimeOut)
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		// outPutStr := string(stderr.Bytes())
		outPutStr := cmdErr.Error()
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\s]*)`)
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

func DownloadProviderByTerraformInit(dirPath string) (err error) {
	cmdStr := models.Config.TerraformCmdPath + " -chdir=" + dirPath + " init -no-color"
	_, cmdErr := execRemoteWithTimeout([]string{cmdStr}, models.DownloadProviderTimeOut)
	if cmdErr != nil {
		// outStr, errStr := string(stdout.Bytes()), string(stderr.Bytes())
		// outPutStr := string(stderr.Bytes())
		outPutStr := cmdErr.Error()
		errorMsgRegx := regexp.MustCompile(`Error: ([\S\s]*)`)
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

func handleOutPutArgs(outPutArgs map[string]interface{},
	outPutParameterNameMap map[string]*models.ParameterTable,
	tfstateAttrParamMap map[string]*models.TfstateAttributeTable,
	reqParam map[string]interface{},
	isInternalAction bool) (outPutResultList []map[string]interface{}, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("HandleOutPutArgs error, error:%v", r)
		}
	}()
	outPutResultList = []map[string]interface{}{}
	// flat outPutParam data
	flatOutPutArgs, hasTerraformOutPutPrefix, _ := handleFlatOutPutParam(outPutArgs)

	// delete the item that id is nil or nil []interface{}
	tmpOutPutResultList := []map[string]interface{}{}
	for i := range flatOutPutArgs {
		/*
			if _, ok := flatOutPutArgs[i]["id"]; ok && flatOutPutArgs[i]["id"] == nil {
				flatOutPutArgs[i]["id"] = ""
			}
			if isResultIdValid(flatOutPutArgs[i]["id"]) == false {
				continue
			}
		*/
		tmpOutPutResultList = append(tmpOutPutResultList, flatOutPutArgs[i])
	}

	var mapOutPutArgs []map[string]interface{}
	if hasTerraformOutPutPrefix {
		// 将数组类型的值进行一一映射
		mapOutPutArgs, _ = handleSliceMapOutPutParam(tmpOutPutResultList)
	} else {
		mapOutPutArgs = tmpOutPutResultList
	}

	for i := range mapOutPutArgs {
		if !isInternalAction {
			for k, v := range outPutParameterNameMap {
				if _, okParam := tfstateAttrParamMap[v.Id]; !okParam {
					if _, ok := reqParam[k]; ok {
						mapOutPutArgs[i][k] = reqParam[k]
						if k == "password" {
							if _, tmpOk := reqParam["seed"]; !tmpOk {
								log.Logger.Error("Try to get seed failed")
							} else {
								enCodeStr, encodeErr := cipher.AesEnPasswordByGuid(reqParam["id"].(string), reqParam["seed"].(string), reqParam[k].(string), "")
								if encodeErr != nil {
									log.Logger.Error("Try to encode failed", log.Error(encodeErr))
								} else {
									mapOutPutArgs[i][k] = enCodeStr
								}
							}
						}
					}
				} else {
					if v.Sensitive == "Y" {
						if _, tmpOk := reqParam["seed"]; !tmpOk {
							log.Logger.Error("Try to get seed failed")
						} else {
							enCodeStr, encodeErr := cipher.AesEnPasswordByGuid(reqParam["id"].(string), reqParam["seed"].(string), mapOutPutArgs[i][k].(string), "")
							if encodeErr != nil {
								log.Logger.Error("Try to encode failed", log.Error(encodeErr))
							} else {
								mapOutPutArgs[i][k] = enCodeStr
							}
						}
					}
				}
			}
		}
		outPutResultList = append(outPutResultList, mapOutPutArgs[i])
	}

	// construct the object

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

func handleFlatOutPutParam(outPutArgs map[string]interface{}) (retOutPutArgs []map[string]interface{}, hasTerraformOutPutPrefix bool, err error) {
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
				ret, _, _ := handleFlatOutPutParam(tmpData[i])
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

func RegionApply(reqParam map[string]interface{}, interfaceData *models.InterfaceTable) (rowData map[string]interface{}, err error) {
	rowData = make(map[string]interface{})
	rowData["callbackParameter"] = reqParam["callbackParameter"].(string)
	rowData["errorCode"] = "1"
	rowData["errorMessage"] = ""

	providerInfoId := reqParam["provider_info"].(string)
	// Get providerInfo data
	// sqlCmd := `SELECT * FROM provider_info WHERE id=?`
	sqlCmd := `SELECT * FROM provider_info WHERE name=?`
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
		err = fmt.Errorf("Source can not be found by interface:%s and provider:%s", interfaceData.Id, providerData.Id)
		log.Logger.Warn("Source can not be found by interface and provider", log.String("interface", interfaceData.Id), log.String("provider", providerData.Id), log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	sourceData := sourceList[0]

	uuid := guid.CreateGuid()
	createTime := time.Now().Format(models.DateTimeFormat)
	resourceId := reqParam["id"].(string)
	resourceAssetId := reqParam["asset_id"].(string)
	createUser := reqParam["operator_user"].(string)
	tfFile := fmt.Sprintf("{\"resource\":{\"%s\":{\"%s\":{\"name\":\"%s\"}}}}", sourceData.Name, resourceId, resourceId)
	tfstateFile := fmt.Sprintf("{\"resources\":{\"instances\":{\"attributes\":{\"name\":\"%s\"}}}}", resourceAssetId)

	// get old resource data
	var oldResourceDataList []*models.ResourceDataTable
	sqlCmd = "SELECT * FROM resource_data WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"

	if _, ok := reqParam[models.ResourceDataDebug]; ok {
		sqlCmd = "SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"
	}

	paramArgs = []interface{}{sourceData.Id, resourceId, resourceId, resourceAssetId}
	err = x.SQL(sqlCmd, paramArgs...).Find(&oldResourceDataList)
	if err != nil {
		err = fmt.Errorf("Get old_resource data by resource:%s and resource_id:%s error: %s", sourceData.Id, resourceId, err.Error())
		log.Logger.Error("Get old_resource_data by resource and resource_id error", log.String("resource", sourceData.Id), log.String("resource_id", resourceId), log.Error(err))
		return
	}

	if _, ok := reqParam[models.ResourceDataDebug]; ok {
		if len(oldResourceDataList) == 0 {
			_, err = x.Exec("INSERT INTO resource_data_debug(id,resource,resource_id,resource_asset_id,tf_file,tf_state_file,region_id,create_time,create_user,update_time,update_user) VALUE (?,?,?,?,?,?,?,?,?,?,?)",
				uuid, sourceData.Id, resourceId, resourceAssetId, tfFile, tfstateFile, resourceId, createTime, createUser, createTime, createUser)
		} else {
			//err = fmt.Errorf("the region:%s is existed", resourceId)
		}
	} else {
		if len(oldResourceDataList) == 0 {
			_, err = x.Exec("INSERT INTO resource_data(id,resource,resource_id,resource_asset_id,tf_file,tf_state_file,region_id,create_time,create_user,update_time,update_user) VALUE (?,?,?,?,?,?,?,?,?,?,?)",
				uuid, sourceData.Id, resourceId, resourceAssetId, tfFile, tfstateFile, resourceId, createTime, createUser, createTime, createUser)
		} else {
			//err = fmt.Errorf("the region:%s is existed", resourceId)
		}
	}

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

func handleApplyOrQuery(action string, reqParam map[string]interface{}, sourceData *models.SourceTable, regionData *models.ResourceDataTable) (rowData map[string]interface{}, err error) {
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
		tfFile := fmt.Sprintf("{\"resource\":{\"%s\":{\"%s\":{\"name\":\"%s\"}}}}", sourceData.Name, resourceId, resourceId)
		tfstateFile := fmt.Sprintf("{\"resources\":{\"instances\":{\"attributes\":{\"name\":\"%s\"}}}}", resourceAssetId)

		// get old resource data
		var oldResourceDataList []*models.ResourceDataTable
		sqlCmd := "SELECT * FROM resource_data WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			sqlCmd = "SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"
		}

		paramArgs := []interface{}{sourceData.Id, resourceId, regionData.RegionId, resourceAssetId}
		err = x.SQL(sqlCmd, paramArgs...).Find(&oldResourceDataList)
		if err != nil {
			err = fmt.Errorf("Get old_resource data by resource:%s and resource_id:%s error: %s", sourceData.Id, resourceId, err.Error())
			log.Logger.Error("Get old_resource_data by resource and resource_id error", log.String("resource", sourceData.Id), log.String("resource_id", resourceId), log.Error(err))
			return
		}

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			if len(oldResourceDataList) == 0 {
				_, err = x.Exec("INSERT INTO resource_data_debug(id,resource,resource_id,resource_asset_id,tf_file,tf_state_file,region_id,create_time,create_user,update_time,update_user) VALUE (?,?,?,?,?,?,?,?,?,?,?)",
					uuid, sourceData.Id, resourceId, resourceAssetId, tfFile, tfstateFile, regionId, createTime, createUser, createTime, createUser)
			} else {
				// err = fmt.Errorf("the resource_id:%s is existed", resourceId)
			}
		} else {
			if len(oldResourceDataList) == 0 {
				_, err = x.Exec("INSERT INTO resource_data(id,resource,resource_id,resource_asset_id,tf_file,tf_state_file,region_id,create_time,create_user,update_time,update_user) VALUE (?,?,?,?,?,?,?,?,?,?,?)",
					uuid, sourceData.Id, resourceId, resourceAssetId, tfFile, tfstateFile, regionId, createTime, createUser, createTime, createUser)
			} else {
				// err = fmt.Errorf("the resource_id:%s is existed", resourceId)
			}
		}

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
		sqlCmd := `SELECT * FROM resource_data WHERE resource_id= AND region_id=?`

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			sqlCmd = `SELECT * FROM resource_data_debug WHERE resource_id=? AND region_id=?`
		}

		paramArgs := []interface{}{resourceId, regionData.RegionId}
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
	plugin string,
	inputResourceData *models.ResourceDataTable) (rowData map[string]interface{}, err error) {

	rowData = make(map[string]interface{})
	rowData["callbackParameter"] = reqParam["callbackParameter"].(string)
	rowData["errorCode"] = "1"
	rowData["errorMessage"] = ""

	var resourceId string
	var resourceData *models.ResourceDataTable
	toDestroyResourceData := []*models.ResourceDataTable{}
	if inputResourceData == nil {
		// Get resource_asset_id by resourceId
		resourceId = reqParam["id"].(string)
		sqlCmd := `SELECT * FROM resource_data WHERE resource_id=? AND region_id=? AND resource=?`

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			sqlCmd = `SELECT * FROM resource_data_debug WHERE resource_id=? AND region_id=? AND resource=?`
		}

		paramArgs := []interface{}{resourceId, regionData.RegionId, sourceData.Id}
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
			err = nil
			rowData["errorCode"] = "0"
			return
		}
		// resourceData = resourceDataInfoList[0]
		toDestroyResourceData = append(toDestroyResourceData, resourceDataInfoList...)
	} else {
		sqlCmd := `SELECT * FROM resource_data WHERE id=?`

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			sqlCmd = `SELECT * FROM resource_data_debug WHERE id=?`
		}

		paramArgs := []interface{}{inputResourceData.Id}
		var resourceDataInfoList []*models.ResourceDataTable
		err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataInfoList)
		if err != nil {
			err = fmt.Errorf("Get resourceDataInfo by resource_id:%s error:%s", resourceId, err.Error())
			log.Logger.Error("Get resourceDataInfo by resource_id error", log.String("resource_id", resourceId), log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
		if len(resourceDataInfoList) == 0 {
			// err = fmt.Errorf("ResourceDataInfo can not be found by resource_id:%s", resourceId)
			// log.Logger.Warn("ResourceDataInfo can not be found by resource_id", log.String("resource_id", resourceId), log.Error(err))
			// rowData["errorMessage"] = err.Error()
			err = nil
			rowData["errorCode"] = "0"
			return
		}
		inputResourceData = resourceDataInfoList[0]
		resourceId = inputResourceData.ResourceId
		resourceData = inputResourceData
		toDestroyResourceData = append(toDestroyResourceData, resourceData)
	}

	// rowData["id"] = resourceId
	for _, resourceData := range toDestroyResourceData {
		if sourceData.TerraformUsed != "N" {
			// Gen the terraform workdir
			err = GenDir(workDirPath)
			if err != nil {
				err = fmt.Errorf("Gen the terraform workdir: %s error: %s", workDirPath, err.Error())
				log.Logger.Error("Gen the terraform workdir error", log.String("workDirPath", workDirPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			// Gen provider.tf.json
			err = GenProviderFile(workDirPath, providerData, providerInfo, regionData)
			if err != nil {
				err = fmt.Errorf("Gen providerFile error: %s", err.Error())
				log.Logger.Error("Gen providerFile error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			defer DelProviderFile(workDirPath)

			// Gen version.tf
			err = GenVersionFile(workDirPath, providerData)
			if err != nil {
				err = fmt.Errorf("Gen versionFile error: %s", err.Error())
				log.Logger.Error("Gen versionFile error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			// Gen softlink of terraform provider file
			err = GenTerraformProviderSoftLink(workDirPath, providerData)
			if err != nil {
				err = fmt.Errorf("Gen terraform provider soft link error: %s", err.Error())
				log.Logger.Error("Gen terraform provider soft link error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			// Gen soft link for .terraform.lock.hcl
			err = GenTerraformLockHclSoftLink(workDirPath, providerData)
			if err != nil {
				err = fmt.Errorf("Gen terraform lock soft link error: %s", err.Error())
				log.Logger.Error("Gen terraform lock soft link error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
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
				// continue
			}
			resourceAssetId := resourceData.ResourceAssetId
			DelTfstateFile(workDirPath)
			if sourceData.ImportSupport != "N" {
				err = TerraformImport(workDirPath, sourceName+"."+uuid, resourceAssetId)
				if err != nil {
					errMsg := err.Error()
					if strings.Contains(errMsg, "Cannot import non-existent remote object") {
						// delet resource_data item
						if _, ok := reqParam[models.ResourceDataDebug]; ok {
							_, err = x.Exec("DELETE FROM resource_data_debug WHERE id=?", resourceData.Id)
						} else {
							_, err = x.Exec("DELETE FROM resource_data WHERE id=?", resourceData.Id)
						}
						DelProviderFile(workDirPath)
						continue
					}

					err = fmt.Errorf("Do TerraformImport error:%s", err.Error())
					log.Logger.Error("Do TerraformImport error", log.Error(err))
					rowData["errorMessage"] = err.Error()
					// continue
					return
				}
			} else {
				// get tfstate file from resource_data table and gen it
				tfstateFileContent := resourceData.TfStateFile
				tfstateFilePath := workDirPath + "/terraform.tfstate"
				GenFile([]byte(tfstateFileContent), tfstateFilePath)
			}

			// clear tf file
			os.Truncate(tfFilePath, 0)

			err = TerraformDestroy(workDirPath)
			if err != nil {
				err = fmt.Errorf("Do TerraformDestroy error: %s", err.Error())
				log.Logger.Error("Do TerraformDestroy error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
				// continue
			}

			// Del provider file
			err = DelProviderFile(workDirPath)
			// err = DelFile(providerFilePath)
			if err != nil {
				err = fmt.Errorf("Do delete provider file error: %s", err.Error())
				log.Logger.Error("Do delete provider file error", log.Error(err))
				rowData["errorMessage"] = err.Error()
			}
		}

		// delet resource_data item
		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			_, err = x.Exec("DELETE FROM resource_data_debug WHERE id=?", resourceData.Id)
		} else {
			_, err = x.Exec("DELETE FROM resource_data WHERE id=?", resourceData.Id)
		}
		if err != nil {
			err = fmt.Errorf("Delete resource data by id:%s error: %s", resourceData.Id, err.Error())
			log.Logger.Error("Delete resource data by id error", log.String("id", resourceData.Id), log.Error(err))
			rowData["errorMessage"] = err.Error()
			return
		}
	}

	rowData["errorCode"] = "0"
	return
}

func TerraformOperation(plugin string, action string, reqParam map[string]interface{}, debugFileContent *[]map[string]interface{}) (rowData map[string]interface{}, err error) {
	var curWorkDirPath = []string{}
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("TerraformOperation error: %v", r)
			rowData["errorMessage"] = err.Error()
		}
		if rowData["errorMessage"].(string) != "" && rowData["errorCode"].(string) == "0" {
			rowData["errorCode"] = "1"
		}

		if _, ok := reqParam[models.ResourceDataDebug]; !ok {
			// clear the workDirPath
			for i := range curWorkDirPath {
				DelDir(curWorkDirPath[i])
			}
		}
	}()

	rowData = make(map[string]interface{})
	rowData["callbackParameter"] = reqParam["callbackParameter"].(string)
	rowData["errorCode"] = "1"
	rowData["errorMessage"] = ""

	// Get interface by plugin and action
	var actionName string
	actionName = action
	if actionName == "destroy" {
		actionName = "apply"
	}
	// sqlCmd := `SELECT * FROM interface WHERE plugin=? AND name=?`
	sqlCmd := `SELECT * FROM interface WHERE plugin IN (SELECT id FROM plugin WHERE name=?) AND name=?`
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
	sqlCmd = `SELECT * FROM resource_data WHERE resource_id=? AND region_id=?`

	if _, ok := reqParam[models.ResourceDataDebug]; ok {
		sqlCmd = `SELECT * FROM resource_data_debug WHERE resource_id=? AND region_id=?`
	}

	paramArgs = []interface{}{regionId, regionId}
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
	// sqlCmd = `SELECT * FROM provider_info WHERE id=?`
	sqlCmd = `SELECT * FROM provider_info WHERE name=?`
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
	providerSecretId, decodeErr := cipher.AesDePasswordByGuid(models.PGuid, models.Config.Auth.PasswordSeed, providerInfoData.SecretId)
	if decodeErr != nil {
		err = fmt.Errorf("Try to decode secretId fail: %s", decodeErr.Error())
		log.Logger.Error("Try to decode secretId fail", log.Error(decodeErr))
		rowData["errorMessage"] = err.Error()
		return
	}
	providerSecretKey, decodeErr := cipher.AesDePasswordByGuid(models.PGuid, models.Config.Auth.PasswordSeed, providerInfoData.SecretKey)
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

	// Get the sorted source list
	var sortedSourceList []*models.SourceTable
	sortedSourceList, err = getSortedSourceList(sourceList, interfaceData, providerData)
	if err != nil {
		err = fmt.Errorf("Get sorted source list error: %s", err.Error())
		log.Logger.Warn("Get sorted source list error", log.Error(err))
		rowData["errorMessage"] = err.Error()
		return
	}
	simulateResourceData := make(map[string][]map[string]interface{})
	if (action == "apply" || action == "query") && sourceList[0].TerraformUsed != "N" {
		// fmt.Printf("%v\n", sortedSourceList)

		resourceId := reqParam["id"].(string)
		var rootResourceAssetId interface{}
		rootResourceAssetId = ""
		// resourceAssetId := reqParam["asset_id"].(string)
		// fmt.Printf("%v\n", resourceAssetId)

		reqParam[models.SimulateResourceDataResult] = make(map[string][]map[string]interface{})
		toDestroyList := make(map[string]*models.ResourceDataTable)
		for sourceDataIdx, sortedSourceData := range sortedSourceList {
			simulateResourceData[sortedSourceData.Id] = []map[string]interface{}{}
			reqParam[models.SimulateResourceData] = simulateResourceData
			reqParam[models.SourceDataIdx] = sourceDataIdx

			isInternalAction := false
			// Get all tfArguments of source
			sqlCmd = `SELECT * FROM tf_argument WHERE source=?`
			paramArgs = []interface{}{sortedSourceData.Id}
			var allTfArgumentList []*models.TfArgumentTable
			err = x.SQL(sqlCmd, paramArgs...).Find(&allTfArgumentList)
			if err != nil {
				err = fmt.Errorf("Get tfArgument data by source:%s error:%s", sortedSourceData.Id, err.Error())
				log.Logger.Error("Get tfArgument data by source error", log.String("source", sortedSourceData.Id), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
			if len(allTfArgumentList) == 0 {
				err = fmt.Errorf("TfArgument data can not be got by source:%s ", sortedSourceData.Id)
				log.Logger.Error("TfArgument data by can not be got by source error", log.String("source", sortedSourceData.Id), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			// Get root tfArguments of source
			tfArgName := "ROOT"
			sqlCmd = `SELECT * FROM tf_argument WHERE source=? AND name=?`
			paramArgs = []interface{}{sortedSourceData.Id, tfArgName}
			var rootTfArgumentList []*models.TfArgumentTable
			err = x.SQL(sqlCmd, paramArgs...).Find(&rootTfArgumentList)
			if err != nil {
				err = fmt.Errorf("Get tfArgument data by source:%s and name:%s error:%s", sortedSourceData.Id, tfArgName, err.Error())
				log.Logger.Error("Get tfArgument data by source and name error", log.String("source", sortedSourceData.Id), log.String("name", tfArgName), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			conStructObject := []map[string]interface{}{}
			if len(rootTfArgumentList) == 0 {
				reqParam[models.SourceDataIdx] = 0
				var convertedArgumentData map[string]interface{}
				convertedArgumentData, rootResourceAssetId, err = handleConvertParams(action, sortedSourceData, allTfArgumentList, reqParam, providerData, regionData)
				if err != nil {
					err = fmt.Errorf("Handle convert params error:%s", err.Error())
					log.Logger.Error("Handle convert params error", log.Error(err))
					rowData["errorMessage"] = err.Error()
					return
				}
				conStructObject = append(conStructObject, convertedArgumentData)
			} else {
				if sourceDataIdx > 0 {
					isInternalAction = true
				}
				inPutValSlice := [][]interface{}{}
				handledTfArguments := make(map[string]bool)
				for _, rootTfArgumentData := range rootTfArgumentList {
					handledTfArguments[rootTfArgumentData.Id] = true
					if rootTfArgumentData.Parameter == "" && rootTfArgumentData.RelativeSource == "" {
						err = fmt.Errorf("TfArgument data: %s must have parameter and relative_source", rootTfArgumentData.Id)
						log.Logger.Error("TfArgument data: %s must have parameter and relative_source", log.String("rootTfArgumentId", rootTfArgumentData.Id), log.Error(err))
						rowData["errorMessage"] = err.Error()
						return
					} else if rootTfArgumentData.Parameter != "" {
						convertedArgumentData, _, tmpErr := handleConvertParams(action, sortedSourceData, []*models.TfArgumentTable{rootTfArgumentData}, reqParam, providerData, regionData)
						if tmpErr != nil {
							err = fmt.Errorf("Handle convert params error:%s", err.Error())
							log.Logger.Error("Handle convert params error", log.Error(err))
							rowData["errorMessage"] = err.Error()
							return
						}
						if rootTfArgumentData.Type == "object" {
							var inPutVal []map[string]interface{}
							if rootTfArgumentData.IsMulti == "N" {
								inPutVal = append(inPutVal, convertedArgumentData[rootTfArgumentData.Name].(map[string]interface{}))
							} else {
								inPutVal = convertedArgumentData[rootTfArgumentData.Name].([]map[string]interface{})
							}

							// Get the memberTfArguments of rootTfArgument
							sqlCmd = "SELECT * FROM tf_argument WHERE source=? AND object_name=?"
							var memberTfArguments []*models.TfArgumentTable
							paramArgs = []interface{}{sortedSourceData.Id, rootTfArgumentData.Id}
							err = x.SQL(sqlCmd, paramArgs...).Find(&memberTfArguments)
							if err != nil {
								err = fmt.Errorf("Get memberTfArgument list error:%s", err.Error())
								log.Logger.Error("Get memberTfArgument list error", log.Error(err))
								rowData["errorMessage"] = err.Error()
								return
							}
							if len(memberTfArguments) == 0 {
								err = fmt.Errorf("MemberTfArgument list can not be found by source:%s and object_name:%s", sortedSourceData.Id, rootTfArgumentData.Id)
								log.Logger.Warn("MemberTfArgument list can not be found by source and object_name", log.String("source", sortedSourceData.Id), log.String("object_name", rootTfArgumentData.Id), log.Error(err))
								rowData["errorMessage"] = err.Error()
								return
							}

							for _, v := range memberTfArguments {
								handledTfArguments[v.Id] = true
							}

							convertedInPutVal := []interface{}{}
							for _, v := range inPutVal {
								var tmpTfArguments map[string]interface{}

								if _, ok := reqParam[models.ResourceDataDebug]; ok {
									v[models.ResourceDataDebug] = reqParam[models.ResourceDataDebug]
								}

								tmpTfArguments, _, err = handleConvertParams(action, sortedSourceData, memberTfArguments, v, providerData, regionData)

								if _, ok := reqParam[models.ResourceDataDebug]; ok {
									delete(v, models.ResourceDataDebug)
								}

								if err != nil {
									err = fmt.Errorf("HandleConvertParams error:%s", err.Error())
									log.Logger.Warn("HandleConvertParams error", log.Error(err))
									rowData["errorMessage"] = err.Error()
									return
								}
								convertedInPutVal = append(convertedInPutVal, tmpTfArguments)
							}
							inPutValSlice = append(inPutValSlice, convertedInPutVal)
						} else {
							// get the key name for the ROOT's values in convertedArgumentData
							sqlCmd = "SELECT * FROM tf_argument WHERE source=? AND name!=? AND parameter=?"
							var memberTfArguments []*models.TfArgumentTable
							paramArgs = []interface{}{sortedSourceData.Id, "ROOT", rootTfArgumentData.Parameter}
							err = x.SQL(sqlCmd, paramArgs...).Find(&memberTfArguments)
							if err != nil {
								err = fmt.Errorf("Get memberTfArgument list error:%s", err.Error())
								log.Logger.Error("Get memberTfArgument list error", log.Error(err))
								rowData["errorMessage"] = err.Error()
								return
							}
							if len(memberTfArguments) == 0 {
								err = fmt.Errorf("MemberTfArgument list can not be found by source:%s and parameter:%s", sortedSourceData.Id, rootTfArgumentData.Parameter)
								log.Logger.Warn("MemberTfArgument list can not be found by source and parameter", log.String("source", sortedSourceData.Id), log.String("parameter", rootTfArgumentData.Parameter), log.Error(err))
								rowData["errorMessage"] = err.Error()
								return
							}

							for _, v := range memberTfArguments {
								handledTfArguments[v.Id] = true
							}

							// find the root's parameter
							sqlCmd = `SELECT * FROM parameter WHERE id=?`
							paramArgs = []interface{}{rootTfArgumentData.Parameter}
							var parameterList []*models.ParameterTable
							err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
							if err != nil {
								err = fmt.Errorf("Get Parameter data by id:%s error:%s", rootTfArgumentData.Parameter, err.Error())
								log.Logger.Error("Get parameter data by id error", log.String("id", rootTfArgumentData.Parameter), log.Error(err))
								return
							}
							if len(parameterList) == 0 {
								err = fmt.Errorf("Parameter data can not be found by id:%s", rootTfArgumentData.Parameter)
								log.Logger.Warn("Parameter data can not be found by id", log.String("id", rootTfArgumentData.Parameter), log.Error(err))
								return
							}
							parameterData := parameterList[0]

							tmpRootVal := convertedArgumentData[rootTfArgumentData.Name]
							tmpPVal := []interface{}{}
							/*
								p := reflect.ValueOf(tmpRootVal)
								for i := 0; i < p.Len(); i++ {
									tmpPVal = append(tmpPVal, p.Index(i).Interface())
								}
							*/
							if rootTfArgumentData.IsMulti == "N" {
								tmpPVal = append(tmpPVal, tmpRootVal)
							} else {
								tmpPVal = tmpRootVal.([]interface{})
							}

							convertedInPutVal := []interface{}{}
							for i := range tmpPVal {
								v := make(map[string]interface{})
								if parameterData.Multiple == "Y" {
									v[parameterData.Name] = []interface{}{tmpPVal[i]}
								} else {
									v[parameterData.Name] = tmpPVal[i]
								}

								var tmpTfArguments map[string]interface{}
								if _, ok := reqParam[models.ResourceDataDebug]; ok {
									v[models.ResourceDataDebug] = reqParam[models.ResourceDataDebug]
								}

								tmpTfArguments, _, err = handleConvertParams(action, sortedSourceData, memberTfArguments, v, providerData, regionData)

								if _, ok := reqParam[models.ResourceDataDebug]; ok {
									delete(v, models.ResourceDataDebug)
								}

								if err != nil {
									err = fmt.Errorf("HandleConvertParams error:%s", err.Error())
									log.Logger.Warn("HandleConvertParams error", log.Error(err))
									rowData["errorMessage"] = err.Error()
									return
								}
								convertedInPutVal = append(convertedInPutVal, tmpTfArguments)
							}
							inPutValSlice = append(inPutValSlice, convertedInPutVal)
						}
					} else if rootTfArgumentData.Parameter == "" {
						sqlCmd = "SELECT * FROM tf_argument WHERE source=? AND relative_source=? AND name!=?"
						var memberTfArguments []*models.TfArgumentTable
						paramArgs = []interface{}{sortedSourceData.Id, rootTfArgumentData.RelativeSource, "ROOT"}
						err = x.SQL(sqlCmd, paramArgs...).Find(&memberTfArguments)
						if err != nil {
							err = fmt.Errorf("Get memberTfArgument list error:%s", err.Error())
							log.Logger.Error("Get memberTfArgument list error", log.Error(err))
							rowData["errorMessage"] = err.Error()
							return
						}
						if len(memberTfArguments) == 0 {
							err = fmt.Errorf("MemberTfArgument list can not be found by source:%s and parameter:%s", sortedSourceData.Id, rootTfArgumentData.Parameter)
							log.Logger.Warn("MemberTfArgument list can not be found by source and parameter", log.String("source", sortedSourceData.Id), log.String("parameter", rootTfArgumentData.Parameter), log.Error(err))
							rowData["errorMessage"] = err.Error()
							return
						}

						for _, v := range memberTfArguments {
							handledTfArguments[v.Id] = true
						}

						reqParam[models.ResourceIdDataConvert] = resourceId
						convertedRootArgumentData, _, tmpErr := handleConvertParams(action, sortedSourceData, []*models.TfArgumentTable{rootTfArgumentData}, reqParam, providerData, regionData)
						delete(reqParam, models.ResourceIdDataConvert)
						if tmpErr != nil {
							err = fmt.Errorf("Handle convert params error:%s", err.Error())
							log.Logger.Error("Handle convert params error", log.Error(err))
							rowData["errorMessage"] = err.Error()
							return
						}

						tmpRootVal := convertedRootArgumentData[rootTfArgumentData.Name]
						tmpRootRes := []interface{}{}
						if rootTfArgumentData.IsMulti == "N" {
							tmpRootRes = append(tmpRootRes, tmpRootVal)
						} else {
							tmpRootRes = tmpRootVal.([]interface{})
						}

						// for i := range tmpRootRes {
						// }
						convertedInPutVal := []interface{}{}
						for i := 0; i < len(tmpRootRes); i++ {

							// v := make(map[string]interface{})
							// if parameterData.Multiple == "Y" {
							// 	v[parameterData.Name] = []interface{}{tmpPVal[i]}
							// } else {
							// 	v[parameterData.Name] = tmpPVal[i]
							// }

							tmpTfArguments := make(map[string]interface{})
							// if _, ok := reqParam[models.ResourceDataDebug]; ok {
							// 	v[models.ResourceDataDebug] = reqParam[models.ResourceDataDebug]
							// }

							// tmpTfArguments, _, err = handleConvertParams(action, sortedSourceData, memberTfArguments, reqParam, providerData, regionData)
							for j := range memberTfArguments {
								tmpTfArguments[memberTfArguments[j].Name] = tmpRootRes[i]
							}

							// if _, ok := reqParam[models.ResourceDataDebug]; ok {
							// 	delete(v, models.ResourceDataDebug)
							// }

							if err != nil {
								err = fmt.Errorf("HandleConvertParams error:%s", err.Error())
								log.Logger.Warn("HandleConvertParams error", log.Error(err))
								rowData["errorMessage"] = err.Error()
								return
							}
							convertedInPutVal = append(convertedInPutVal, tmpTfArguments)
						}
						inPutValSlice = append(inPutValSlice, convertedInPutVal)
					}
				}
				// Construct the object
				curObject := make(map[string]interface{})
				handleConStructObject(&conStructObject, inPutValSlice, curObject, 0)

				// handle remain tfArguments
				remainTfArguments := []*models.TfArgumentTable{}
				for _, v := range allTfArgumentList {
					if _, ok := handledTfArguments[v.Id]; !ok {
						remainTfArguments = append(remainTfArguments, v)
					}
				}

				var tmpTfArguments map[string]interface{}
				reqParam[models.ResourceIdDataConvert] = resourceId
				tmpTfArguments, _, err = handleConvertParams(action, sortedSourceData, remainTfArguments, reqParam, providerData, regionData)
				delete(reqParam, models.ResourceIdDataConvert)
				if err != nil {
					err = fmt.Errorf("HandleConvertParams error:%s", err.Error())
					log.Logger.Warn("HandleConvertParams error", log.Error(err))
					rowData["errorMessage"] = err.Error()
					return
				}

				// Add remain tfArgument to conStructObject
				for i := range conStructObject {
					for k, v := range tmpTfArguments {
						conStructObject[i][k] = v
					}
				}
			}

			// Finish to construct the converted parameters, and start to handle the whole process

			// Get the resource_data list by resource_id and source
			sqlCmd = `SELECT * FROM resource_data WHERE resource=? AND resource_id=? AND region_id=?`
			if _, ok := reqParam[models.ResourceDataDebug]; ok {
				sqlCmd = `SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=?`
			}
			paramArgs = []interface{}{sortedSourceData.Id, resourceId, regionData.RegionId}
			var resourceDataList []*models.ResourceDataTable
			err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
			if err != nil {
				err = fmt.Errorf("Get resource data by resource:%s and resource_id:%s error: %s", sortedSourceData.Id, resourceId, err.Error())
				log.Logger.Error("Get resource data by resource and resource_id error", log.String("resource", sortedSourceData.Id), log.String("resource_id", resourceId), log.Error(err))
				return
			}
			if len(resourceDataList) == 0 {
				err = fmt.Errorf("ResourceData can not be found by resource:%s and resource_id:%s", sortedSourceData.Id, resourceId)
				log.Logger.Warn("ResourceData can not be found by resource and resource_id", log.String("resource", sortedSourceData.Id), log.String("resource_id", resourceId), log.Error(err))
			}

			// Get tfArgument list by key_argument='Y'
			sqlCmd = `SELECT * FROM tf_argument WHERE source=? AND key_argument=?`
			paramArgs = []interface{}{sortedSourceData.Id, "Y"}
			var keyTfArgumentDataList []*models.TfArgumentTable
			err = x.SQL(sqlCmd, paramArgs...).Find(&keyTfArgumentDataList)
			if err != nil {
				err = fmt.Errorf("Get tfArgument data by resource:%s and key_argument:%s error: %s", sortedSourceData.Id, "Y", err.Error())
				log.Logger.Error("Get tfArgument data by resource and key_argument error", log.String("resource", sortedSourceData.Id), log.String("key_arugment", "Y"), log.Error(err))
				return
			}
			if len(keyTfArgumentDataList) == 0 {
				err = fmt.Errorf("TfArgument Data can not be found by resource:%s and key_argument:%s", sortedSourceData.Id, "Y")
				log.Logger.Warn("TfArgument Data can not be found by resource and key_argument", log.String("resource", sortedSourceData.Id), log.String("key_argument", "Y"), log.Error(err))
			}

			workDirPath := GenWorkDirPath(reqParam["id"].(string),
				reqParam["requestSn"].(string),
				reqParam["requestId"].(string),
				providerData,
				regionData,
				plugin,
				sortedSourceData)

			curWorkDirPath = append(curWorkDirPath, workDirPath)

			// Gen the terraform workdir
			err = GenDir(workDirPath)
			if err != nil {
				err = fmt.Errorf("Gen the terraform workdir: %s error: %s", workDirPath, err.Error())
				log.Logger.Error("Gen the terraform workdir error", log.String("workDirPath", workDirPath), log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			// Gen provider.tf.json
			err = GenProviderFile(workDirPath, providerData, providerInfoData, regionData)
			if err != nil {
				err = fmt.Errorf("Gen providerFile error: %s", err.Error())
				log.Logger.Error("Gen providerFile error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}
			defer DelProviderFile(workDirPath)

			// Gen version.tf
			err = GenVersionFile(workDirPath, providerData)
			if err != nil {
				err = fmt.Errorf("Gen versionFile error: %s", err.Error())
				log.Logger.Error("Gen versionFile error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			// Gen softlink of terraform provider file
			err = GenTerraformProviderSoftLink(workDirPath, providerData)
			if err != nil {
				err = fmt.Errorf("Gen terraform provider soft link error: %s", err.Error())
				log.Logger.Error("Gen terraform provider soft link error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			// Gen soft link for .terraform.lock.hcl
			err = GenTerraformLockHclSoftLink(workDirPath, providerData)
			if err != nil {
				err = fmt.Errorf("Gen terraform lock soft link error: %s", err.Error())
				log.Logger.Error("Gen terraform lock soft link error", log.Error(err))
				rowData["errorMessage"] = err.Error()
				return
			}

			newCreateObject := make(map[int]bool)
			importObject := make(map[int]string)
			importObjectResourceData := make(map[int]*models.ResourceDataTable)
			needToTakeAway := make(map[int]string)
			toDestroyResource := make(map[string]*models.ResourceDataTable)
			matchResourceData := make(map[string]bool)
			if action == "apply" {
				if len(keyTfArgumentDataList) > 0 {
					keyArgumentNameVal := make(map[string]interface{})
					for _, v := range keyTfArgumentDataList {
						keyArgumentNameVal[v.Name] = ""
					}

					for i := range conStructObject {
						curObject := conStructObject[i]
						for k, _ := range keyArgumentNameVal {
							keyArgumentNameVal[k] = curObject[k]
						}
						// 对比 datas 的 tf file，看是否都匹配
						for _, data := range resourceDataList {
							tmpTfFileArgument := make(map[string]map[string]map[string]map[string]interface{})
							tmpTfFileArgument["resource"] = make(map[string]map[string]map[string]interface{})
							tmpTfFileArgument["resource"][sortedSourceData.Name] = make(map[string]map[string]interface{})
							tmpTfFileArgument["resource"][sortedSourceData.Name][resourceId] = make(map[string]interface{})
							json.Unmarshal([]byte(data.TfFile), &tmpTfFileArgument)
							isMatch := true
							for k, v := range keyArgumentNameVal {
								if v != tmpTfFileArgument["resource"][sortedSourceData.Name][resourceId][k] {
									isMatch = false
									break
								}
							}
							if isMatch {
								// check if the item needed to be deleted because of the relatived id in toDestroyList
								isMatchAgain := true
								for _, v := range keyArgumentNameVal {
									isAllValid := true
									for j := range toDestroyList {
										if toDestroyList[j].ResourceAssetId == v {
											isAllValid = false
											break
										}
									}
									if isAllValid == false {
										isMatchAgain = false
										toDestroyResource[data.Id] = data
										needToTakeAway[i] = data.ResourceAssetId
										break
									}
								}
								if isMatchAgain {
									matchResourceData[data.Id] = true
									importObject[i] = data.ResourceAssetId
									importObjectResourceData[i] = data
								}
								break
							}
						}
					}
				} else {
					if len(resourceDataList) > 0 {
						matchResourceData[resourceDataList[0].Id] = true
						importObject[0] = resourceDataList[0].ResourceAssetId
						importObjectResourceData[0] = resourceDataList[0]
					}
				}

				for i := range conStructObject {
					if _, ok := importObject[i]; !ok {
						if _, okAgain := needToTakeAway[i]; !okAgain {
							newCreateObject[i] = true
						}
					}
				}
				for _, data := range resourceDataList {
					if _, ok := matchResourceData[data.Id]; !ok {
						// toDestroyResource[data.ResourceAssetId] = data
						toDestroyResource[data.Id] = data
					}
				}
			}

			// Recodr the debugFileContent
			curDebugFileStartIdx := len(*debugFileContent)
			for i := range conStructObject {
				curDebugFileContent := make(map[string]interface{})
				curDebugFileContent["tf_json_old"] = ""
				curDebugFileContent["tf_json_new"] = ""
				curDebugFileContent["tf_state_old"] = ""
				curDebugFileContent["tf_state_new"] = ""
				curDebugFileContent["tf_state_import"] = ""
				curDebugFileContent["plan_message"] = ""
				curDebugFileContent["source_name"] = sortedSourceData.Name
				*debugFileContent = append(*debugFileContent, curDebugFileContent)

				if _, ok := reqParam[models.ResourceDataDebug]; ok {
					curTfFileContentStr, err := GenTfFile(workDirPath, sortedSourceData, action, resourceId, conStructObject[i])
					if err != nil {
						err = fmt.Errorf("Gen tfFile error: %s", err.Error())
						log.Logger.Error("Gen tfFile error", log.Error(err))
						rowData["errorMessage"] = err.Error()
						continue
					}
					curDebugFileContent["tf_json_new"] = curTfFileContentStr

					if _, tmpOk := importObject[i]; tmpOk {
						// get tf_json_old and tf_state_old file content
						getOldTfFile(curDebugFileContent, regionData, sortedSourceData, resourceId, importObject[i])
					}
				}
			}
			if action == "apply" {
				if reqParam["confirmToken"] != "Y" {
					destroyAssetId := ""
					totalDestroyCnt := len(toDestroyResource)
					if len(toDestroyResource) > 0 {
						for _, resourceData := range toDestroyResource {
							destroyAssetId += resourceData.ResourceAssetId + ", "
						}
					}

					for i := range conStructObject {
						curDebugFileContent := (*debugFileContent)[curDebugFileStartIdx+i]
						// check if importObject needed to be destroy
						if _, ok := importObject[i]; ok || (sourceDataIdx == 0 && rootResourceAssetId != "" && rootResourceAssetId != nil) {
							// Gen tf.json file
							// uuid := "_" + guid.CreateGuid()
							_, err = GenTfFile(workDirPath, sortedSourceData, action, resourceId, conStructObject[i])
							if err != nil {
								err = fmt.Errorf("Gen tfFile error: %s", err.Error())
								log.Logger.Error("Gen tfFile error", log.Error(err))
								rowData["errorMessage"] = err.Error()
								continue
							}

							err = TerraformInit(workDirPath)
							if err != nil {
								err = fmt.Errorf("Do TerraformInit error:%s", err.Error())
								log.Logger.Error("Do TerraformInit error", log.Error(err))
								rowData["errorMessage"] = err.Error()
								// return
								continue
							}

							DelTfstateFile(workDirPath)
							if sortedSourceData.ImportSupport != "N" {
								if sourceDataIdx == 0 && rootResourceAssetId != "" && rootResourceAssetId != nil {
									err = TerraformImport(workDirPath, sortedSourceData.Name+"."+resourceId, rootResourceAssetId.(string))
								} else {
									err = TerraformImport(workDirPath, sortedSourceData.Name+"."+resourceId, importObject[i])
								}
								if err != nil {
									errMsg := err.Error()
									if strings.Contains(errMsg, "Cannot import non-existent remote object") == false {
										err = fmt.Errorf("Do TerraformImport error:%s", err.Error())
										rowData["errorMessage"] = err.Error()
										// return
										continue
									} else {
										// deleteOldResourceData(sortedSourceData, regionData, resourceId, importObject[i], reqParam)
									}
								} else if len(importObjectResourceData) > i {
									oldTfstateFile := importObjectResourceData[i].TfStateFile
									var oldTfstateFileObj models.TfstateFileData
									err = json.Unmarshal([]byte(oldTfstateFile), &oldTfstateFileObj)
									if err != nil {
										err = fmt.Errorf("Unmarshal tfstate file data error:%s", err.Error())
										log.Logger.Error("Unmarshal tfstate file data error", log.Error(err))
										return
									}

									secondFileObj := getFileAttrContent(workDirPath + "/terraform.tfstate")
									first, second := make(map[string]interface{}), make(map[string]interface{})
									first = oldTfstateFileObj.Resources[0].Instances[0].Attributes
									err = json.Unmarshal(secondFileObj.AttrBytes, &second)
									if err != nil {
										fmt.Printf("json unmarshal second file fail,%s \n", err.Error())
										return
									}

									result, diff, message := compareObject(first, second)
									if diff != 0 {
										err = fmt.Errorf("Compare import_state file and old tfstate file error:%s. Please confirm again!", message)
										log.Logger.Error("Compare import_state file and old tfstate file error", log.String("message", message), log.Error(err))
										rowData["errorMessage"] = err.Error()
										rowData["errorCode"] = "-1"
										return
									}
									resultBytes, tmpErr := json.MarshalIndent(result, "        ", "\t")
									if tmpErr != nil {
										err = fmt.Errorf("json marshal result fail,%s \n", tmpErr.Error())
										return
									}

									newFileBytes := []byte{}
									newFileWriter := bytes.NewBuffer(newFileBytes)
									newFileWriter.WriteString(secondFileObj.FileContent[:secondFileObj.StartIndex])
									newFileWriter.Write(resultBytes)
									newFileWriter.WriteString(secondFileObj.FileContent[secondFileObj.EndIndex:])
									ioutil.WriteFile(workDirPath+"/terraform.tfstate", newFileWriter.Bytes(), 0644)
								}
							} else {
								// get tfstate file from resource_data table and gen it
								tfstateFileContent := importObjectResourceData[i].TfStateFile
								tfstateFilePath := workDirPath + "/terraform.tfstate"
								GenFile([]byte(tfstateFileContent), tfstateFilePath)
							}
							if _, ok := reqParam[models.ResourceDataDebug]; ok {
								// get import tfstate file
								tfstateFilePath := workDirPath + "/terraform.tfstate"
								tfstateImportFileData, tmpErr := ReadFile(tfstateFilePath)
								if tmpErr != nil {
									err = fmt.Errorf("Read tfstate import file error:%s", tmpErr.Error())
									log.Logger.Error("Read tfstate import file error", log.Error(err))
									rowData["errorMessage"] = err.Error()
									// return
								}
								tfstateImportFileContentStr := string(tfstateImportFileData)
								curDebugFileContent["tf_state_import"] = tfstateImportFileContentStr
							}

							destroyCnt, tmpErr := TerraformPlan(workDirPath)
							if tmpErr != nil {
								err = fmt.Errorf("Do TerraformPlan error:%s", tmpErr.Error())
								log.Logger.Error("Do TerraformPlan error", log.Error(err))
								rowData["errorMessage"] = err.Error()
								// return
							}

							if destroyCnt > 0 {
								// 二次确认
								totalDestroyCnt += destroyCnt
								destroyAssetId += importObject[i] + ", "
							}

							if _, ok := reqParam[models.ResourceDataDebug]; ok {
								// get plan file
								planFilePath := workDirPath + "/planfile"
								planFileData, tmpErr := ReadFile(planFilePath)
								if tmpErr != nil {
									err = fmt.Errorf("Read tfstate import file error:%s", tmpErr.Error())
									log.Logger.Error("Read tfstate import file error", log.Error(err))
									rowData["errorMessage"] = err.Error()
									// return
								}
								planFileContentStr := string(planFileData)
								curDebugFileContent["plan_message"] = planFileContentStr
							}

							DelTfstateFile(workDirPath)
						}
					}
					// test
					// totalDestroyCnt = 1
					if totalDestroyCnt > 0 {
						destroyCntStr := strconv.Itoa(totalDestroyCnt)
						rowData["errorMessage"] = destroyCntStr + " resource(s) will be destroy: " + destroyAssetId + "please confirm again!"
						rowData["errorCode"] = "-1"
						return
					}
				}
			}

			// Do Terraform Action
			for i := range conStructObject {
				if _, ok := needToTakeAway[i]; ok {
					continue
				}
				curDebugFileContent := (*debugFileContent)[curDebugFileStartIdx+i]
				var tfFileContentStr string
				err = TerraformInit(workDirPath)
				if err != nil {
					err = fmt.Errorf("Do TerraformInit error:%s", err.Error())
					log.Logger.Error("Do TerraformInit error", log.Error(err))
					rowData["errorMessage"] = err.Error()
					return
				}
				if action == "apply" {
					if _, ok := importObject[i]; ok || (sourceDataIdx == 0 && rootResourceAssetId != "" && rootResourceAssetId != nil) {
						// Gen tf.json file
						// uuid := "_" + guid.CreateGuid()
						tfFileContentStr, err = GenTfFile(workDirPath, sortedSourceData, action, resourceId, conStructObject[i])
						if err != nil {
							err = fmt.Errorf("Gen tfFile error: %s", err.Error())
							log.Logger.Error("Gen tfFile error", log.Error(err))
							rowData["errorMessage"] = err.Error()
							// return
							continue
						}

						DelTfstateFile(workDirPath)
						if sortedSourceData.ImportSupport != "N" {
							if sourceDataIdx == 0 && rootResourceAssetId != "" && rootResourceAssetId != nil {
								err = TerraformImport(workDirPath, sortedSourceData.Name+"."+resourceId, rootResourceAssetId.(string))
							} else {
								err = TerraformImport(workDirPath, sortedSourceData.Name+"."+resourceId, importObject[i])
							}
							if err != nil {
								errMsg := err.Error()
								if strings.Contains(errMsg, "Cannot import non-existent remote object") == false {
									err = fmt.Errorf("Do TerraformImport error:%s", err.Error())
									rowData["errorMessage"] = err.Error()
									// return
								} else {
									deleteOldResourceData(sortedSourceData, regionData, resourceId, importObject[i], reqParam)
								}
							} else {
								// firstFileObj := getFileAttrContent(workDirPath + "/terraform.tfstate")
								// get the old tfstate file content
								if len(importObjectResourceData) > i {
									oldTfstateFile := importObjectResourceData[i].TfStateFile
									var oldTfstateFileObj models.TfstateFileData
									err = json.Unmarshal([]byte(oldTfstateFile), &oldTfstateFileObj)
									if err != nil {
										err = fmt.Errorf("Unmarshal tfstate file data error:%s", err.Error())
										log.Logger.Error("Unmarshal tfstate file data error", log.Error(err))
										return
									}

									secondFileObj := getFileAttrContent(workDirPath + "/terraform.tfstate")
									first, second := make(map[string]interface{}), make(map[string]interface{})
									first = oldTfstateFileObj.Resources[0].Instances[0].Attributes
									err = json.Unmarshal(secondFileObj.AttrBytes, &second)
									if err != nil {
										fmt.Printf("json unmarshal second file fail,%s \n", err.Error())
										return
									}

									result, _, _ := compareObject(first, second)
									resultBytes, tmpErr := json.MarshalIndent(result, "        ", "\t")
									if tmpErr != nil {
										err = fmt.Errorf("json marshal result fail,%s \n", tmpErr.Error())
										return
									}

									newFileBytes := []byte{}
									newFileWriter := bytes.NewBuffer(newFileBytes)
									newFileWriter.WriteString(secondFileObj.FileContent[:secondFileObj.StartIndex])
									newFileWriter.Write(resultBytes)
									newFileWriter.WriteString(secondFileObj.FileContent[secondFileObj.EndIndex:])
									ioutil.WriteFile(workDirPath+"/terraform.tfstate", newFileWriter.Bytes(), 0644)
								}
							}
						} else {
							// get tfstate file from resource_data table and gen it
							tfstateFileContent := importObjectResourceData[i].TfStateFile
							tfstateFilePath := workDirPath + "/terraform.tfstate"
							GenFile([]byte(tfstateFileContent), tfstateFilePath)
						}
						if _, ok := reqParam[models.ResourceDataDebug]; ok {
							// resource_data debug mode, get the terraform.state file after terraform import
							tfstateFilePath := workDirPath + "/terraform.tfstate"
							tfstateFileData, tmpErr := ReadFile(tfstateFilePath)
							if tmpErr != nil {
								err = fmt.Errorf("Read import_tfstate file error:%s", tmpErr.Error())
								log.Logger.Error("Read import_tfstate file error", log.Error(err))
								// rowData["errorMessage"] = err.Error()
								// return
							}
							tfstateFileContentStr := string(tfstateFileData)
							curDebugFileContent["tf_state_import"] = tfstateFileContentStr
							// DelTfstateFile(workDirPath)
						}
						if len(importObjectResourceData) > 0 {
							reqParam[models.ImportResourceDataTableId] = importObjectResourceData[i].Id
						}
					}
				}

				// Gen tf.json file
				tfFileContentStr, err = GenTfFile(workDirPath, sortedSourceData, action, resourceId, conStructObject[i])
				if err != nil {
					err = fmt.Errorf("Gen tfFile error: %s", err.Error())
					log.Logger.Error("Gen tfFile error", log.Error(err))
					rowData["errorMessage"] = err.Error()
					// return
					continue
				}

				if action == "apply" {
					destroyCnt, tmpErr := TerraformPlan(workDirPath)
					fmt.Printf("%v\n", destroyCnt)
					if tmpErr != nil {
						err = fmt.Errorf("Do TerraformPlan error:%s", tmpErr.Error())
						log.Logger.Error("Do TerraformPlan error", log.Error(err))
						rowData["errorMessage"] = err.Error()
						return
					}
					if _, ok := reqParam[models.ResourceDataDebug]; ok {
						// resource_data debug mode, get the plan file after terraform plan
						planFilePath := workDirPath + "/planfile"
						planFileData, tmpErr := ReadFile(planFilePath)
						if tmpErr != nil {
							err = fmt.Errorf("Read plan file error:%s", tmpErr.Error())
							log.Logger.Error("Read plan file error", log.Error(err))
							rowData["errorMessage"] = err.Error()
							// return
						}
						planFileContentStr := string(planFileData)
						curDebugFileContent["plan_message"] = planFileContentStr
					}
				}

				err = TerraformApply(workDirPath)
				if err != nil {
					err = fmt.Errorf("Do TerraformApply error:%s", err.Error())
					log.Logger.Error("Do TerraformApply error", log.Error(err))
					rowData["errorMessage"] = err.Error()
					return
					// continue
				}

				if _, ok := reqParam[models.ResourceDataDebug]; ok {
					tfstateFilePath := workDirPath + "/terraform.tfstate"
					tfstateFileData, err := ReadFile(tfstateFilePath)
					if err != nil {
						err = fmt.Errorf("Read tfstate file error:%s", err.Error())
						log.Logger.Error("Read tfstate file error", log.Error(err))
						//return
					}
					tfstateFileContentStr := string(tfstateFileData)
					curDebugFileContent["tf_state_new"] = tfstateFileContentStr
				}

				// handl tfstate file
				err = handleTfstateOutPut(sortedSourceData,
					interfaceData,
					reqParam,
					regionData,
					providerData,
					action,
					workDirPath,
					tfFileContentStr,
					resourceId,
					rowData,
					curDebugFileContent,
					isInternalAction)

				// *debugFileContent = append(*debugFileContent, curDebugFileContent)

				DelTfstateFile(workDirPath)

				if action == "query" {
					if sourceDataIdx != 0 {
						resourceDataResult := reqParam[models.SimulateResourceDataResult].(map[string][]map[string]interface{})
						rootResult := resourceDataResult[sortedSourceList[0].Id]
						curSourceRes := resourceDataResult[sortedSourceData.Id]
						rootIdx := -1
						for ix := range rootResult {
							flag := true
							for k, v := range conStructObject[i] {
								if rootResult[ix][k] != v {
									flag = false
									break
								}
							}
							if flag == true {
								rootIdx = ix
							}
						}
						if rootIdx != -1 {
							curRootResultOut := rootResult[rootIdx]["output"].(map[string]interface{})
							// fmt.Printf("%v", curRootResultOut)
							if len(curSourceRes) > 0 {
								for j := range curSourceRes {
									for k, v := range curSourceRes[j] {
										if _, ok := curRootResultOut[k]; !ok {
											if _, tmpOk := v.([]interface{}); tmpOk {
												var tmpV []interface{}
												tmpV = v.([]interface{})
												curRootResultOut[k] = tmpV
											} else {
												curRootResultOut[k] = []interface{}{v}
											}
										} else {
											if _, tmpOk := v.([]interface{}); tmpOk {
												var tmpV []interface{}
												tmpV = v.([]interface{})
												curRootResultOut[k] = append(curRootResultOut[k].([]interface{}), tmpV...)
											} else {
												curRootResultOut[k] = append(curRootResultOut[k].([]interface{}), v)
											}
										}
									}
								}
							}
						} else {
							// for aws query
							if providerData.Name == models.ProviderName["Aws"] {
								if _, ok := resourceDataResult[providerData.Name]; !ok {
									resourceDataResult[providerData.Name] = []map[string]interface{}{}
								}
								resourceDataResult[providerData.Name] = append(resourceDataResult[providerData.Name], curSourceRes...)
							}
						}
						resourceDataResult[sortedSourceData.Id] = []map[string]interface{}{}
					}
				}
			}
			if action == "apply" && len(toDestroyResource) > 0 {
				for k, v := range toDestroyResource {
					toDestroyList[k] = v
				}
			}

			DelProviderFile(workDirPath)
		}
		if action == "query" {
			if len(sortedSourceList) > 1 {
				curSimulateResourceData := reqParam[models.SimulateResourceDataResult].(map[string][]map[string]interface{})
				// rowData[models.TerraformOutPutPrefix] = curSimulateResourceData[sortedSourceList[0].Id]
				result := []interface{}{}
				if _, ok := curSimulateResourceData[providerData.Name]; !ok {
					curResult := curSimulateResourceData[sortedSourceList[0].Id]
					for i := range curResult {
						result = append(result, curResult[i]["output"])
					}
				} else {
					curResult := curSimulateResourceData[providerData.Name]
					for i := range curResult {
						result = append(result, curResult[i])
					}
				}
				rowData[models.TerraformOutPutPrefix] = result
			}
		}
		if action == "apply" && len(toDestroyList) > 0 {
			for i := len(sortedSourceList) - 1; i >= 0; i-- {
				// deletedResourceDataId := make(map[string]bool)
				for _, v := range toDestroyList {
					if v.Resource == sortedSourceList[i].Id {
						//deletedResourceDataId[v.Id] = true
						workDirPath := GenWorkDirPath(reqParam["id"].(string),
							reqParam["requestSn"].(string),
							reqParam["requestId"].(string),
							providerData,
							regionData,
							plugin,
							sortedSourceList[i])
						_, err = handleDestroy(workDirPath,
							sortedSourceList[i],
							providerData,
							providerInfoData,
							regionData,
							reqParam,
							plugin,
							v)
						if err != nil {
							err = fmt.Errorf("Handle Destroy error: %s", err.Error())
							log.Logger.Error("Handle Destroy error", log.Error(err))
							rowData["errorMessage"] = err.Error()
						}
					}
				}
			}
		}
		rowData["errorCode"] = "0"
	} else {
		sourceData := sourceList[0]

		workDirPath := GenWorkDirPath(reqParam["id"].(string),
			reqParam["requestSn"].(string),
			reqParam["requestId"].(string),
			providerData,
			regionData,
			plugin,
			sourceData)

		curDebugFileContent := make(map[string]interface{})
		curDebugFileContent["tf_json_old"] = ""
		curDebugFileContent["tf_json_new"] = ""
		curDebugFileContent["tf_state_old"] = ""
		curDebugFileContent["tf_state_new"] = ""
		curDebugFileContent["tf_state_import"] = ""
		curDebugFileContent["plan_message"] = ""
		curDebugFileContent["source_name"] = sourceData.Name
		if action == "apply" || action == "query" {
			var retOutput map[string]interface{}
			var tmpErr error
			if sourceData.TerraformUsed != "N" {
				// retOutput, tmpErr = handleTerraformApplyOrQuery(reqParam, sourceData, providerData, providerInfoData, regionData, action, plugin, workDirPath, interfaceData, curDebugFileContent)
			} else {
				retOutput, tmpErr = handleApplyOrQuery(action, reqParam, sourceData, regionData)
			}
			*debugFileContent = append(*debugFileContent, curDebugFileContent)
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
			rowData["id"] = reqParam["id"].(string)
			for i := len(sortedSourceList) - 1; i >= 0; i-- {
				workDirPath = GenWorkDirPath(reqParam["id"].(string),
					reqParam["requestSn"].(string),
					reqParam["requestId"].(string),
					providerData,
					regionData,
					plugin,
					sortedSourceList[i])
				curWorkDirPath = append(curWorkDirPath, workDirPath)
				retOutput, tmpErr := handleDestroy(workDirPath, sortedSourceList[i], providerData, providerInfoData, regionData, reqParam, plugin, nil)

				if _, ok := retOutput["errorCode"]; ok {
					if retOutput["errorCode"] == "1" {
						err = fmt.Errorf("Handle Destroy error: %s", tmpErr.Error())
						log.Logger.Error("Handle Destroy error", log.Error(err))
						rowData["errorMessage"] = err.Error()
						return
					}
				}

				/*
				if tmpErr != nil {
					err = fmt.Errorf("Handle Destroy error: %s", tmpErr.Error())
					log.Logger.Error("Handle Destroy error", log.Error(err))
					rowData["errorMessage"] = err.Error()
					continue
				}
				 */

				/*
				for k, v := range retOutput {
					rowData[k] = v
				}
				 */
				// rowData["id"] = reqParam["id"].(string)
			}
			rowData["errorCode"] = "0"
		} else {
			err = fmt.Errorf("Action: %s is inValid", action)
			log.Logger.Error("Action is inValid", log.String("action", action), log.Error(err))
			rowData["errorMessage"] = err.Error()
		}
	}
	return
}

func convertData(relativeSourceId string, reqParam map[string]interface{}, regionData *models.ResourceDataTable, tfArgument *models.TfArgumentTable, sourceData *models.SourceTable) (arg interface{}, err error) {
	if tfArgument.Parameter == "" {
		if sourceData.SourceType == "data_resource" {
			if _, ok := reqParam[models.SimulateResourceData]; ok {
				curSimulateResourceData := reqParam[models.SimulateResourceData].(map[string][]map[string]interface{})

				tmpRes := []interface{}{}
				resourceDatas := curSimulateResourceData[relativeSourceId]
				for i := range resourceDatas {
					tmpData := resourceDatas[i]["tfstateFile"].(map[string]interface{})
					assetIdAttribute := resourceDatas[i]["assetIdAttribute"].(string)
					if _, ok := tmpData[assetIdAttribute]; ok {
						tmpRes = append(tmpRes, tmpData[assetIdAttribute])
					}
				}
				if len(tmpRes) > 0 {
					if tfArgument.IsMulti == "Y" {
						arg = tmpRes
					} else {
						arg = tmpRes[0]
					}
				}
				return
			}
		}
		// get data from resource_data
		// curTfArgRelativeSource := remainTfArguments[i].RelativeSource
		sqlCmd := `SELECT * FROM resource_data WHERE resource=? AND resource_id=? AND region_id=?`

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			sqlCmd = `SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=?`
		}
		// resourceId: 来源 param 先判断
		resourceId := reqParam[models.ResourceIdDataConvert].(string)
		paramArgs := []interface{}{relativeSourceId, resourceId, regionData.RegionId}
		var resourceDataList []*models.ResourceDataTable
		err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
		if err != nil {
			err = fmt.Errorf("Get resource data by resource:%s and resource_id:%s error: %s", relativeSourceId, resourceId, err.Error())
			log.Logger.Error("Get resource data by resource and resource_id error", log.String("resource", relativeSourceId), log.String("resource_id", resourceId), log.Error(err))
			return
		}
		if len(resourceDataList) == 0 {
			err = fmt.Errorf("ResourceData can not be found by resource:%s and resource_id:%s", relativeSourceId, resourceId)
			log.Logger.Warn("ResourceData can not be found by resource and resource_id", log.String("resource", relativeSourceId), log.String("resource_id", resourceId), log.Error(err))
			// return
		}
		// arg = resourceDataList[0].ResourceAssetId
		/*
			tmpRes := []string{}
			for i := range resourceDataList {
				tmpRes = append(tmpRes, resourceDataList[i].ResourceAssetId)
			}
			arg = tmpRes

		*/
		if tfArgument.IsMulti == "Y" {
			tmpRes := []interface{}{}
			for i := range resourceDataList {
				tmpRes = append(tmpRes, resourceDataList[i].ResourceAssetId)
			}
			arg = tmpRes
		} else {
			arg = resourceDataList[0].ResourceAssetId
		}
		return
	}

	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgument.Parameter}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgument.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgument.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	if _, ok := reqParam[parameterData.Name]; !ok {
		return
	}
	if reqParam[parameterData.Name] == nil {
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
	sqlCmd = "SELECT * FROM resource_data WHERE resource=? AND region_id=? AND resource_id IN ('" + resourceIdsStr + "')"

	if _, ok := reqParam[models.ResourceDataDebug]; ok {
		sqlCmd = "SELECT * FROM resource_data_debug WHERE resource=? AND region_id=? AND resource_id IN ('" + resourceIdsStr + "')"
	}
	var resourceDataList []*models.ResourceDataTable
	paramArgs = []interface{}{relativeSourceId, regionData.RegionId}
	err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
	if err != nil {
		err = fmt.Errorf("Get resource data by resource:%s and resource_id:%s error: %s", relativeSourceId, resourceIdsStr, err.Error())
		log.Logger.Error("Get resource data by resource and resource_id error", log.String("resource", relativeSourceId), log.String("resource_id", resourceIdsStr), log.Error(err))
		return
	}
	if len(resourceDataList) == 0 {
		/*
			err = fmt.Errorf("Resource_data can not be found by resource:%s and resource_id:%s", relativeSourceId, resourceIdsStr)
			log.Logger.Warn("Resource_data can not be found by resource and resource_id", log.String("resource", relativeSourceId), log.String("resource_id", resourceIdsStr), log.Error(err))
		*/
		err = nil
		return
	}

	if tfArgument.IsMulti == "Y" {
		tmpRes := []interface{}{}
		for i := range resourceDataList {
			tmpRes = append(tmpRes, resourceDataList[i].ResourceAssetId)
		}
		arg = tmpRes
	} else {
		arg = resourceDataList[0].ResourceAssetId
	}
	return
}

func reverseConvertData(parameterData *models.ParameterTable, tfstateAttributeData *models.TfstateAttributeTable, tfstateVal interface{}, reqParam map[string]interface{}, regionData *models.ResourceDataTable) (argKey string, argVal interface{}, err error) {
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
	sqlCmd := "SELECT * FROM resource_data WHERE resource=? AND region_id=? AND resource_asset_id IN ('" + resourceAssetIdsStr + "')"

	if _, ok := reqParam[models.ResourceDataDebug]; ok {
		sqlCmd = "SELECT * FROM resource_data_debug WHERE resource=? AND region_id=? AND resource_asset_id IN ('" + resourceAssetIdsStr + "')"
	}

	paramArgs := []interface{}{relativeSourceId, regionData.RegionId}
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

	if parameterData.Multiple == "Y" {
		tmpRes := []interface{}{}
		for i := range resourceDataList {
			tmpRes = append(tmpRes, resourceDataList[i].ResourceId)
		}
		argVal = tmpRes
	} else {
		argVal = resourceDataList[0].ResourceId
	}
	return
}

func convertTemplate(providerData *models.ProviderTable, reqParam map[string]interface{}, tfArgument *models.TfArgumentTable) (arg interface{}, err error) {
	if tfArgument.Parameter == "" {
		arg = tfArgument.DefaultValue
		return
	}
	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgument.Parameter}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgument.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgument.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	if reqParam[parameterData.Name] == nil {
		return
	}

	sqlCmd = `SELECT * FROM template_value WHERE template=? AND value=?`
	templateId := parameterData.Template
	paramVal := reqParam[parameterData.Name].(string)
	paramArgs = []interface{}{templateId, paramVal}
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

func convertAttr(tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}, regionData *models.ResourceDataTable, tfArgument *models.TfArgumentTable, sourceData *models.SourceTable) (arg interface{}, err error) {
	if tfArgument.Parameter == "" {
		// arg = tfArgument.DefaultValue
		if sourceData.SourceType == "data_resource" {
			if _, ok := reqParam[models.SimulateResourceData]; ok {
				curSimulateResourceData := reqParam[models.SimulateResourceData].(map[string][]map[string]interface{})

				tmpRes := []interface{}{}
				relativeSourceId := tfArgumentData.RelativeSource
				resourceDatas := curSimulateResourceData[relativeSourceId]
				for i := range resourceDatas {
					tmpData := resourceDatas[i]["tfstateFile"].(map[string]interface{})
					assetIdAttribute := resourceDatas[i]["assetIdAttribute"].(string)
					if _, ok := tmpData[assetIdAttribute]; ok {
						if _, okAgain := tmpData[assetIdAttribute].([]interface{}); okAgain {
							tmpRes = append(tmpRes, tmpData[assetIdAttribute].([]interface{})...)
						} else {
							tmpRes = append(tmpRes, tmpData[assetIdAttribute])
						}
					}
				}
				if len(tmpRes) > 0 {
					if tfArgument.IsMulti == "Y" {
						arg = tmpRes
					} else {
						arg = tmpRes[0]
					}
				}
				return
			}
		}

		// get data from resource_data
		sqlCmd := `SELECT * FROM resource_data WHERE resource=? AND resource_id=? AND region_id=?`

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			sqlCmd = `SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=?`
		}
		// resourceId: 来源 param 先判断
		relativeSourceId := tfArgumentData.RelativeSource
		resourceId := reqParam[models.ResourceIdDataConvert].(string)
		paramArgs := []interface{}{relativeSourceId, resourceId, regionData.RegionId}
		var resourceDataList []*models.ResourceDataTable
		err = x.SQL(sqlCmd, paramArgs...).Find(&resourceDataList)
		if err != nil {
			err = fmt.Errorf("Get resource data by resource:%s and resource_id:%s error: %s", relativeSourceId, resourceId, err.Error())
			log.Logger.Error("Get resource data by resource and resource_id error", log.String("resource", relativeSourceId), log.String("resource_id", resourceId), log.Error(err))
			return
		}
		if len(resourceDataList) == 0 {
			err = fmt.Errorf("ResourceData can not be found by resource:%s and resource_id:%s", relativeSourceId, resourceId)
			log.Logger.Warn("ResourceData can not be found by resource and resource_id", log.String("resource", relativeSourceId), log.String("resource_id", resourceId), log.Error(err))
			return
		}
		resourceData := resourceDataList[0]

		sqlCmd = `SELECT * FROM tfstate_attribute WHERE id=?`
		paramArgs = []interface{}{tfArgumentData.RelativeTfstateAttribute}
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
		arg = tfstateFileAttributes[tfstateAttirbuteData.Name]
		/*
			if tfArgument.IsMulti == "Y" {
				tmpRes := []interface{}{}
				for i := range resourceDataList {
					tmpRes = append(tmpRes, resourceDataList[i].ResourceAssetId)
				}
				arg = tmpRes
			} else {
				arg = resourceDataList[0].ResourceAssetId
			}

		*/
		return
	}
	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgument.Parameter}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgument.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgument.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	if reqParam[parameterData.Name] == nil {
		return
	}

	relativeResourceIds := []string{}
	if parameterData.Multiple == "Y" {
		tmpData := reqParam[parameterData.Name].([]interface{})
		for i := range tmpData {
			relativeResourceIds = append(relativeResourceIds, tmpData[i].(string))
		}
	} else {
		relativeResourceIds = append(relativeResourceIds, reqParam[parameterData.Name].(string))
	}

	sqlCmd = `SELECT * FROM tfstate_attribute WHERE id=?`
	paramArgs = []interface{}{tfArgumentData.RelativeTfstateAttribute}
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
		sqlCmd := `SELECT * FROM resource_data WHERE resource=? AND resource_id=? AND region_id=?`

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			sqlCmd = `SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=?`
		}

		paramArgs := []interface{}{tfArgumentData.RelativeSource, relativeResourceIds[i], regionData.RegionId}
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

	if tfArgumentData.IsMulti == "Y" {
		tmpRes := []interface{}{}
		for i := range result {
			tmpRes = append(tmpRes, result[i])
		}
		arg = tmpRes
	} else {
		arg = result[0]
	}
	return
}

func reverseConvertAttr(parameterData *models.ParameterTable, tfstateAttributeData *models.TfstateAttributeTable, tfstateVal interface{}, reqParam map[string]interface{}, regionData *models.ResourceDataTable) (argKey string, argVal interface{}, err error) {
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
	sqlCmd = `SELECT * FROM resource_data WHERE resource=? AND region_id=?`

	if _, ok := reqParam[models.ResourceDataDebug]; ok {
		sqlCmd = `SELECT * FROM resource_data_debug WHERE resource=? AND region_id=?`
	}

	paramArgs = []interface{}{tfstateAttributeData.RelativeSource, regionData.RegionId}
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
	if parameterData.Multiple == "Y" {
		tmpRes := []interface{}{}
		for i := range result {
			tmpRes = append(tmpRes, result[i].(string))
		}
		argVal = tmpRes
	} else {
		argVal = result[0]
	}
	return
}

func convertContextData(tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}, regionData *models.ResourceDataTable, tfArgument *models.TfArgumentTable, sourceData *models.SourceTable) (arg interface{}, isDiscard bool, err error) {
	if tfArgument.Parameter == "" {
		arg = tfArgument.DefaultValue
		return
	}
	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgument.Parameter}
	var tmpparameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&tmpparameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgument.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	if len(tmpparameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgument.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	// parameterData := tmpparameterList[0]
	isDiscard = false

	// Get relative parameter
	sqlCmd = `SELECT * FROM parameter WHERE id=?`
	relativeParameterId := tfArgumentData.RelativeParameter
	paramArgs = []interface{}{relativeParameterId}
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

	if reqParam[relativeParameterData.Name] == nil {
		return
	}

	if reqParam[relativeParameterData.Name].(string) == tfArgumentData.RelativeParameterValue {
		arg, err = convertData(tfArgumentData.RelativeSource, reqParam, regionData, tfArgument, sourceData)
	} else {
		isDiscard = true
	}
	return
}

func reverseConvertContextData(parameterData *models.ParameterTable,
	tfstateAttributeData *models.TfstateAttributeTable,
	tfstateVal interface{},
	outPutArgs map[string]interface{},
	reqParam map[string]interface{},
	regionData *models.ResourceDataTable) (argKey string, argVal interface{}, isDiscard bool, err error) {

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
		argKey, argVal, err = reverseConvertData(parameterData, tfstateAttributeData, tfstateVal, reqParam, regionData)
	} else {
		isDiscard = true
	}
	return
}

func convertContextDirect(tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}, regionData *models.ResourceDataTable) (arg interface{}, isDiscard bool, err error) {
	if tfArgumentData.Parameter == "" {
		arg = tfArgumentData.DefaultValue
		return
	}
	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgumentData.Parameter}
	var tmpparameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&tmpparameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgumentData.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgumentData.Parameter), log.Error(err))
		return
	}
	if len(tmpparameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgumentData.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgumentData.Parameter), log.Error(err))
		return
	}
	// parameterData := tmpparameterList[0]
	isDiscard = false

	// Get relative parameter
	sqlCmd = `SELECT * FROM parameter WHERE id=?`
	relativeParameterId := tfArgumentData.RelativeParameter
	paramArgs = []interface{}{relativeParameterId}
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
	if reqParam[relativeParameterData.Name] == nil {
		return
	}
	if reqParam[relativeParameterData.Name].(string) == tfArgumentData.RelativeParameterValue {
		arg, err = convertDirect(tfArgumentData.DefaultValue, reqParam, tfArgumentData)
	} else {
		isDiscard = true
	}
	return
}

func reverseConvertContextDirect(parameterData *models.ParameterTable,
	tfstateAttributeData *models.TfstateAttributeTable,
	tfstateVal interface{},
	outPutArgs map[string]interface{},
	reqParam map[string]interface{},
	regionData *models.ResourceDataTable) (argKey string, argVal interface{}, isDiscard bool, err error) {

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
		argKey, argVal, err = reverseConvertDirect(parameterData, tfstateAttributeData, tfstateVal)
	} else {
		isDiscard = true
	}
	return
}

func convertContextAttr(tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}, regionData *models.ResourceDataTable, sourceData *models.SourceTable) (arg interface{}, isDiscard bool, err error) {
	if tfArgumentData.Parameter == "" {
		arg = tfArgumentData.DefaultValue
		return
	}
	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgumentData.Parameter}
	var tmpparameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&tmpparameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgumentData.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgumentData.Parameter), log.Error(err))
		return
	}
	if len(tmpparameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgumentData.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgumentData.Parameter), log.Error(err))
		return
	}
	// parameterData := tmpparameterList[0]
	isDiscard = false

	// Get relative parameter
	sqlCmd = `SELECT * FROM parameter WHERE id=?`
	relativeParameterId := tfArgumentData.RelativeParameter
	paramArgs = []interface{}{relativeParameterId}
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
	if reqParam[relativeParameterData.Name] == nil {
		return
	}
	if reqParam[relativeParameterData.Name].(string) == tfArgumentData.RelativeParameterValue {
		arg, err = convertAttr(tfArgumentData, reqParam, regionData, tfArgumentData, sourceData)
	} else {
		isDiscard = true
	}
	return
}

func reverseConvertContextAttr(parameterData *models.ParameterTable,
	tfstateAttributeData *models.TfstateAttributeTable,
	tfstateVal interface{},
	outPutArgs map[string]interface{},
	reqParam map[string]interface{},
	regionData *models.ResourceDataTable) (argKey string, argVal interface{}, isDiscard bool, err error) {

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
		argKey, argVal, err = reverseConvertAttr(parameterData, tfstateAttributeData, tfstateVal, reqParam, regionData)
	} else {
		isDiscard = true
	}
	return
}

func convertContextTemplate(tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}, regionData *models.ResourceDataTable, providerData *models.ProviderTable) (arg interface{}, isDiscard bool, err error) {
	if tfArgumentData.Parameter == "" {
		arg = tfArgumentData.DefaultValue
		return
	}
	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgumentData.Parameter}
	var tmpparameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&tmpparameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgumentData.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgumentData.Parameter), log.Error(err))
		return
	}
	if len(tmpparameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgumentData.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgumentData.Parameter), log.Error(err))
		return
	}
	// parameterData := tmpparameterList[0]
	isDiscard = false

	// Get relative parameter
	sqlCmd = `SELECT * FROM parameter WHERE id=?`
	relativeParameterId := tfArgumentData.RelativeParameter
	paramArgs = []interface{}{relativeParameterId}
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
	if reqParam[relativeParameterData.Name] == nil {
		return
	}
	if reqParam[relativeParameterData.Name].(string) == tfArgumentData.RelativeParameterValue {
		arg, err = convertTemplate(providerData, reqParam, tfArgumentData)
	} else {
		isDiscard = true
	}
	return
}

func reverseConvertContextTemplate(parameterData *models.ParameterTable,
	tfstateAttributeData *models.TfstateAttributeTable,
	tfstateVal interface{},
	outPutArgs map[string]interface{},
	reqParam map[string]interface{},
	regionData *models.ResourceDataTable,
	providerData *models.ProviderTable) (argKey string, argVal interface{}, isDiscard bool, err error) {

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
		argKey, argVal, err = reverseConvertTemplate(parameterData, providerData, tfstateVal)
	} else {
		isDiscard = true
	}
	return
}

func convertDirect(defaultValue string, reqParam map[string]interface{}, tfArgument *models.TfArgumentTable) (arg interface{}, err error) {
	if tfArgument.Parameter == "" {
		arg = tfArgument.DefaultValue
		return
	}
	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgument.Parameter}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgument.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgument.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	parameterData := parameterList[0]

	var reqArg interface{}
	if _, ok := reqParam[parameterData.Name]; !ok {
		return
	} else if reqParam[parameterData.Name] == nil {
		reqArg = tfArgument.DefaultValue
	} else {
		reqArg = reqParam[parameterData.Name]
	}

	if parameterData.DataType == "object" {
		if parameterData.Multiple == "N" {
			var curArg map[string]interface{}
			tmpMarshal, _ := json.Marshal(reqParam[parameterData.Name])
			json.Unmarshal(tmpMarshal, &curArg)

			if tfArgument.IsMulti == "N" {
				arg = curArg
			} else {
				arg = []map[string]interface{}{curArg}
			}
		} else {
			var curArg []map[string]interface{}
			tmpMarshal, _ := json.Marshal(reqParam[parameterData.Name])
			json.Unmarshal(tmpMarshal, &curArg)
			if tfArgument.IsMulti == "Y" {
				arg = curArg
			} else {
				arg = curArg[0]
			}
		}
	} else {
		// arg = reqParam[parameterData.Name]
		if parameterData.Multiple == "N" {
			tmpInputArg := reqArg
			if tfArgument.IsMulti == "Y" {
				arg = []interface{}{tmpInputArg}
			} else {
				arg = tmpInputArg
			}
		} else {
			tmpInputArg := reqArg.([]interface{})
			if tfArgument.IsMulti == "Y" {
				arg = tmpInputArg
			} else {
				arg = tmpInputArg[0]
			}
		}
	}

	if parameterData.Sensitive == "Y" {
		if _, tmpOk := reqParam["seed"]; !tmpOk {
			err = fmt.Errorf("Parameter data: seed can not be found ")
			return
		} else if reqParam["seed"].(string) == "" {
			err = fmt.Errorf("Parameter data: seed can not be empty ")
			return
		}

		if _, ok := arg.(string); ok {
			if strings.HasPrefix(arg.(string),"{cipher_a}") {
				arg, err = cipher.AesDePasswordByGuid(reqParam["id"].(string), reqParam["seed"].(string), arg.(string))
				return
			}
		}
	}

	if tfArgument.DefaultValue == models.RandomFlag && (arg == nil || arg == "") {
		randomVal := guid.CreateGuid()
		arg = randomVal[:16]
		reqParam[parameterData.Name] = arg
	} else {
		if _, ok := arg.(string); ok && arg.(string) == models.RandomFlag {
			randomVal := guid.CreateGuid()
			arg = randomVal[:16]
			reqParam[parameterData.Name] = arg
		}
	}

	return
}

func convertFunction(tfArgumentData *models.TfArgumentTable, reqParam map[string]interface{}, tfArgument *models.TfArgumentTable) (arg interface{}, err error) {
	if tfArgument.Parameter == "" {
		arg = tfArgument.DefaultValue
		return
	}
	// 查询 tfArgument 对应的 parameter
	sqlCmd := `SELECT * FROM parameter WHERE id=?`
	paramArgs := []interface{}{tfArgument.Parameter}
	var parameterList []*models.ParameterTable
	err = x.SQL(sqlCmd, paramArgs...).Find(&parameterList)
	if err != nil {
		err = fmt.Errorf("Get Parameter data by id:%s error:%s", tfArgument.Parameter, err.Error())
		log.Logger.Error("Get parameter data by id error", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	if len(parameterList) == 0 {
		err = fmt.Errorf("Parameter data can not be found by id:%s", tfArgument.Parameter)
		log.Logger.Warn("Parameter data can not be found by id", log.String("id", tfArgument.Parameter), log.Error(err))
		return
	}
	parameterData := parameterList[0]
	if reqParam[parameterData.Name] == nil {
		return
	}

	functionDefine := tfArgumentData.FunctionDefine
	var functionDefineData models.FunctionDefine
	json.Unmarshal([]byte(functionDefine), &functionDefineData)

	resultIdx := -1
	if functionDefineData.Return != "result" {
		idxStrStart := strings.Index(functionDefineData.Return, "[")
		idxStrEnd := strings.Index(functionDefineData.Return, "]")
		if idxStrStart == -1 || idxStrEnd == -1 || idxStrStart >= idxStrEnd {
			err = fmt.Errorf("The function_define return_value: %s of tfArgument:%s config error", functionDefineData.Return, tfArgumentData.Name)
			log.Logger.Error("The function_define return_value of tfArgument config error", log.String("return_value", functionDefineData.Return), log.String("tfArgument", tfArgumentData.Name), log.Error(err))
			return
		}
		resultIdx, _ = strconv.Atoi(functionDefineData.Return[idxStrStart+1 : idxStrEnd])
	}
	reqVal := reqParam[parameterData.Name]
	var result []interface{}
	if parameterData.DataType == "object" {
		handleReqVals := []map[string]interface{}{}
		if parameterData.Multiple == "Y" {
			tmpData := reqVal.([]map[string]interface{})
			for i := range tmpData {
				handleReqVals = append(handleReqVals, tmpData[i])
			}
		} else {
			handleReqVals = append(handleReqVals, reqVal.(map[string]interface{}))
		}

		if functionDefineData.Function == models.FunctionConvertFunctionDefineName["Remove"] {
			for _, val := range handleReqVals {
				removeResult := []map[string]string{}
				removeKeys := functionDefineData.Args.RemoveKey
				for i := range removeKeys {
					tmpVal := make(map[string]string)
					for k, v := range val {
						tmpVal[k] = v.(string)
					}
					delete(tmpVal, removeKeys[i])
					removeResult = append(removeResult, tmpVal)
				}
				result = append(result, removeResult[0])
			}
		}
	} else {
		handleReqVals := []string{}
		if parameterData.Multiple == "Y" {
			tmpData := reqVal.([]interface{})
			for i := range tmpData {
				handleReqVals = append(handleReqVals, tmpData[i].(string))
			}
		} else {
			handleReqVals = append(handleReqVals, reqVal.(string))
		}
		if functionDefineData.Function == models.FunctionConvertFunctionDefineName["Split"] {
			for _, reqValStr := range handleReqVals {
				splitResult := [][]string{}
				splitChars := functionDefineData.Args.SplitChar
				for i := range splitChars {
					curResult := strings.Split(reqValStr, splitChars[i])
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
			for _, reqValStr := range handleReqVals {
				replaceResult := []string{}
				replaceVals := functionDefineData.Args.ReplaceVal
				for i := range replaceVals {
					for old, new := range replaceVals[i] {
						curResult := strings.Replace(reqValStr, old, new, -1)
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
			for _, reqValStr := range handleReqVals {
				regxResult := [][]string{}
				regExprs := functionDefineData.Args.RegExp
				for i := range regExprs {
					regExp := regexp.MustCompile(regExprs[i])
					curResult := regExp.FindStringSubmatch(reqValStr)
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
			err = fmt.Errorf("The function_define:%s of tfArgument:%s config error", functionDefine, tfArgumentData.Name)
			log.Logger.Error("The function_define of tfArgument config error", log.String("function_define", functionDefine), log.String("tfstateAttribute", tfArgumentData.Name), log.Error(err))
			return
		}
	}
	if tfArgumentData.IsMulti == "Y" {
		tmpRes := []interface{}{}
		for i := range result {
			tmpRes = append(tmpRes, result[i])
		}
		arg = tmpRes
	} else {
		arg = result[0]
	}
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

	var result []interface{}
	if tfstateAttributeData.Type == "object" {
		handleTfstateVals := []map[string]interface{}{}
		if tfstateAttributeData.IsMulti == "Y" {
			tmpData := tfstateVal.([]map[string]interface{})
			for i := range tmpData {
				handleTfstateVals = append(handleTfstateVals, tmpData[i])
			}
		} else {
			handleTfstateVals = append(handleTfstateVals, tfstateVal.(map[string]interface{}))
		}

		if functionDefineData.Function == models.FunctionConvertFunctionDefineName["Remove"] {
			for _, val := range handleTfstateVals {
				removeResult := []map[string]string{}
				removeKeys := functionDefineData.Args.RemoveKey
				for i := range removeKeys {
					tmpVal := make(map[string]string)
					for k, v := range val {
						tmpVal[k] = v.(string)
					}
					delete(tmpVal, removeKeys[i])
					removeResult = append(removeResult, tmpVal)
				}
				result = append(result, removeResult[0])
			}
		}
	} else {
		handleTfstateVals := []string{}
		if tfstateAttributeData.IsMulti == "Y" {
			tmpData := tfstateVal.([]interface{})
			for i := range tmpData {
				handleTfstateVals = append(handleTfstateVals, tmpData[i].(string))
			}
		} else {
			handleTfstateVals = append(handleTfstateVals, tfstateVal.(string))
		}
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
	}
	argKey = parameterData.Name
	if parameterData.Multiple == "Y" {
		tmpRes := []interface{}{}
		for i := range result {
			tmpRes = append(tmpRes, result[i])
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
	/*
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
	*/
	var result []interface{}
	if tfstateAttributeData.IsMulti == "Y" {
		result = tfstateVal.([]interface{})
	} else {
		result = append(result, tfstateVal)
	}

	if parameterData.Multiple == "Y" {
		tmpRes := []interface{}{}
		for i := range result {
			tmpRes = append(tmpRes, result[i])
		}
		argVal = tmpRes
	} else {
		argVal = result[0]
	}

	//if tfstateAttributeData.ObjectName != "" {
	//	relativeTfstateAttr := tfstateAttrIdMap[tfstateAttributeData.ObjectName]
	//	if relativeTfstateAttr.Type == "object" {
	//		argVal = tfstateFileAttributes[argKey]
	//	}
	//}
	return
}

func handleReverseConvert(outPutParameterNameMap map[string]*models.ParameterTable,
	outPutParameterIdMap map[string]*models.ParameterTable,
	tfstateAttrParamMap map[string]*models.TfstateAttributeTable,
	tfstateAttrNameMap map[string]*models.TfstateAttributeTable,
	tfstateAttrIdMap map[string]*models.TfstateAttributeTable,
	reqParam map[string]interface{},
	providerData *models.ProviderTable,
	tfstateFileAttributes map[string]interface{},
	action string,
	parentObjectName string,
	tfstateAttributeList []*models.TfstateAttributeTable,
	paramCnt *int,
	regionData *models.ResourceDataTable) (outPutArgs map[string]interface{}, err error) {

	var errorTfstateAttr *models.TfstateAttributeTable
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("HandleReverseConvert error, TfstateAttr:%s convert error:%v", errorTfstateAttr.Name, r)
		}
	}()

	outPutArgs = make(map[string]interface{})
	curLevelResult := make(map[string]interface{})

	// 循环遍历每个 tfstateAttribute 进行 reverseConvert 生成输出参数
	for _, tfstateAttr := range tfstateAttributeList {
		errorTfstateAttr = tfstateAttr
		if tfstateAttr.ObjectName == parentObjectName {
			// handle current level tfstateAttribute
			// if tfstateAttr.Type == "object" && tfstateAttr.Name != "tags" {
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
						tfstateAttrIdMap,
						reqParam,
						providerData,
						tmpCurTfstateFileAttributes,
						action,
						tfstateAttr.Id,
						tfstateAttributeList,
						paramCnt,
						regionData)
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
				if tfstateAttr.Parameter == "" || tfstateAttr.Name == "tags" {
					*paramCnt += 1
					outPutArgs[models.TerraformOutPutPrefix+strconv.Itoa(*paramCnt)] = curAttributesRet
				} else {
					outPutArgs[outPutParameterIdMap[tfstateAttr.Parameter].Name] = curAttributesRet
				}

				if tfstateAttr.Name != "tags" {
					continue
				}
			} /*else {*/
			curParamData := outPutParameterIdMap[tfstateAttr.Parameter]
			if curParamData == nil {
				continue
			}
			if tfstateOutParamVal, ok := tfstateFileAttributes[tfstateAttr.Name]; ok {
				convertWay := tfstateAttr.ConvertWay
				var outArgKey string
				var outArgVal interface{}
				var isDiscard = false
				switch convertWay {
				case models.ConvertWay["Data"]:
					outArgKey, outArgVal, err = reverseConvertData(curParamData, tfstateAttr, tfstateOutParamVal, reqParam, regionData)
				case models.ConvertWay["Template"]:
					if tfstateAttr.DefaultValue != "" {
						tfstateOutParamVal = tfstateAttr.DefaultValue
					}
					outArgKey, outArgVal, err = reverseConvertTemplate(curParamData, providerData, tfstateOutParamVal)
				case models.ConvertWay["Attr"]:
					outArgKey, outArgVal, err = reverseConvertAttr(curParamData, tfstateAttr, tfstateOutParamVal, reqParam, regionData)
				case models.ConvertWay["ContextData"]:
					outArgKey, outArgVal, isDiscard, err = reverseConvertContextData(curParamData, tfstateAttr, tfstateOutParamVal, curLevelResult, reqParam, regionData)
				case models.ConvertWay["Direct"]:
					outArgKey, outArgVal, err = reverseConvertDirect(curParamData, tfstateAttr, tfstateOutParamVal)
					// outArgKey, outArgVal, err = curParamData.Name, tfstateOutParamVal, nil
				case models.ConvertWay["Function"]:
					outArgKey, outArgVal, err = reverseConvertFunction(curParamData, tfstateAttr, tfstateOutParamVal)
				case models.ConvertWay["ContextDirect"]:
					outArgKey, outArgVal, isDiscard, err = reverseConvertContextDirect(curParamData, tfstateAttr, tfstateOutParamVal, curLevelResult, reqParam, regionData)
				case models.ConvertWay["ContextAttr"]:
					outArgKey, outArgVal, isDiscard, err = reverseConvertContextAttr(curParamData, tfstateAttr, tfstateOutParamVal, curLevelResult, reqParam, regionData)
				case models.ConvertWay["ContextTemplate"]:
					outArgKey, outArgVal, isDiscard, err = reverseConvertContextTemplate(curParamData, tfstateAttr, tfstateOutParamVal, curLevelResult, reqParam, regionData, providerData)
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
					err = fmt.Errorf("TfstateAttr:%s Reverse convert parameter:%s error:%s", tfstateAttr.Name, curParamData.Name, err.Error())
					log.Logger.Error("Revese convert parameter error", log.String("tfstateAttrName", tfstateAttr.Name), log.String("parameter", curParamData.Name), log.Error(err))
					return
				}

				// check outArg type, string -> int
				/*
					if _, ok := outArgVal.(string); ok {
						if curParamData.DataType == "int" {
							// tmpVal, _ := strconv.Atoi(outArgVal.(string))
							// tmpVal := outArgVal.(float64)
							tmpVal, _ := strconv.ParseFloat(fmt.Sprintf("%v", outArgVal), 64)
							outArgVal = tmpVal
						}
					}
				*/
				if curParamData.DataType == "int" {
					if tfstateAttr.IsMulti == "Y" {
						if tmpVal, ok := outArgVal.([]string); ok {
							tmpRes := []float64{}
							for i := range tmpVal {
								tmpRet, _ := strconv.ParseFloat(fmt.Sprintf("%v", tmpVal[i]), 64)
								tmpRes = append(tmpRes, tmpRet)
							}
							outArgVal = tmpRes
						}
					} else {
						if tmpVal, ok := outArgVal.(string); ok {
							tmpRes, _ := strconv.ParseFloat(fmt.Sprintf("%v", tmpVal), 64)
							outArgVal = tmpRes
						}
					}
				} else if curParamData.DataType == "string" {
					if tfstateAttr.IsMulti == "Y" {
						if tmpVal, ok := outArgVal.([]float64); ok {
							tmpRes := []string{}
							for i := range tmpVal {
								tmpRes = append(tmpRes, fmt.Sprintf("%.0f", tmpVal[i]))
							}
						}
					} else {
						if tmpVal, ok := outArgVal.(float64); ok {
							outArgVal = fmt.Sprintf("%.0f", tmpVal)
						}
					}
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
			//}
		} else {
			continue
		}
	}
	return
}

func getSortedSourceList(sourceList []*models.SourceTable, interfaceData *models.InterfaceTable, providerData *models.ProviderTable) (sortedSourceList []*models.SourceTable, err error) {
	sortedSourceListIdMap := make(map[string]bool)
	if len(sourceList) == 1 {
		sortedSourceList = append(sortedSourceList, sourceList[0])
		return
	} else {
		// get the first batch sourceListId
		// sqlCmd := `SELECT DISTINCT(source) FROM tf_argument WHERE source NOT IN (SELECT id FROM source WHERE interface=? AND provider=?) AND (parameter is null AND relative_source is null)`
		sqlCmd := `SELECT DISTINCT(source) FROM tf_argument WHERE source NOT IN (SELECT DISTINCT(source) FROM tf_argument WHERE source IN (SELECT id FROM source WHERE interface=? AND provider=?) AND parameter is null AND relative_source is not null) AND source IN (SELECT id FROM source WHERE interface=? AND provider=?)`
		paramArgs := []interface{}{interfaceData.Id, providerData.Id, interfaceData.Id, providerData.Id}
		var tmpTfArgumentList []*models.TfArgumentTable
		err = x.SQL(sqlCmd, paramArgs...).Find(&tmpTfArgumentList)
		if err != nil {
			err = fmt.Errorf("Get first batch source ids by interface:%s and provider:%s error:%s", interfaceData.Id, providerData.Id, err.Error())
			log.Logger.Error("Get first batch source ids by interface and provider error", log.String("interface", interfaceData.Id), log.String("provider", providerData.Id), log.Error(err))
			return
		}
		if len(tmpTfArgumentList) == 0 {
			err = fmt.Errorf("First batch source_ids can not be found by interface:%s and provider:%s", interfaceData.Id, providerData.Id)
			log.Logger.Warn("First batch source ids can not be found by interface and provider", log.String("interface", interfaceData.Id), log.String("provider", providerData.Id), log.Error(err))
			return
		}

		initAllSourceListIdMap := make(map[string]*models.SourceTable)
		for i := range sourceList {
			initAllSourceListIdMap[sourceList[i].Id] = sourceList[i]
		}

		// delete the first batch sources in initAllSourceListIdMap
		for i := range tmpTfArgumentList {
			if _, ok := initAllSourceListIdMap[tmpTfArgumentList[i].Source]; ok {
				sortedSourceListIdMap[tmpTfArgumentList[i].Source] = true
				sortedSourceList = append(sortedSourceList, initAllSourceListIdMap[tmpTfArgumentList[i].Source])
				delete(initAllSourceListIdMap, tmpTfArgumentList[i].Source)
			} else {
				err = fmt.Errorf("TfArgument config error: there are some first batch sourceIds not in allSourceList")
				log.Logger.Warn("TfArgument config error: there are some first batch sourceIds not in allSourceList", log.Error(err))
				return
			}
		}

		// get the all tf_argument data of each remain source list
		tfArgumentListSourceIdMap := make(map[string][]*models.TfArgumentTable)
		for sourceId := range initAllSourceListIdMap {
			sqlCmd = `SELECT * FROM tf_argument WHERE source=?`
			paramArgs = []interface{}{sourceId}
			var tmpTfArgumentList []*models.TfArgumentTable
			err = x.SQL(sqlCmd, paramArgs...).Find(&tmpTfArgumentList)
			if err != nil {
				err = fmt.Errorf("Get tfArgument data by source:%s error:%s", sourceId, err.Error())
				log.Logger.Error("Get tfArgument data by source error", log.String("source", sourceId), log.Error(err))
				return
			}
			if len(tmpTfArgumentList) == 0 {
				err = fmt.Errorf("TfArgument data can not be found by source:%s", sourceId)
				log.Logger.Warn("TfArgument data can not be found by source", log.String("source", sourceId), log.Error(err))
				return
			}
			for i := range tmpTfArgumentList {
				tfArgumentListSourceIdMap[sourceId] = append(tfArgumentListSourceIdMap[sourceId], tmpTfArgumentList[i])
			}
		}

		// get the second, the third batch sources ...
		remainCnt := len(initAllSourceListIdMap)
		for remainCnt > 0 {
			for sourceId := range initAllSourceListIdMap {
				isValid := true
				for _, tmpTfArgument := range tfArgumentListSourceIdMap[sourceId] {
					if tmpTfArgument.Parameter != "" {
						continue
					} else {
						if _, ok := sortedSourceListIdMap[tmpTfArgument.RelativeSource]; ok {
							continue
						} else {
							isValid = false
							break
						}
					}
				}
				if isValid == true {
					sortedSourceListIdMap[sourceId] = true
					sortedSourceList = append(sortedSourceList, initAllSourceListIdMap[sourceId])
					delete(initAllSourceListIdMap, sourceId)
				}
			}
			if len(initAllSourceListIdMap) == remainCnt {
				err = fmt.Errorf("TfArgument config error: there are some sourceIds can not be in sortedSourceList")
				log.Logger.Warn("TfArgument config error: there are some sourceIds can not be in sortedSourceList", log.Error(err))
				return
			}
			remainCnt = len(initAllSourceListIdMap)
		}
	}
	return
}

func handleConStructObject(conStructObject *[]map[string]interface{}, inPutValSlice [][]interface{}, curObject map[string]interface{}, idx int) {
	if idx == len(inPutValSlice) {
		tmpObject := make(map[string]interface{})
		for k, v := range curObject {
			tmpObject[k] = v
		}
		if len(tmpObject) > 0 {
			*conStructObject = append(*conStructObject, tmpObject)
		}
		return
	}
	for i := 0; i < len(inPutValSlice[idx]); i++ {
		tmpVal := inPutValSlice[idx][i].(map[string]interface{})
		for k, v := range tmpVal {
			curObject[k] = v
		}
		handleConStructObject(conStructObject, inPutValSlice, curObject, idx+1)
		for k, _ := range tmpVal {
			delete(curObject, k)
		}
	}
	return
}

func handleConvertParams(action string,
	sourceData *models.SourceTable,
	tfArgumentList []*models.TfArgumentTable,
	reqParam map[string]interface{},
	providerData *models.ProviderTable,
	regionData *models.ResourceDataTable) (tfArguments map[string]interface{}, resourceAssetId interface{}, err error) {

	var errorTfArgument *models.TfArgumentTable
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("HandleConvertParams error, sourceName: %s, TfArgument:%s convert error:%v", sourceData.Name, errorTfArgument.Name, r)
		}
	}()

	// sort the tfArgumentList
	tfArgumentIdMap := make(map[string]*models.TfArgumentTable)
	orderTfArgumentList := []*models.TfArgumentTable{}
	for i, v := range tfArgumentList {
		if v.ObjectName == "" {
			orderTfArgumentList = append(orderTfArgumentList, tfArgumentList[i])
			tfArgumentIdMap[v.Id] = tfArgumentList[i]
		}
	}
	for i, v := range tfArgumentList {
		if _, ok := tfArgumentIdMap[v.Id]; !ok {
			orderTfArgumentList = append(orderTfArgumentList, tfArgumentList[i])
			tfArgumentIdMap[v.Id] = tfArgumentList[i]
		}
	}

	tfArgumentList = orderTfArgumentList

	tfArguments = make(map[string]interface{})
	// 循环处理每一个 tf_argument
	for i := range tfArgumentList {
		errorTfArgument = tfArgumentList[i]
		convertWay := tfArgumentList[i].ConvertWay
		var arg interface{}
		var isDiscard = false
		switch convertWay {
		case models.ConvertWay["Data"]:
			// search resource_data table，get resource_asset_id by resource_id and resource(which is relative_source column in tf_argument table )
			arg, err = convertData(tfArgumentList[i].RelativeSource, reqParam, regionData, tfArgumentList[i], sourceData)
		case models.ConvertWay["Template"]:
			arg, err = convertTemplate(providerData, reqParam, tfArgumentList[i])
		case models.ConvertWay["ContextData"]:
			arg, isDiscard, err = convertContextData(tfArgumentList[i], reqParam, regionData, tfArgumentList[i], sourceData)
		case models.ConvertWay["Attr"]:
			// search resouce_data table by relative_source and 输入的值, 获取 tfstat_file 字段内容,找到relative_tfstate_attribute id(search tfstate_attribute table) 对应的 name, 获取其在 tfstate_file 中的值
			arg, err = convertAttr(tfArgumentList[i], reqParam, regionData, tfArgumentList[i], sourceData)
		case models.ConvertWay["Direct"]:
			arg, err = convertDirect(tfArgumentList[i].DefaultValue, reqParam, tfArgumentList[i])
		case models.ConvertWay["Function"]:
			arg, err = convertFunction(tfArgumentList[i], reqParam, tfArgumentList[i])
		case models.ConvertWay["ContextDirect"]:
			arg, isDiscard, err = convertContextDirect(tfArgumentList[i], reqParam, regionData)
		case models.ConvertWay["ContextAttr"]:
			arg, isDiscard, err = convertContextAttr(tfArgumentList[i], reqParam, regionData, sourceData)
		case models.ConvertWay["ContextTemplate"]:
			arg, isDiscard, err = convertContextTemplate(tfArgumentList[i], reqParam, regionData, providerData)
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
				if arg != nil && arg != "" {
					if resourceAssetId == "" || resourceAssetId == nil {
						resourceAssetId = arg
					} else {
						if resourceAssetId != arg {
							err = fmt.Errorf("Source:%s, tfArgument:%s two asset_id result is different error", sourceData.Name, tfArgumentList[i].Name)
							log.Logger.Error("Convert parameter error: two asset_id result is different", log.String("sourceName", sourceData.Name), log.String("tfArgumentName", tfArgumentList[i].Name), log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
							return
						}
					}
				}
				/*
					if parameterData.Name == "id" {
						// if arg != nil {
						// 	resourceId = arg.(string)
						// }
					} else if parameterData.Name == "asset_id" {
						if arg != nil {
							resourceAssetId = arg.(string)
						}
					}
				*/
				continue
			}

			// merge the input tfArgument
			if tfArgumentList[i].ObjectName != "" {
				relativeTfArgumentData := tfArgumentIdMap[tfArgumentList[i].ObjectName]
				if relativeTfArgumentData != nil && relativeTfArgumentData.Type == "object" && (relativeTfArgumentData.Name == "tags" || relativeTfArgumentData.Parameter == "") {
					// tmpVal := tfArguments[relativeTfArgumentData.Name].(map[string]interface{})
					// tmpVal[tfArgumentList[i].Name] = arg
					// tfArguments[relativeTfArgumentData.Name] = tmpVal
					if tfArguments[relativeTfArgumentData.Name] != nil {
						// fmt.Printf("%v, %v, %T ## ", tfArguments[relativeTfArgumentData.Name], tfArguments[relativeTfArgumentData.Name] == nil, tfArguments[relativeTfArgumentData.Name])
						tmpVal := tfArguments[relativeTfArgumentData.Name].(map[string]interface{})
						if len(tmpVal) == 0 {
							tmpVal = make(map[string]interface{})
						}
						if arg != nil {
							tmpVal[tfArgumentList[i].Name] = arg
						}
						tfArguments[relativeTfArgumentData.Name] = tmpVal
					} else {
						if arg != nil {
							tmpVal := make(map[string]interface{})
							tmpVal[tfArgumentList[i].Name] = arg
							tfArguments[relativeTfArgumentData.Name] = tmpVal
						}
					}
					continue
				}
			}
		}

		if action == "query" {
			// merge the input tfArgument
			if tfArgumentList[i].ObjectName != "" {
				relativeTfArgumentData := tfArgumentIdMap[tfArgumentList[i].ObjectName]
				if relativeTfArgumentData != nil && relativeTfArgumentData.Type == "object" && relativeTfArgumentData.Parameter == "" {
					// tmpVal := tfArguments[relativeTfArgumentData.Name].(map[string]interface{})
					// tmpVal[tfArgumentList[i].Name] = arg
					// tfArguments[relativeTfArgumentData.Name] = tmpVal
					if tfArguments[relativeTfArgumentData.Name] != nil {
						// fmt.Printf("%v, %v, %T ## ", tfArguments[relativeTfArgumentData.Name], tfArguments[relativeTfArgumentData.Name] == nil, tfArguments[relativeTfArgumentData.Name])
						tmpVal := tfArguments[relativeTfArgumentData.Name].(map[string]interface{})
						if len(tmpVal) == 0 {
							tmpVal = make(map[string]interface{})
						}
						if arg != nil {
							tmpVal[tfArgumentList[i].Name] = arg
						}
						tfArguments[relativeTfArgumentData.Name] = tmpVal
					} else {
						if arg != nil {
							tmpVal := make(map[string]interface{})
							tmpVal[tfArgumentList[i].Name] = arg
							tfArguments[relativeTfArgumentData.Name] = tmpVal
						}
					}
					continue
				}
			}
		}

		if action == "query" {
			if arg == nil || arg == "" {
				continue
			}
		}

		if err != nil {
			err = fmt.Errorf("Source:%s, tfArgument:%s, Convert parameter:%s error:%s", sourceData.Name, tfArgumentList[i].Name, tfArgumentList[i].Parameter, err.Error())
			log.Logger.Error("Convert parameter error", log.String("sourceName", sourceData.Name), log.String("tfArgumentName", tfArgumentList[i].Name), log.String("parameterId", tfArgumentList[i].Parameter), log.Error(err))
			return
		}

		if arg == nil || arg == "" {
			continue
		}

		// check the type string, int
		if tfArgumentList[i].Type == "int" {
			// tmpVal, ok := arg.(int)
			// tmpVal, _ := strconv.Atoi(arg.(string))
			// tmpVal := arg.(float64)
			/*
				tmpVal, _ := strconv.ParseFloat(fmt.Sprintf("%v", arg), 64)
				arg = tmpVal
			*/
			if tfArgumentList[i].IsMulti == "Y" {
				if tmpVal, ok := arg.([]string); ok {
					tmpRes := []float64{}
					for i := range tmpVal {
						tmpRet, _ := strconv.ParseFloat(fmt.Sprintf("%v", tmpVal[i]), 64)
						tmpRes = append(tmpRes, tmpRet)
					}
					arg = tmpRes
				}
			} else {
				if tmpVal, ok := arg.(string); ok {
					tmpRes, _ := strconv.ParseFloat(fmt.Sprintf("%v", tmpVal), 64)
					arg = tmpRes
				}
			}
		} else if tfArgumentList[i].Type == "string" {
			if tfArgumentList[i].IsMulti == "Y" {
				if tmpVal, ok := arg.([]float64); ok {
					tmpRes := []string{}
					for i := range tmpVal {
						tmpRes = append(tmpRes, fmt.Sprintf("%.0f", tmpVal[i]))
					}
				}
			} else {
				if tmpVal, ok := arg.(float64); ok {
					arg = fmt.Sprintf("%.0f", tmpVal)
				}
			}
		}

		// merger the tfArgument if they have the same name && tfArgument.IsMulti == "Y"
		if _, ok := tfArguments[tfArgumentList[i].Name]; ok {
			if tfArgumentList[i].IsMulti == "Y" {
				tmpData := []interface{}{}
				if _, ok := tfArguments[tfArgumentList[i].Name].([]interface{}); ok {
					p := reflect.ValueOf(tfArguments[tfArgumentList[i].Name])
					for idx := 0; idx < p.Len(); idx++ {
						tmpData = append(tmpData, p.Index(idx).Interface())
					}
				} else {
					tmpData = append(tmpData, tfArguments[tfArgumentList[i].Name])
				}

				if _, ok := arg.([]interface{}); ok {
					p := reflect.ValueOf(arg)
					for idx := 0; idx < p.Len(); idx++ {
						tmpData = append(tmpData, p.Index(idx).Interface())
					}
				} else {
					tmpData = append(tmpData, arg)
				}
				tfArguments[tfArgumentList[i].Name] = tmpData
			} else {
				tfArguments[tfArgumentList[i].Name] = arg
			}
		} else {
			tfArguments[tfArgumentList[i].Name] = arg
		}

		// handle convert the object type tfArgument
		if tfArgumentList[i].Type == "object" && tfArgumentList[i].Name != "tags" {
			memberArgumentList := []*models.TfArgumentTable{}
			for j := range tfArgumentList {
				if tfArgumentList[j].ObjectName == tfArgumentList[i].Id {
					memberArgumentList = append(memberArgumentList, tfArgumentList[j])
				}
			}
			if len(memberArgumentList) > 0 {
				inputArgs := []map[string]interface{}{}
				if tfArgumentList[i].IsMulti == "Y" {
					// inputArgs = append(inputArgs, arg.([]map[string]interface{})...)
					inputArgs = arg.([]map[string]interface{})
				} else {
					inputArgs = append(inputArgs, arg.(map[string]interface{}))
				}
				tmpConvertResult := []interface{}{}
				for k := range inputArgs {
					if _, ok := reqParam[models.ResourceDataDebug]; ok {
						inputArgs[k][models.ResourceDataDebug] = reqParam[models.ResourceDataDebug]
					}
					tmpRes, _, _ := handleConvertParams(action,
						sourceData,
						memberArgumentList,
						inputArgs[k],
						providerData,
						regionData)
					tmpConvertResult = append(tmpConvertResult, tmpRes)
				}

				if tfArgumentList[i].IsMulti == "Y" {
					tfArguments[tfArgumentList[i].Name] = tmpConvertResult
				} else {
					tfArguments[tfArgumentList[i].Name] = tmpConvertResult[0]
				}
			}
		}

		// if arg != nil && convertWay == "direct" && parameterData.DataType == "string" && arg.(string) == "null" {
		// 	delete(tfArguments, tfArgumentList[i].Name)
		// }
	}
	return
}

func handleTfstateOutPut(sourceData *models.SourceTable,
	interfaceData *models.InterfaceTable,
	reqParam map[string]interface{},
	regionData *models.ResourceDataTable,
	providerData *models.ProviderTable,
	action string,
	dirPath string,
	tfFileContentStr string,
	resourceId string,
	retOutput map[string]interface{},
	curDebugFileContent map[string]interface{},
	isInternalAction bool) (err error) {

	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("HandleTfstateOutPut error:%v", r)
		}
	}()

	sourceIdStr := sourceData.Id
	// Get tfstate_attribute by sourceId
	sqlCmd := "SELECT * FROM tfstate_attribute WHERE source IN ('" + sourceIdStr + "')"
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

	var tfstateObjectTypeAttribute *models.TfstateAttributeTable
	tfstateAttrParamMap := make(map[string]*models.TfstateAttributeTable)
	tfstateAttrNameMap := make(map[string]*models.TfstateAttributeTable)
	tfstateAttrIdMap := make(map[string]*models.TfstateAttributeTable)
	for _, v := range tfstateAttributeList {
		if v.Parameter == "" && v.ObjectName == "" && (v.Name != "ids" && v.Name != "root_block_device") {
			tfstateObjectTypeAttribute = v
		} else {
			tfstateAttrParamMap[v.Parameter] = v
		}
		tfstateAttrNameMap[v.Name] = v
		tfstateAttrIdMap[v.Id] = v
	}

	if action == "apply" {
		tfstateObjectTypeAttribute = nil
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

	// sort the tfstateAttribute by the objectName
	tmptfstateIdMap := make(map[string]*models.TfstateAttributeTable)
	tmpOrderTfstateAttrList := []*models.TfstateAttributeTable{}
	for i, v := range orderTfstateAttrList {
		if v.ObjectName == "" {
			tmpOrderTfstateAttrList = append(tmpOrderTfstateAttrList, orderTfstateAttrList[i])
			tmptfstateIdMap[v.Id] = orderTfstateAttrList[i]
		}
	}
	for i, v := range orderTfstateAttrList {
		if _, ok := tmptfstateIdMap[v.Id]; !ok {
			tmpOrderTfstateAttrList = append(tmpOrderTfstateAttrList, orderTfstateAttrList[i])
			tmptfstateIdMap[v.Id] = orderTfstateAttrList[i]
		}
	}
	orderTfstateAttrList = tmpOrderTfstateAttrList

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

	if _, ok := reqParam[models.ResourceDataDebug]; ok {
		curDebugFileContent["tf_json_new"] = tfFileContentStr
		curDebugFileContent["tf_state_new"] = tfstateFileContentStr
		curDebugFileContent["source_name"] = sourceData.Name
	}

	if action == "apply" {
		// 记录到 resource_data table
		resourceDataId := guid.CreateGuid()
		resourceDataSourceId := sourceData.Id
		resourceDataResourceId := resourceId
		resourceDataResourceAssetId := tfstateFileAttributes[sourceData.AssetIdAttribute]
		createTime := time.Now().Format(models.DateTimeFormat)
		createUser := reqParam["operator_user"].(string)

		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			// get resource_data_debug table
			sqlCmd = "SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"
			var oldResourceDataDebugList []*models.ResourceDataTable
			paramArgs := []interface{}{resourceDataSourceId, resourceDataResourceId, regionData.RegionId, resourceDataResourceAssetId}
			err = x.SQL(sqlCmd, paramArgs...).Find(&oldResourceDataDebugList)
			if err != nil {
				err = fmt.Errorf("Get old_resource data_debug by resource:%s and resource_id:%s error: %s", resourceDataSourceId, resourceDataResourceId, err.Error())
				log.Logger.Error("Get old_resource_data_debug by resource and resource_id error", log.String("resource", resourceDataSourceId), log.String("resource_id", resourceDataResourceId), log.Error(err))
				retOutput["errorMessage"] = err.Error()
			}
			if len(oldResourceDataDebugList) == 0 {
				curDebugFileContent["tf_json_old"] = ""
				curDebugFileContent["tf_state_old"] = ""
			} else {
				curDebugFileContent["tf_json_old"] = oldResourceDataDebugList[0].TfFile
				curDebugFileContent["tf_state_old"] = oldResourceDataDebugList[0].TfStateFile
			}

			if len(oldResourceDataDebugList) == 0 {
				// insert into resource_data_debug
				_, err = x.Exec("INSERT INTO resource_data_debug(id,resource,resource_id,resource_asset_id,tf_file,tf_state_file,region_id,create_time,create_user,update_time,update_user) VALUE (?,?,?,?,?,?,?,?,?,?,?)",
					resourceDataId, resourceDataSourceId, resourceDataResourceId, resourceDataResourceAssetId, tfFileContentStr, tfstateFileContentStr, regionData.RegionId, createTime, createUser, createTime, createUser)

				if _, ok := reqParam[models.ImportResourceDataTableId]; ok {
					delId := reqParam[models.ImportResourceDataTableId].(string)
					_, err = x.Exec("DELETE FROM resource_data_debug WHERE id=?", delId)

					delete(reqParam, models.ImportResourceDataTableId)
				}
			} else {
				// update the oldResourceDataDebug item
				tmpId := oldResourceDataDebugList[0].Id
				tmpTfFile := tfFileContentStr
				tmpTfStateFile := tfstateFileContentStr
				// _, err = x.Exec("UPDATE resource_data_debug SET tf_file=?,tf_state_file=?,update_time=?,update_user=? WHERE id=?",
				//	tmpTfFile, tmpTfStateFile, createTime, createUser, tmpId)
				_, err = x.Exec("UPDATE resource_data_debug SET id=?,tf_file=?,tf_state_file=?,update_time=?,update_user=? WHERE id=?",
					resourceDataId, tmpTfFile, tmpTfStateFile, createTime, createUser, tmpId)
			}
		} else {
			// get resource_data table
			sqlCmd = "SELECT * FROM resource_data WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"
			var oldResourceDataList []*models.ResourceDataTable
			paramArgs := []interface{}{resourceDataSourceId, resourceDataResourceId, regionData.RegionId, resourceDataResourceAssetId}
			err = x.SQL(sqlCmd, paramArgs...).Find(&oldResourceDataList)
			if err != nil {
				err = fmt.Errorf("Get old_resource data by resource:%s and resource_id:%s error: %s", resourceDataSourceId, resourceDataResourceId, err.Error())
				log.Logger.Error("Get old_resource_data by resource and resource_id error", log.String("resource", resourceDataSourceId), log.String("resource_id", resourceDataResourceId), log.Error(err))
				retOutput["errorMessage"] = err.Error()
			}
			if len(oldResourceDataList) == 0 {
				_, err = x.Exec("INSERT INTO resource_data(id,resource,resource_id,resource_asset_id,tf_file,tf_state_file,region_id,create_time,create_user,update_time,update_user) VALUE (?,?,?,?,?,?,?,?,?,?,?)",
					resourceDataId, resourceDataSourceId, resourceDataResourceId, resourceDataResourceAssetId, tfFileContentStr, tfstateFileContentStr, regionData.RegionId, createTime, createUser, createTime, createUser)

				if _, ok := reqParam[models.ImportResourceDataTableId]; ok {
					delId := reqParam[models.ImportResourceDataTableId].(string)
					_, err = x.Exec("DELETE FROM resource_data_debug WHERE id=?", delId)

					delete(reqParam, models.ImportResourceDataTableId)
				}
			} else {
				// update the oldResourceDataDebug item
				tmpId := oldResourceDataList[0].Id
				tmpTfFile := tfFileContentStr
				tmpTfStateFile := tfstateFileContentStr
				// _, err = x.Exec("UPDATE resource_data SET tf_file=?,tf_state_file=?,update_time=?,update_user=? WHERE id=?",
				//	tmpTfFile, tmpTfStateFile, createTime, createUser, tmpId)
				_, err = x.Exec("UPDATE resource_data SET id=?,tf_file=?,tf_state_file=?,update_time=?,update_user=? WHERE id=?",
					resourceDataId, tmpTfFile, tmpTfStateFile, createTime, createUser, tmpId)
			}
		}

		if err != nil {
			err = fmt.Errorf("Try to create resource_data fail,%s ", err.Error())
			log.Logger.Error("Try to create resource_data fail", log.Error(err))
			retOutput["errorMessage"] = err.Error()
		}
	} else if action == "query" {
		/*
			// record the resource_data into simulateResourceData struct
			curSimulateResourceData := reqParam[models.SimulateResourceData].(map[string][]map[string]interface{})
			// curResourceDataSlice := curSimulateResourceData[sourceData.Id]

			curResourceData := make(map[string]interface{})
			curResourceData["resourceId"] = resourceId
			curResourceData["resourceAssetId"] = tfstateFileAttributes[sourceData.AssetIdAttribute]
			curResourceData["tfstateFile"] = tfstateFileContentStr

			// curResourceDataSlice = append(curResourceDataSlice, curResourceData)
			curSimulateResourceData[sourceData.Id] = append(curSimulateResourceData[sourceData.Id], curResourceData)
		*/
	}

	if tfstateObjectTypeAttribute == nil {
		var outPutArgs map[string]interface{}
		parentObjectName := ""
		paramCnt := 0
		outPutArgs, err = handleReverseConvert(outPutParameterNameMap,
			outPutParameterIdMap,
			tfstateAttrParamMap,
			tfstateAttrNameMap,
			tfstateAttrIdMap,
			reqParam,
			providerData,
			tfstateFileAttributes,
			action,
			parentObjectName,
			orderTfstateAttrList,
			&paramCnt,
			regionData)
		if err != nil {
			err = fmt.Errorf("Handle reverse convert error:%s", err.Error())
			log.Logger.Error("Handle revese convert  error", log.Error(err))
			retOutput["errorMessage"] = err.Error()
			return
		}

		if action == "query" {
			// record the resource_data into simulateResourceData struct
			curSimulateResourceData := reqParam[models.SimulateResourceData].(map[string][]map[string]interface{})

			curResourceData := make(map[string]interface{})
			curResourceData["resourceId"] = resourceId
			curResourceData["assetIdAttribute"] = sourceData.AssetIdAttribute
			curResourceData["tfstateFile"] = tfstateFileAttributes
			curSimulateResourceData[sourceData.Id] = append(curSimulateResourceData[sourceData.Id], curResourceData)
		}

		// handle outPutArgs
		outPutResultList, _ := handleOutPutArgs(outPutArgs, outPutParameterNameMap, tfstateAttrParamMap, reqParam, isInternalAction)

		if action == "apply" {
			isInternalAction = false
		}

		if !isInternalAction {
			if action == "apply" {
				if retOutput[models.TerraformOutPutPrefix] == nil {
					retOutput[models.TerraformOutPutPrefix] = outPutResultList
				} else {
					if curRetOutput, ok := retOutput[models.TerraformOutPutPrefix].([]map[string]interface{}); ok {
						if len(curRetOutput) > 0 {
							if len(outPutResultList) > 0 {
								for k, v := range outPutResultList[0] {
									curRetOutput[0][k] = v
								}
							}
						} else {
							retOutput[models.TerraformOutPutPrefix] = outPutResultList
						}
					} else {
						retOutput[models.TerraformOutPutPrefix] = outPutResultList
					}
				}
			} else {
				retOutput[models.TerraformOutPutPrefix] = outPutResultList
			}
		}

		if action == "query" {
			curRes := reqParam[models.SimulateResourceDataResult].(map[string][]map[string]interface{})
			curRes[sourceData.Id] = append(curRes[sourceData.Id], outPutResultList...)
			reqParam[models.SimulateResourceDataResult] = curRes
		}
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

		if action == "query" {
			// record the resource_data into simulateResourceData struct
			curSimulateResourceData := reqParam[models.SimulateResourceData].(map[string][]map[string]interface{})

			for i := range tfstateResult {
				curResourceData := make(map[string]interface{})
				curResourceData["resourceId"] = resourceId
				curResourceData["assetIdAttribute"] = sourceData.AssetIdAttribute
				curResourceData["tfstateFile"] = tfstateResult[i]
				curSimulateResourceData[sourceData.Id] = append(curSimulateResourceData[sourceData.Id], curResourceData)
			}
		}

		querryFilteredResult := []map[string]interface{}{}
		outPutResultList := []map[string]interface{}{}
		for i := range tfstateResult {
			var outPutArgs map[string]interface{}
			parentObjectName := tfstateObjectTypeAttribute.Id
			paramCnt := 0
			outPutArgs, err = handleReverseConvert(outPutParameterNameMap,
				outPutParameterIdMap,
				tfstateAttrParamMap,
				tfstateAttrNameMap,
				tfstateAttrIdMap,
				reqParam,
				providerData,
				tfstateResult[i],
				action,
				parentObjectName,
				orderTfstateAttrList,
				&paramCnt,
				regionData)

			if err != nil {
				err = fmt.Errorf("Handle reverse convert error:%s", err.Error())
				log.Logger.Error("Handle revese convert  error", log.Error(err))
				retOutput["errorMessage"] = err.Error()
				return
			}

			// handle outPutArgs
			tmpOutPutResult, _ := handleOutPutArgs(outPutArgs, outPutParameterNameMap, tfstateAttrParamMap, reqParam, isInternalAction)
			outPutResultList = append(outPutResultList, tmpOutPutResult...)
			//retOutput[models.TerraformOutPutPrefix] = outPutResultList

			if action == "query" {
				if reqParam[models.SourceDataIdx] == 0 {
					// action: query, check the result is valid
					filterKeys := make(map[string]interface{})
					for k := range reqParam {
						if _, ok := models.ExcludeFilterKeys[k]; !ok {
							filterKeys[k] = reqParam[k]
						}
					}
					for ix := range tmpOutPutResult {
						isValid := true
						for k, v := range filterKeys {
							if tmpOutPutResult[ix][k] != v {
								isValid = false
								break
							}
						}
						if isValid {
							tmpFilterRes := make(map[string]interface{})
							tmpFilterRes[sourceData.AssetIdAttribute] = tfstateResult[i][sourceData.AssetIdAttribute]
							tmpFilterRes["output"] = tmpOutPutResult[ix]
							querryFilteredResult = append(querryFilteredResult, tmpFilterRes)
						}
					}
				}
			}

		}

		if action == "apply" {
			isInternalAction = false
		}

		if !isInternalAction {
			if action == "apply" {
				if retOutput[models.TerraformOutPutPrefix] == nil {
					retOutput[models.TerraformOutPutPrefix] = outPutResultList
				} else {
					if curRetOutput, ok := retOutput[models.TerraformOutPutPrefix].([]map[string]interface{}); ok {
						if len(curRetOutput) > 0 {
							if len(outPutResultList) > 0 {
								for k, v := range outPutResultList[0] {
									curRetOutput[0][k] = v
								}
							}
						} else {
							retOutput[models.TerraformOutPutPrefix] = outPutResultList
						}
					} else {
						retOutput[models.TerraformOutPutPrefix] = outPutResultList
					}
				}
			} else {
				retOutput[models.TerraformOutPutPrefix] = outPutResultList
			}
		}
		if action == "query" {
			curRes := reqParam[models.SimulateResourceDataResult].(map[string][]map[string]interface{})
			if reqParam[models.SourceDataIdx] == 0 {
				curRes[sourceData.Id] = append(curRes[sourceData.Id], querryFilteredResult...)
				reqParam[models.SimulateResourceDataResult] = curRes
			} else {
				curRes[sourceData.Id] = append(curRes[sourceData.Id], outPutResultList...)
				reqParam[models.SimulateResourceDataResult] = curRes
			}
		}
	}
	return
}

func getOldTfFile(curDebugFileContent map[string]interface{},
	regionData *models.ResourceDataTable,
	sourceData *models.SourceTable,
	resourceId string,
	resourceAssetId string) (err error) {

	// get resource_data_debug table
	sqlCmd := "SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"
	var oldResourceDataDebugList []*models.ResourceDataTable
	paramArgs := []interface{}{sourceData.Id, resourceId, regionData.RegionId, resourceAssetId}
	err = x.SQL(sqlCmd, paramArgs...).Find(&oldResourceDataDebugList)
	if err != nil {
		err = fmt.Errorf("Get old_resource data_debug by resource:%s and resource_id:%s error: %s", sourceData.Id, resourceId, err.Error())
		log.Logger.Error("Get old_resource_data_debug by resource and resource_id error", log.String("resource", sourceData.Id), log.String("resource_id", resourceId), log.Error(err))
	}
	if len(oldResourceDataDebugList) == 0 {
		curDebugFileContent["tf_json_old"] = ""
		curDebugFileContent["tf_state_old"] = ""
	} else {
		curDebugFileContent["tf_json_old"] = oldResourceDataDebugList[0].TfFile
		curDebugFileContent["tf_state_old"] = oldResourceDataDebugList[0].TfStateFile
	}
	return
}

func deleteOldResourceData(sourceData *models.SourceTable,
	regionData *models.ResourceDataTable,
	resourceId string,
	resourceAssetId string,
	reqParam map[string]interface{}) (err error) {

	resourceDataSourceId := sourceData.Id
	resourceDataResourceId := resourceId
	resourceDataResourceAssetId := resourceAssetId

	sqlCmd := "SELECT * FROM resource_data WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"
	if _, ok := reqParam[models.ResourceDataDebug]; ok {
		sqlCmd = "SELECT * FROM resource_data_debug WHERE resource=? AND resource_id=? AND region_id=? AND resource_asset_id=?"
	}
	var oldResourceDataList []*models.ResourceDataTable
	paramArgs := []interface{}{resourceDataSourceId, resourceDataResourceId, regionData.RegionId, resourceDataResourceAssetId}
	err = x.SQL(sqlCmd, paramArgs...).Find(&oldResourceDataList)
	if err != nil {
		err = fmt.Errorf("Get old_resource data_debug by resource:%s and resource_id:%s error: %s", resourceDataSourceId, resourceDataResourceId, err.Error())
		log.Logger.Error("Get old_resource_data_debug by resource and resource_id error", log.String("resource", resourceDataSourceId), log.String("resource_id", resourceDataResourceId), log.Error(err))
	}
	if len(oldResourceDataList) > 0 {
		resourceData := oldResourceDataList[0]
		if _, ok := reqParam[models.ResourceDataDebug]; ok {
			_, err = x.Exec("DELETE FROM resource_data_debug WHERE id=?", resourceData.Id)
		} else {
			_, err = x.Exec("DELETE FROM resource_data WHERE id=?", resourceData.Id)
		}
	}
	return
}

func compareObject(first, second map[string]interface{}) (result map[string]interface{}, diff int, message string) {
	result = make(map[string]interface{})
	for k, v := range second {
		result[k] = v
		if v == nil {
			if first[k] != nil {
				// fmt.Printf("k: %s is nil,use first value:%v \n", k, first[k])
				result[k] = first[k]
			}
			continue
		}
		tmpFirV := fmt.Sprintf("%v", first[k])
		tmpSecV := fmt.Sprintf("%v", v)
		if tmpSecV == "[]" || tmpSecV == "{}" || tmpSecV == "map[]" {
			//fmt.Printf("k:%s fir:%s sec:%s \n",k, tmpFirV, tmpSecV)
			if tmpFirV == "" || tmpFirV == "<nil>" {
				continue
			}
		}
		if tmpSecV != tmpFirV {
			diff = 1
			message += fmt.Sprintf("Key:%s is diff with record:%s, real:%s \n", k, tmpFirV, tmpSecV)
		}
	}
	message = strings.ReplaceAll(message, "<nil>", "null")
	return
}

func getFileAttrContent(filename string) models.TfFileAttrFetchResult {
	result := models.TfFileAttrFetchResult{}
	tfFileByte, _ := ioutil.ReadFile(filename)
	result.FileContent = string(tfFileByte)
	startFlag, startIndex, endIndex := 0, 0, 0
	for i := strings.Index(result.FileContent, "\"attributes\":"); i < len(result.FileContent); i++ {
		if result.FileContent[i] == 123 {
			startFlag += 1
			if startIndex == 0 {
				startIndex = i
			}
			continue
		}
		if result.FileContent[i] == 125 {
			startFlag = startFlag - 1
			if startFlag == 0 {
				endIndex = i
				break
			}
		}
	}
	endIndex += 1
	result.StartIndex = startIndex
	result.EndIndex = endIndex
	result.AttrBytes = []byte(result.FileContent[startIndex:endIndex])
	return result
}

func GenTerraformConfigFile(dirPath string, providerData *models.ProviderTable) (err error) {
	// provider
	providerContentData := make(map[string]map[string]interface{})
	providerContentData[providerData.Name] = make(map[string]interface{})

	// terraform
	terraformData := make(map[string]map[string]map[string]interface{})
	terraformData["required_providers"] = make(map[string]map[string]interface{})
	terraformData["required_providers"][providerData.Name] = make(map[string]interface{})
	terraformData["required_providers"][providerData.Name]["source"] = providerData.NameSpace + "/" + providerData.Name
	terraformData["required_providers"][providerData.Name]["version"] = providerData.Version

	providerFileData := make(map[string]interface{})
	providerFileData["terraform"] = terraformData
	providerFileData["provider"] = providerContentData

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
	return
}
