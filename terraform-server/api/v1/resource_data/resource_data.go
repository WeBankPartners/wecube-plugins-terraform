package resource_data

import (
	"encoding/json"
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/services/db"
	"github.com/gin-gonic/gin"
	"io/ioutil"
	"net/http"
	"reflect"
	"strconv"
	"strings"
)

func ResourceDataBatchCreate(c *gin.Context) {
	var param []*models.ResourceDataTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	rowData, err := db.ResourceDataBatchCreate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnData(c, rowData)
	}
}

func ResourceDataList(c *gin.Context) {
	paramsMap := make(map[string]interface{})
	rowData, err := db.ResourceDataList(paramsMap)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.ResourceDataTable{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func ResourceDataBatchDelete(c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	param := strings.Split(trimIds, ",")
	if len(param) == 0 {
		middleware.ReturnParamEmptyError(c, "ids")
		return
	}
	err := db.ResourceDataBatchDelete(param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func ResourceDataBatchUpdate(c *gin.Context) {
	var param []*models.ResourceDataTable
	var err error
	if err = c.ShouldBindJSON(&param); err != nil {
		middleware.ReturnParamValidateError(c, err)
		return
	}
	user := middleware.GetRequestUser(c)
	err = db.ResourceDataBatchUpdate(user, param)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		middleware.ReturnSuccess(c)
	}
	return
}

func TerraformOperation(c *gin.Context) {
	plugin := c.Param("plugin")
	action := c.Param("action")

	if plugin == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param plugin can not be empty "))
		return
	}

	if action == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param action can not be empty "))
		return
	}

	var err error
	bodyData, err := ioutil.ReadAll(c.Request.Body)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	}

	var request_param map[string]interface{}
	err = json.Unmarshal(bodyData, &request_param)
	inputs := request_param["inputs"]
	p := reflect.ValueOf(inputs)
	params := []map[string]interface{}{}
	for i := 0; i < p.Len(); i++ {
		params = append(params, p.Index(i).Interface().(map[string]interface{}))
	}

	rowData := models.PluginInterfaceResultObj{}
	rowData.ResultCode = "0"
	rowData.ResultMessage = "success"
	for i := range params {
		params[i]["operator_user"] = request_param["operator"]
		params[i]["requestId"] = request_param["requestId"]
		params[i]["requestSn"] = strconv.Itoa(i + 1)
		retData, err := db.TerraformOperation(plugin, action, params[i])
		if err != nil {
			rowData.ResultCode = "1"
			rowData.ResultMessage = "fail"
		}
		// handle one input, many output
		if v, ok := retData[models.TerraformOutPutPrefix]; ok {
			tmpData, _ := json.Marshal(v)
			var resultList []map[string]interface{}
			json.Unmarshal(tmpData, &resultList)
			for i := range resultList {
				tmpRetData := make(map[string]interface{})
				tmpRetData["callbackParameter"] = retData["callbackParameter"]
				tmpRetData["errorCode"] = retData["errorCode"]
				tmpRetData["errorMessage"] = retData["errorMessage"]
				for k, v := range resultList[i] {
					tmpRetData[k] = v
				}
				rowData.Results.Outputs = append(rowData.Results.Outputs, tmpRetData)
			}
		} else {
			rowData.Results.Outputs = append(rowData.Results.Outputs, retData)
		}
	}
	c.JSON(http.StatusOK, rowData)
	return
}

// for resource_data_debug
func ResourceDataDebugList (c *gin.Context) {
	ids := c.Query("ids")
	trimIds := strings.Trim(ids, ",")
	queryIds := strings.Split(trimIds, ",")
	queryIdsStr := strings.Join(queryIds, "','")
	rowData, err := db.ResourceDataDebugList(queryIdsStr)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	} else {
		if len(rowData) == 0 {
			rowData = []*models.ResourceDataQuery{}
		}
		middleware.ReturnData(c, rowData)
	}
	return
}

