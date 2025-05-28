package resource_data

import (
	"encoding/json"
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/try"
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
	resource := c.Query("resource")
	resourceId := c.Query("resource_id")
	resourceAssetId := c.Query("resource_asset_id")
	pageStr := c.DefaultQuery("page", "1")
	pageSizeStr := c.DefaultQuery("pageSize", "20")
	page, _ := strconv.Atoi(pageStr)
	pageSize, _ := strconv.Atoi(pageSizeStr)
	if page < 1 {
		page = 1
	}
	if pageSize < 1 {
		pageSize = 20
	}

	paramsMap := map[string]interface{}{}
	if resource != "" {
		paramsMap["resource"] = resource
	}
	if resourceId != "" {
		paramsMap["resource_id"] = resourceId
	}
	if resourceAssetId != "" {
		paramsMap["resource_asset_id"] = resourceAssetId
	}

	rowData, total, err := db.ResourceDataListWithPage(paramsMap, page, pageSize)
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
		return
	}
	if len(rowData) == 0 {
		rowData = []*models.ResourceDataQuery{}
	}
	pageInfo := models.PageInfo{
		StartIndex: (page - 1) * pageSize,
		PageSize:   pageSize,
		TotalRows:  total,
	}
	middleware.ReturnPageData(c, pageInfo, rowData)
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

func operationConsumer(ch chan int, done chan bool, request_param map[string]interface{}, params []map[string]interface{},
	plugin string, action string, rowData *models.PluginInterfaceResultObj, resultChan chan []map[string]interface{}) {
	for {
		i, ok := <-ch
		if ok {
			if _, ok := request_param["operator"]; ok {
				params[i]["operator_user"] = request_param["operator"]
			} else {
				params[i]["operator_user"] = "system"
			}
			params[i]["requestId"] = request_param["requestId"].(string) + "_" + strconv.Itoa(i+1)
			params[i]["requestSn"] = strconv.Itoa(i + 1)
			debugFileContent := []map[string]interface{}{}
			retData, _ := db.TerraformOperation(plugin, action, params[i], &debugFileContent)
			if _, ok := retData["errorCode"]; ok && retData["errorCode"] != "0" {
				rowData.ResultCode = "1"
				rowData.ResultMessage = "fail"
			}
			curResultOutputs := []map[string]interface{}{}
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
					// rowData.Results.Outputs = append(rowData.Results.Outputs, tmpRetData)
					curResultOutputs = append(curResultOutputs, tmpRetData)
				}
			} else {
				// rowData.Results.Outputs = append(rowData.Results.Outputs, retData)
				curResultOutputs = append(curResultOutputs, retData)
			}
			resultChan <- curResultOutputs
		} else {
			break
		}
	}
	done <- true
	return
}

func TerraformOperation(c *gin.Context) {
	rowData := models.PluginInterfaceResultObj{}
	rowData.ResultCode = "0"
	rowData.ResultMessage = "success"
	/*
		defer func() {
			if r := recover(); r != nil {
				err := fmt.Errorf("TerraformOperation error: %v", r)
				rowData.ResultCode = "1"
				rowData.ResultMessage = err.Error()
				c.JSON(http.StatusOK, rowData)
			}
		}()
	*/
	defer try.ExceptionStack(func(e interface{}, err interface{}) {
		retErr := fmt.Errorf("TerraformOperation error: %v", err)
		rowData.ResultCode = "1"
		rowData.ResultMessage = retErr.Error()
		c.JSON(http.StatusOK, rowData)
		log.Logger.Error(e.(string))
	})

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

	// rowData := models.PluginInterfaceResultObj{}
	// rowData.ResultCode = "0"
	// rowData.ResultMessage = "success"
	count := len(params)
	resultChan := make(chan []map[string]interface{}, count)
	consumerCnt := models.ConsumerCount
	if models.Config.RequestConsumerCount > 0 {
		consumerCnt = models.Config.RequestConsumerCount
	}
	if count < consumerCnt {
		consumerCnt = count
	}
	ch := make(chan int, consumerCnt)
	doneChan := make(chan bool, consumerCnt)
	for i := 0; i < consumerCnt; i++ {
		go operationConsumer(ch, doneChan, request_param, params, plugin, action, &rowData, resultChan)
	}

	// producer
	for i := 0; i < count; i++ {
		ch <- i
	}
	close(ch)

	for i := 0; i < consumerCnt; i++ {
		<-doneChan
	}

	/*
		var wg sync.WaitGroup
		wg.Add(count)
		for i := range params {
			go func(i int) {
				defer wg.Done()

				if _, ok := request_param["operator"]; ok {
					params[i]["operator_user"] = request_param["operator"]
				} else {
					params[i]["operator_user"] = "system"
				}
				params[i]["requestId"] = request_param["requestId"].(string) + "_" + strconv.Itoa(i + 1)
				params[i]["requestSn"] = strconv.Itoa(i + 1)
				debugFileContent := []map[string]interface{}{}
				retData, _ := db.TerraformOperation(plugin, action, params[i], &debugFileContent)
				if _, ok := retData["errorCode"]; ok && retData["errorCode"] != "0" {
					rowData.ResultCode = "1"
					rowData.ResultMessage = "fail"
				}
				curResultOutputs := []map[string]interface{}{}
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
						// rowData.Results.Outputs = append(rowData.Results.Outputs, tmpRetData)
						curResultOutputs = append(curResultOutputs, tmpRetData)
					}
				} else {
					// rowData.Results.Outputs = append(rowData.Results.Outputs, retData)
					curResultOutputs = append(curResultOutputs, retData)
				}
				resultChan<-curResultOutputs
			}(i)
		}
		wg.Wait()
	*/
	close(resultChan)
	for i := range resultChan {
		curRes := i
		rowData.Results.Outputs = append(rowData.Results.Outputs, curRes...)
	}

	c.JSON(http.StatusOK, rowData)
	return
}

