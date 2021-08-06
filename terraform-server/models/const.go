package models

const (
	DateTimeFormat      = "2006-01-02 15:04:05"
	SysTableIdConnector = "__"
	UrlPrefix           = "/terraform"
	MultiRefType        = "multiRef"
	AutofillRuleType    = "autofillRule"
	ObjectInputType     = "object"
	AutofillSuggest     = "suggest#"
	SystemUser          = "system"
	AdminUser           = "admin"
	AdminRole           = "SUPER_ADMIN"
	SystemRole          = "SUB_SYSTEM"
	PlatformUser        = "SYS_PLATFORM"
	PasswordDisplay     = "****"
	BashCmd             = "/bin/sh"
	RandomFlag          = "{random}"
	TerraformOutPutPrefix  = "$_result_list$"
	ParameterSourceDefault = "custom"
	TfArgumentKeyArgumentDefault = "N"
	CommandTimeOut      = 600
	ResourceDataDebug   = "$_resource_data_debug$"
	ResourceIdDataConvert  = "#resourceId#"
	PGuid               = "6101d5ff9c058ecd8d2dddd974d38f98"
	ImportResourceDataTableId = "$_resource_data_table_id$"
	SimulateResourceData = "$_simulate_resource_data$"
	SimulateResourceDataReturn = "$_simulate_resource_data_return$"
	SimulateResourceDataResult = "$_simulate_resource_data_result$"
	SourceDataIdx        = "$_source_data_idx$"
)

var (
	SEPERATOR  = string([]byte{0x01})
	ConvertWay = map[string]string{"Data": "data", "Template": "template", "ContextData": "context_data", "Attr": "attribute", "Direct": "direct", "Function": "function", "ContextDirect": "context_direct", "ContextAttr": "context_attribute", "ContextTemplate": "context_template"}
	// TerraformProviderPathDiffMap = map[string]string{"tencentcloud": ".terraform/providers/registry.terraform.io/tencentcloudstack/tencentcloud/",
	// 												 "alicloud": ".terraform/providers/registry.terraform.io/hashicorp/alicloud/"}
	TerraformProviderPathDiffMap = map[string]string{"tencentcloud": ".terraform/providers/registry.terraform.io/",
													 "alicloud": ".terraform/providers/registry.terraform.io/"}
	FunctionConvertFunctionDefineName = map[string]string{"Split": "split", "Replace": "replace", "Regx": "regx", "Remove": "remove"}

	ExcludeFilterKeys = map[string]bool{"confirmToken":true, "callbackParameter":true, "id":true, "asset_id":true,
		"provider_info":true, "region_id":true, "operator_user":true, "requestId":true, "requestSn":true,
		SimulateResourceData:true, ResourceDataDebug:true, ResourceIdDataConvert:true, ImportResourceDataTableId: true,
		SimulateResourceDataReturn:true, SimulateResourceDataResult:true, SourceDataIdx:true}
)
