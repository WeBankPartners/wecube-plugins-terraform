package api

import (
	"bytes"
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/resource_data"
	"io/ioutil"
	"net/http"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/interfaces"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/log_operation"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/parameter"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/plugin"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/provider"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/source"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/template"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/tf_argument"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/tfstate_attribute"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/gin-gonic/gin"
)

type handlerFuncObj struct {
	HandlerFunc  func(c *gin.Context)
	Method       string
	Url          string
	LogOperation bool
}

var (
	httpHandlerFuncList []*handlerFuncObj
)

func init() {
	// declaration
	httpHandlerFuncList = append(httpHandlerFuncList,
		&handlerFuncObj{Url: "/plugins", Method: "POST", HandlerFunc: plugin.PluginBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/plugins", Method: "GET", HandlerFunc: plugin.PluginList},
		&handlerFuncObj{Url: "/plugin/:pluginId", Method: "DELETE", HandlerFunc: plugin.PluginDelete, LogOperation: true},
		&handlerFuncObj{Url: "/plugin/:pluginId", Method: "PUT", HandlerFunc: plugin.PluginUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/plugin", Method: "DELETE", HandlerFunc: plugin.PluginBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/plugin", Method: "PUT", HandlerFunc: plugin.PluginBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/interfaces", Method: "POST", HandlerFunc: interfaces.InterfaceBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/interfaces", Method: "GET", HandlerFunc: interfaces.InterfaceList},
		&handlerFuncObj{Url: "/interface/:interfaceId", Method: "DELETE", HandlerFunc: interfaces.InterfaceDelete, LogOperation: true},
		&handlerFuncObj{Url: "/interface/:interfaceId", Method: "PUT", HandlerFunc: interfaces.InterfaceUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/interface", Method: "DELETE", HandlerFunc: interfaces.InterfaceBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/interface", Method: "PUT", HandlerFunc: interfaces.InterfaceBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/templates", Method: "POST", HandlerFunc: template.TemplateBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/templates", Method: "GET", HandlerFunc: template.TemplateList},
		&handlerFuncObj{Url: "/template/:templateId", Method: "DELETE", HandlerFunc: template.TemplateDelete, LogOperation: true},
		&handlerFuncObj{Url: "/template/:templateId", Method: "PUT", HandlerFunc: template.TemplateUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/template", Method: "DELETE", HandlerFunc: template.TemplateBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/template", Method: "PUT", HandlerFunc: template.TemplateBatchUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/templates/:pluginId", Method: "GET", HandlerFunc: template.TemplateListByPlugin},

		&handlerFuncObj{Url: "/template_values", Method: "POST", HandlerFunc: template.TemplateValueBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/template_values", Method: "GET", HandlerFunc: template.TemplateValueList},
		&handlerFuncObj{Url: "/template_value/:templateValueId", Method: "DELETE", HandlerFunc: template.TemplateValueDelete, LogOperation: true},
		&handlerFuncObj{Url: "/template_value/:templateValueId", Method: "PUT", HandlerFunc: template.TemplateValueUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/template_value", Method: "DELETE", HandlerFunc: template.TemplateValueBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/template_value", Method: "PUT", HandlerFunc: template.TemplateValueBatchUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/template_values/:parameterId", Method: "GET", HandlerFunc: template.TemplateValueListByParameter},

		&handlerFuncObj{Url: "/parameters", Method: "POST", HandlerFunc: parameter.ParameterBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/parameters", Method: "GET", HandlerFunc: parameter.ParameterList},
		&handlerFuncObj{Url: "/parameter/:parameterId", Method: "DELETE", HandlerFunc: parameter.ParameterDelete, LogOperation: true},
		&handlerFuncObj{Url: "/parameter/:parameterId", Method: "PUT", HandlerFunc: parameter.ParameterUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/parameter", Method: "DELETE", HandlerFunc: parameter.ParameterBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/parameter", Method: "PUT", HandlerFunc: parameter.ParameterBatchUpdate, LogOperation: true},
	)

	// cloud config
	httpHandlerFuncList = append(httpHandlerFuncList,
		&handlerFuncObj{Url: "/providers", Method: "POST", HandlerFunc: provider.ProviderBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/providers", Method: "GET", HandlerFunc: provider.ProviderList},
		&handlerFuncObj{Url: "/provider/:providerId", Method: "DELETE", HandlerFunc: provider.ProviderDelete, LogOperation: true},
		&handlerFuncObj{Url: "/provider/:providerId", Method: "PUT", HandlerFunc: provider.ProviderUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/provider", Method: "DELETE", HandlerFunc: provider.ProviderBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/provider", Method: "PUT", HandlerFunc: provider.ProviderBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/provider_infos", Method: "POST", HandlerFunc: provider.ProviderInfoBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/provider_infos", Method: "GET", HandlerFunc: provider.ProviderInfoList},
		&handlerFuncObj{Url: "/provider_info/:providerInfoId", Method: "DELETE", HandlerFunc: provider.ProviderInfoDelete, LogOperation: true},
		&handlerFuncObj{Url: "/provider_info/:providerInfoId", Method: "PUT", HandlerFunc: provider.ProviderInfoUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/provider_info", Method: "DELETE", HandlerFunc: provider.ProviderInfoBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/provider_info", Method: "PUT", HandlerFunc: provider.ProviderInfoBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/provider_template_values", Method: "POST", HandlerFunc: provider.ProviderTemplateValueBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/provider_template_values", Method: "GET", HandlerFunc: provider.ProviderTemplateValueList},
		&handlerFuncObj{Url: "/provider_template_value/:providerTemplateValueId", Method: "DELETE", HandlerFunc: provider.ProviderTemplateValueDelete, LogOperation: true},
		&handlerFuncObj{Url: "/provider_template_value/:providerTemplateValueId", Method: "PUT", HandlerFunc: provider.ProviderTemplateValueUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/provider_template_value", Method: "DELETE", HandlerFunc: provider.ProviderTemplateValueBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/provider_template_value", Method: "PUT", HandlerFunc: provider.ProviderTemplateValueBatchUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/provider_template_values/:templateName", Method: "GET", HandlerFunc: provider.ProviderTemplateValueListByTemplate},

		&handlerFuncObj{Url: "/sources", Method: "POST", HandlerFunc: source.SourceBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/sources", Method: "GET", HandlerFunc: source.SourceList},
		&handlerFuncObj{Url: "/source/:sourceId", Method: "DELETE", HandlerFunc: source.SourceDelete, LogOperation: true},
		&handlerFuncObj{Url: "/source/:sourceId", Method: "PUT", HandlerFunc: source.SourceUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/source", Method: "DELETE", HandlerFunc: source.SourceBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/source", Method: "PUT", HandlerFunc: source.SourceBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/tf_arguments", Method: "POST", HandlerFunc: tf_argument.TfArgumentBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/tf_arguments", Method: "GET", HandlerFunc: tf_argument.TfArgumentList},
		&handlerFuncObj{Url: "/tf_argument/:tfArgumentId", Method: "DELETE", HandlerFunc: tf_argument.TfArgumentDelete, LogOperation: true},
		&handlerFuncObj{Url: "/tf_argument/:tfArgumentId", Method: "PUT", HandlerFunc: tf_argument.TfArgumentUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/tf_argument", Method: "DELETE", HandlerFunc: tf_argument.TfArgumentBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/tf_argument", Method: "PUT", HandlerFunc: tf_argument.TfArgumentBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/tfstate_attributes", Method: "POST", HandlerFunc: tfstate_attribute.TfstateAttributeBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/tfstate_attributes", Method: "GET", HandlerFunc: tfstate_attribute.TfstateAttributeList},
		&handlerFuncObj{Url: "/tfstate_attribute/:tfstateAttributeId", Method: "DELETE", HandlerFunc: tfstate_attribute.TfstateAttributeDelete, LogOperation: true},
		&handlerFuncObj{Url: "/tfstate_attribute/:tfstateAttributeId", Method: "PUT", HandlerFunc: tfstate_attribute.TfstateAttributeUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/tfstate_attribute", Method: "DELETE", HandlerFunc: tfstate_attribute.TfstateAttributeBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/tfstate_attribute", Method: "PUT", HandlerFunc: tfstate_attribute.TfstateAttributeBatchUpdate, LogOperation: true},
	)

	// resource_data
	httpHandlerFuncList = append(httpHandlerFuncList,
		&handlerFuncObj{Url: "/resource_datas", Method: "POST", HandlerFunc: resource_data.ResourceDataBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/:plugin/:action", Method: "POST", HandlerFunc: resource_data.TerraformOperation, LogOperation: true},
	)
}

func InitHttpServer() {
	urlPrefix := models.UrlPrefix
	r := gin.New()
	if !models.PluginRunningMode {
		// reflect ui resource
		r.LoadHTMLGlob("public/*.html")
		r.Static(fmt.Sprintf("%s/js", urlPrefix), fmt.Sprintf("public%s/js", urlPrefix))
		r.Static(fmt.Sprintf("%s/css", urlPrefix), fmt.Sprintf("public%s/css", urlPrefix))
		r.Static(fmt.Sprintf("%s/img", urlPrefix), fmt.Sprintf("public%s/img", urlPrefix))
		//r.Static(fmt.Sprintf("%s/fonts", urlPrefix), fmt.Sprintf("public%s/fonts", urlPrefix))
		r.GET(fmt.Sprintf("%s/", urlPrefix), func(c *gin.Context) {
			c.HTML(http.StatusOK, "index.html", gin.H{})
		})
		// allow cross request
		if models.Config.HttpServer.Cross {
			crossHandler(r)
		}
	}
	r.Static(fmt.Sprintf("%s/fonts", urlPrefix), fmt.Sprintf("public%s/fonts", urlPrefix))
	// access log
	if models.Config.Log.AccessLogEnable {
		r.Use(httpLogHandle())
	}
	// const handler func
	// r.POST(urlPrefix+"/api/v1/login", permission.Login)
	// register handler func with auth
	authRouter := r.Group(urlPrefix + "/api/v1")
	// authRouter.GET("/refresh-token", permission.RefreshToken)
	for _, funcObj := range httpHandlerFuncList {
		switch funcObj.Method {
		case "GET":
			if funcObj.LogOperation {
				authRouter.GET(funcObj.Url, funcObj.HandlerFunc, log_operation.HandleOperationLog)
			} else {
				authRouter.GET(funcObj.Url, funcObj.HandlerFunc)
			}
			break
		case "POST":
			if funcObj.LogOperation {
				authRouter.POST(funcObj.Url, funcObj.HandlerFunc, log_operation.HandleOperationLog)
			} else {
				authRouter.POST(funcObj.Url, funcObj.HandlerFunc)
			}
			break
		case "PUT":
			if funcObj.LogOperation {
				authRouter.PUT(funcObj.Url, funcObj.HandlerFunc, log_operation.HandleOperationLog)
			} else {
				authRouter.PUT(funcObj.Url, funcObj.HandlerFunc)
			}
			break
		case "DELETE":
			if funcObj.LogOperation {
				authRouter.DELETE(funcObj.Url, funcObj.HandlerFunc, log_operation.HandleOperationLog)
			} else {
				authRouter.DELETE(funcObj.Url, funcObj.HandlerFunc)
			}
			break
		}
	}
	/*
		r.POST(urlPrefix+"/entities/:ciType/query", middleware.AuthToken(), ci.HandleCiModelRequest)
		r.POST(urlPrefix+"/entities/:ciType/create", middleware.AuthCoreRequestToken(), ci.HandleCiModelRequest, ci.HandleOperationLog)
		r.POST(urlPrefix+"/entities/:ciType/update", middleware.AuthCoreRequestToken(), ci.HandleCiModelRequest, ci.HandleOperationLog)
		r.POST(urlPrefix+"/entities/:ciType/delete", middleware.AuthCoreRequestToken(), ci.HandleCiModelRequest, ci.HandleOperationLog)
		r.GET(urlPrefix+"/data-model", middleware.AuthToken(), ci.GetAllDataModel)
		r.POST(urlPrefix+"/plugin/ci-data/operation", middleware.AuthCorePluginToken(), ci.PluginCiDataOperationHandle, ci.HandleOperationLog)
		r.POST(urlPrefix+"/plugin/ci-data/attr-value", middleware.AuthCorePluginToken(), ci.PluginCiDataAttrValueHandle, ci.HandleOperationLog)
	*/
	r.Run(":" + models.Config.HttpServer.Port)
}

func crossHandler(r *gin.Engine) {
	r.Use(func(c *gin.Context) {
		if c.GetHeader("Origin") != "" {
			c.Header("Access-Control-Allow-Origin", c.GetHeader("Origin"))
		}
	})
}

func httpLogHandle() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		bodyBytes, _ := ioutil.ReadAll(c.Request.Body)
		c.Request.Body.Close()
		c.Request.Body = ioutil.NopCloser(bytes.NewReader(bodyBytes))
		c.Set("requestBody", string(bodyBytes))
		c.Next()
		log.AccessLogger.Info("request", log.String("url", c.Request.RequestURI), log.String("method", c.Request.Method), log.Int("code", c.Writer.Status()), log.String("operator", c.GetString("user")), log.String("ip", middleware.GetRemoteIp(c)), log.Float64("cost_ms", time.Now().Sub(start).Seconds()*1000), log.String("body", string(bodyBytes)))
	}
}