// for resource_data_debug
func ResourceDataDebugList(c *gin.Context) {
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

func TerraformOperationDebug(c *gin.Context) {
	rowData := models.PluginInterfaceResultObjDebug{}
	rowData.StatusCode = "OK"
	rowData.ResultCode = "0"
	rowData.ResultMessage = "success"
	defer func() {
		if r := recover(); r != nil {
			err := fmt.Errorf("TerraformOperationDebug error: %v", r)
			rowData.ResultCode = "1"
			rowData.ResultMessage = err.Error()
			c.JSON(http.StatusOK, rowData)
		}
	}()

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

	// rowData := models.PluginInterfaceResultObjDebug{}
	// rowData.StatusCode = "OK"
	// rowData.ResultCode = "0"
	// rowData.ResultMessage = "success"
	count := len(params)
	resultChan := make(chan map[string]interface{}, count)
	consumerCnt := models.ConsumerCount
	if models.Config.RequestConsumerCount > 0 {
		consumerCnt = models.Config.RequestConsumerCount
	}
	if count < consumerCnt {
		consumerCnt = count
	}
	ch := make(chan int, consumerCnt)
	doneChan := make(chan bool, consumerCnt)
	for i := 0; i < consumerCnt; i++ {
		go operationDebugConsumer(ch, doneChan, request_param, params, plugin, action, &rowData, resultChan)
	}

	// producer
	for i := 0; i < count; i++ {
		ch <- i
	}
	close(ch)

	for i := 0; i < consumerCnt; i++ {
		<-doneChan
	}
	/*
		var wg sync.WaitGroup
		wg.Add(count)
		for i := range params {
			go func(i int) {
				defer wg.Done()

				if _, ok := request_param["operator"]; ok {
					params[i]["operator_user"] = request_param["operator"]
				} else {
					params[i]["operator_user"] = "system"
				}
				params[i]["requestId"] = request_param["requestId"].(string) + "_" + strconv.Itoa(i+1)
				params[i]["requestSn"] = strconv.Itoa(i + 1)
				params[i][models.ResourceDataDebug] = true
				debugFileContent := []map[string]interface{}{}
				retData, _ := db.TerraformOperation(plugin, action, params[i], &debugFileContent)
				if _, ok := retData["errorCode"]; ok && retData["errorCode"] != "0" {
					rowData.ResultCode = "1"
					rowData.ResultMessage = "fail"
				}

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
					}
					if len(resultList) == 0 {
						delete(retData, models.TerraformOutPutPrefix)
						curResultOutputs = append(curResultOutputs, retData)
					}
				} else {
					curResultOutputs = append(curResultOutputs, retData)
				}
				curCombineResult := make(map[string]interface{})
				curCombineResult["result_data"] = curResultOutputs

				curCombineResult["resource_results"] = debugFileContent
				resultChan<-curCombineResult
			}(i)

			// rowData.Results.Outputs = append(rowData.Results.Outputs, curCombineResult)
		}
		wg.Wait()
	*/
	close(resultChan)
	for i := range resultChan {
		curRes := i
		rowData.Results.Outputs = append(rowData.Results.Outputs, curRes)
	}

	// c.JSON(http.StatusOK, rowData)
	tmpRetVal, _ := json.Marshal(rowData)
	c.Data(http.StatusOK, "application/json", tmpRetVal)
	return
}

func operationDebugConsumer(ch chan int, done chan bool, request_param map[string]interface{}, params []map[string]interface{},
	plugin string, action string, rowData *models.PluginInterfaceResultObjDebug, resultChan chan map[string]interface{}) {
	for {
		i, ok := <-ch
		if ok {
			if _, ok := request_param["operator"]; ok {
				params[i]["operator_user"] = request_param["operator"]
			} else {
				params[i]["operator_user"] = "system"
			}
			params[i]["requestId"] = request_param["requestId"].(string) + "_" + strconv.Itoa(i+1)
			params[i]["requestSn"] = strconv.Itoa(i + 1)
			params[i][models.ResourceDataDebug] = true
			debugFileContent := []map[string]interface{}{}
			retData, _ := db.TerraformOperation(plugin, action, params[i], &debugFileContent)
			if _, ok := retData["errorCode"]; ok && retData["errorCode"] != "0" {
				rowData.ResultCode = "1"
				rowData.ResultMessage = "fail"
			}

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
				}
				if len(resultList) == 0 {
					delete(retData, models.TerraformOutPutPrefix)
					curResultOutputs = append(curResultOutputs, retData)
				}
			} else {
				curResultOutputs = append(curResultOutputs, retData)
			}
			curCombineResult := make(map[string]interface{})
			curCombineResult["result_data"] = curResultOutputs

			curCombineResult["resource_results"] = debugFileContent
			resultChan <- curCombineResult
		} else {
			break
		}
	}
	done <- true
	return
}

func ResourceTypeList(c *gin.Context) {
	resourceList, err := db.GetAllResourceTypes()
	if err != nil {
		middleware.ReturnServerHandleError(c, err)
		return
	}

	// 去重 name 字段
	nameMap := make(map[string]bool)
	result := make([]map[string]string, 0)
	for _, r := range resourceList {
		if _, exists := nameMap[r.Name]; exists {
			continue
		}
		nameMap[r.Name] = true
		result = append(result, map[string]string{
			"id":   r.Id,
			"name": r.Name,
		})
	}

	middleware.ReturnData(c, result)
}
