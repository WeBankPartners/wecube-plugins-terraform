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
)

var (
	SEPERATOR  = string([]byte{0x01})
	ConvertWay = [...]string{"data", "template", "context", "pipe", "default"}
)