func TerraformOperationDebug (c *gin.Context) {
	plugin := c.Param("plugin")
	action := c.Param("action")

	if plugin == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param plugin can not be empty "))
		return
	}

	if action == "" {
		middleware.ReturnParamValidateError(c, fmt.Errorf("Url param action can not be empty "))
		return
	}

	var err error
	bodyData, err := ioutil.ReadAll(c.Request.Body)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
	}

	var request_param map[string]interface{}
	err = json.Unmarshal(bodyData, &request_param)
	inputs := request_param["inputs"]
	p := reflect.ValueOf(inputs)
	params := []map[string]interface{}{}
	for i := 0; i < p.Len(); i++ {
		params = append(params, p.Index(i).Interface().(map[string]interface{}))
	}

	rowData := models.PluginInterfaceResultObjDebug{}
	rowData.StatusCode = "OK"
	rowData.ResultCode = "0"
	rowData.ResultMessage = "success"
	for i := range params {
		params[i]["operator_user"] = request_param["operator"]
		params[i]["requestId"] = request_param["requestId"]
		params[i]["requestSn"] = strconv.Itoa(i + 1)
		params[i][models.ResourceDataDebug] = true

		retData, err := db.TerraformOperation(plugin, action, params[i])
		if err != nil {
			rowData.ResultCode = "1"
			rowData.ResultMessage = "fail"
		}

		// get file data
		tf_json_old := params[i][models.ResourceDataDebug+"oldTfFile"]
		tf_json_new := params[i][models.ResourceDataDebug+"newTfFile"]
		tf_state_old := params[i][models.ResourceDataDebug+"oldTfStateFile"]
		tf_state_new := params[i][models.ResourceDataDebug+"newTfStateFile"]
		tf_state_import := params[i][models.ResourceDataDebug+"importTfFile"]
		plan_message := params[i][models.ResourceDataDebug+"planFile"]
		sourceName := params[i][models.ResourceDataDebug+"sourceName"]

		delete(params[i], models.ResourceDataDebug+"oldTfFile")
		delete(params[i], models.ResourceDataDebug+"newTfFile")
		delete(params[i], models.ResourceDataDebug+"oldTfStateFile")
		delete(params[i], models.ResourceDataDebug+"newTfStateFile")
		delete(params[i], models.ResourceDataDebug+"importTfFile")
		delete(params[i], models.ResourceDataDebug+"planFile")
		delete(params[i], models.ResourceDataDebug+"sourceName")

		// handle one input, many output
		curResultOutputs := []map[string]interface{}{}
		if v, ok := retData[models.TerraformOutPutPrefix]; ok {
			tmpData, _ := json.Marshal(v)
			var resultList []map[string]interface{}
			json.Unmarshal(tmpData, &resultList)
			for i := range resultList {
				tmpRetData := make(map[string]interface{})
				tmpRetData["callbackParameter"] = retData["callbackParameter"]
				tmpRetData["errorCode"] = retData["errorCode"]
				tmpRetData["errorMessage"] = retData["errorMessage"]
				for k, v := range resultList[i] {
					tmpRetData[k] = v
				}
				curResultOutputs = append(curResultOutputs, tmpRetData)
				//rowData.Results.Outputs = append(rowData.Results.Outputs, tmpRetData)
			}
		} else {
			curResultOutputs = append(curResultOutputs, retData)
			//rowData.Results.Outputs = append(rowData.Results.Outputs, retData)
		}
		curCombineResult := make(map[string]interface{})
		curCombineResult["result_data"] = curResultOutputs

		tmpCurCombineResult := make(map[string]interface{})
		tmpCurCombineResult["sourc_name"] = sourceName
		tmpCurCombineResult["tf_json_old"] = tf_json_old
		tmpCurCombineResult["tf_json_new"] = tf_json_new
		tmpCurCombineResult["tf_state_old"] = tf_state_old
		tmpCurCombineResult["tf_state_new"] = tf_state_new
		tmpCurCombineResult["tf_state_import"] = tf_state_import
		tmpCurCombineResult["plan_message"] = plan_message

		tmpSlice := []interface{}{}
		tmpSlice = append(tmpSlice, tmpCurCombineResult)
		curCombineResult["resource_results"] = tmpSlice

		rowData.Results.Outputs = append(rowData.Results.Outputs, curCombineResult)
	}
	c.JSON(http.StatusOK, rowData)
	return
}