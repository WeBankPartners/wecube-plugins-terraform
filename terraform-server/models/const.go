package models

const (
	DateTimeFormat      = "2006-01-02 15:04:05"
	SysTableIdConnector = "__"
	UrlPrefix           = "/weterraform"
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
	TerraformOutPutPrefix  = "$_result_list$"
	ParameterSourceDefault = "custom"
)

var (
	SEPERATOR  = string([]byte{0x01})
	ConvertWay = map[string]string{"Data": "data", "Template": "template", "ContextData": "context_data", "Attr": "attribute", "Direct": "direct", "Function": "function"}
	TerraformProviderPathDiffMap = map[string]string{"tencentcloud": ".terraform/providers/registry.terraform.io/tencentcloudstack/tencentcloud/",
													 "alicloud": ".terraform/providers/registry.terraform.io/hashicorp/alicloud/"}
	FunctionConvertFunctionDefineName = map[string]string{"Split": "split", "Replace": "replace", "Regx": "regx"}
)
