package api

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"

	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/middleware"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/interfaces"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/log_operation"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/parameter"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/plugin"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/provider"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/api/v1/resource_data"
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
		&handlerFuncObj{Url: "/plugins", Method: "DELETE", HandlerFunc: plugin.PluginBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/plugins", Method: "PUT", HandlerFunc: plugin.PluginBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/interfaces", Method: "POST", HandlerFunc: interfaces.InterfaceBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/interfaces", Method: "GET", HandlerFunc: interfaces.InterfaceList},
		&handlerFuncObj{Url: "/interfaces", Method: "DELETE", HandlerFunc: interfaces.InterfaceBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/interfaces", Method: "PUT", HandlerFunc: interfaces.InterfaceBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/templates", Method: "POST", HandlerFunc: template.TemplateBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/templates", Method: "GET", HandlerFunc: template.TemplateList},
		&handlerFuncObj{Url: "/templates", Method: "DELETE", HandlerFunc: template.TemplateBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/templates", Method: "PUT", HandlerFunc: template.TemplateBatchUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/templates/:pluginId", Method: "GET", HandlerFunc: template.TemplateListByPlugin},

		&handlerFuncObj{Url: "/template_values", Method: "POST", HandlerFunc: template.TemplateValueBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/template_values", Method: "GET", HandlerFunc: template.TemplateValueList},
		&handlerFuncObj{Url: "/template_values", Method: "DELETE", HandlerFunc: template.TemplateValueBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/template_values", Method: "PUT", HandlerFunc: template.TemplateValueBatchUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/template_values/:parameterId", Method: "GET", HandlerFunc: template.TemplateValueListByParameter},

		&handlerFuncObj{Url: "/parameters", Method: "POST", HandlerFunc: parameter.ParameterBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/parameters", Method: "GET", HandlerFunc: parameter.ParameterList},
		&handlerFuncObj{Url: "/parameters", Method: "DELETE", HandlerFunc: parameter.ParameterBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/parameters", Method: "PUT", HandlerFunc: parameter.ParameterBatchUpdate, LogOperation: true},
	)

	// cloud config
	httpHandlerFuncList = append(httpHandlerFuncList,
		&handlerFuncObj{Url: "/providers", Method: "POST", HandlerFunc: provider.ProviderBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/providers", Method: "GET", HandlerFunc: provider.ProviderList},
		&handlerFuncObj{Url: "/providers", Method: "DELETE", HandlerFunc: provider.ProviderBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/providers", Method: "PUT", HandlerFunc: provider.ProviderBatchUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/providers/download", Method: "POST", HandlerFunc: provider.ProviderDownload, LogOperation: false},
		&handlerFuncObj{Url: "/providers/upload", Method: "POST", HandlerFunc: provider.ProviderUpload, LogOperation: false},

		&handlerFuncObj{Url: "/provider_infos", Method: "POST", HandlerFunc: provider.ProviderInfoBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/provider_infos", Method: "GET", HandlerFunc: provider.ProviderInfoList},
		&handlerFuncObj{Url: "/provider_infos", Method: "DELETE", HandlerFunc: provider.ProviderInfoBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/provider_infos", Method: "PUT", HandlerFunc: provider.ProviderInfoBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/provider_template_values", Method: "POST", HandlerFunc: provider.ProviderTemplateValueBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/provider_template_values", Method: "GET", HandlerFunc: provider.ProviderTemplateValueList},
		&handlerFuncObj{Url: "/provider_template_values", Method: "DELETE", HandlerFunc: provider.ProviderTemplateValueBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/provider_template_values", Method: "PUT", HandlerFunc: provider.ProviderTemplateValueBatchUpdate, LogOperation: true},
		&handlerFuncObj{Url: "/provider_template_values/:templateId", Method: "GET", HandlerFunc: provider.ProviderTemplateValueListByTemplate},

		&handlerFuncObj{Url: "/sources", Method: "POST", HandlerFunc: source.SourceBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/sources", Method: "GET", HandlerFunc: source.SourceList},
		&handlerFuncObj{Url: "/sources", Method: "DELETE", HandlerFunc: source.SourceBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/sources", Method: "PUT", HandlerFunc: source.SourceBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/tf_arguments", Method: "POST", HandlerFunc: tf_argument.TfArgumentBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/tf_arguments", Method: "GET", HandlerFunc: tf_argument.TfArgumentList},
		&handlerFuncObj{Url: "/tf_arguments", Method: "DELETE", HandlerFunc: tf_argument.TfArgumentBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/tf_arguments", Method: "PUT", HandlerFunc: tf_argument.TfArgumentBatchUpdate, LogOperation: true},

		&handlerFuncObj{Url: "/tfstate_attributes", Method: "POST", HandlerFunc: tfstate_attribute.TfstateAttributeBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/tfstate_attributes", Method: "GET", HandlerFunc: tfstate_attribute.TfstateAttributeList},
		&handlerFuncObj{Url: "/tfstate_attributes", Method: "DELETE", HandlerFunc: tfstate_attribute.TfstateAttributeBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/tfstate_attributes", Method: "PUT", HandlerFunc: tfstate_attribute.TfstateAttributeBatchUpdate, LogOperation: true},
	)

	// resource_data
	httpHandlerFuncList = append(httpHandlerFuncList,
		&handlerFuncObj{Url: "/resource_datas", Method: "POST", HandlerFunc: resource_data.ResourceDataBatchCreate, LogOperation: true},
		&handlerFuncObj{Url: "/resource_datas", Method: "GET", HandlerFunc: resource_data.ResourceDataList},
		&handlerFuncObj{Url: "/resource_datas", Method: "DELETE", HandlerFunc: resource_data.ResourceDataBatchDelete, LogOperation: true},
		&handlerFuncObj{Url: "/resource_datas", Method: "PUT", HandlerFunc: resource_data.ResourceDataBatchUpdate, LogOperation: true},

		// for resource_data_debug
		&handlerFuncObj{Url: "/resource_data_debugs", Method: "GET", HandlerFunc: resource_data.ResourceDataDebugList},
		&handlerFuncObj{Url: "/terraform_debug/:plugin/:action", Method: "POST", HandlerFunc: resource_data.TerraformOperationDebug, LogOperation: true},

		// &handlerFuncObj{Url: "/terraform/:plugin/:action", Method: "POST", HandlerFunc: resource_data.TerraformOperation, LogOperation: true},
	)

	// export and import
	httpHandlerFuncList = append(httpHandlerFuncList,
		&handlerFuncObj{Url: "/provider_plugin_config/export", Method: "GET", HandlerFunc: provider.ProviderPluginExport, LogOperation: true},
		&handlerFuncObj{Url: "/provider_plugin_config/import", Method: "POST", HandlerFunc: provider.ProviderPluginImport, LogOperation: false},
		&handlerFuncObj{Url: "/plugin_xml/export", Method: "GET", HandlerFunc: plugin.PluginXmlExport, LogOperation: true},
	)
}

func InitHttpServer() {
	urlPrefix := models.UrlPrefix
	r := gin.New()
	if !models.PluginRunningMode {
		// reflect ui resource
		r.LoadHTMLGlob("public/*.html")
		r.Static(fmt.Sprintf("%s/js", urlPrefix), "public/js")
		r.Static(fmt.Sprintf("%s/css", urlPrefix), "public/css")
		r.Static(fmt.Sprintf("%s/img", urlPrefix), "public/img")
		r.Static(fmt.Sprintf("%s/fonts", urlPrefix), "public/fonts")
		r.GET(fmt.Sprintf("%s/", urlPrefix), func(c *gin.Context) {
			c.HTML(http.StatusOK, "index.html", gin.H{})
		})
		// allow cross request
		if models.Config.HttpServer.Cross {
			crossHandler(r)
		}
	}
	// access log
	if models.Config.Log.AccessLogEnable {
		r.Use(httpLogHandle())
	}
	// const handler func
	// r.POST(urlPrefix+"/api/v1/login", permission.Login)
	// register handler func with auth
	authRouter := r.Group(urlPrefix+"/api/v1", middleware.AuthCoreRequestToken())
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
	// r.POST(urlPrefix + "/api/v1/:plugin/:action", middleware.AuthCoreRequestToken(), resource_data.TerraformOperation, log_operation.HandleOperationLog)
	r.POST(urlPrefix+"/api/v1/terraform/:plugin/:action", middleware.AuthCoreRequestToken(), resource_data.TerraformOperation, log_operation.HandleOperationLog)
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
