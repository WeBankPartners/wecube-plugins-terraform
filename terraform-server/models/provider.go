package models

type ProviderTable struct {
	Id                     string `json:"id" xorm:"id"`
	Name                   string `json:"name" xorm:"name"`
	Version                string `json:"version" xorm:"version"`
	SecretIdAttrName       string `json:"secretIdAttrName" xorm:"secret_id_attr_name"`
	SecretKeyAttrName      string `json:"secretKeyAttrName" xorm:"secret_key_attr_name"`
	RegionAttrName         string `json:"regionAttrName" xorm:"region_attr_name"`
	ClientIdAttrName       string `json:"clientIdAttrName" xorm:"client_id_attr_name"`
	ClientSecretAttrName   string `json:"clientSecretAttrName" xorm:"client_secret_attr_name"`
	TenantIdAttrName       string `json:"tenantIdAttrName" xorm:"tenant_id_attr_name"`
	SubscriptionIdAttrName string `json:"subscriptionIdAttrName" xorm:"subscription_id_attr_name"`
	CreateTime             string `json:"createTime" xorm:"create_time"`
	CreateUser             string `json:"createUser" xorm:"create_user"`
	UpdateTime             string `json:"updateTime" xorm:"update_time"`
	UpdateUser             string `json:"updateUser" xorm:"update_user"`
	Initialized            string `json:"initialized" xorm:"Initialized"`
	NameSpace              string `json:"nameSpace" xorm:"name_space"`
}

type ProviderPluginImportObj struct {
	Provider              []*ProviderTable              `json:"provider"`
	ProviderTemplateValue []*ProviderTemplateValueTable `json:"provider_template_value"`
	Template              []*TemplateTable              `json:"template"`
	TemplateValue         []*TemplateValueTable         `json:"template_value"`
	Plugin                []*PluginTable                `json:"plugin"`
	Interface             []*InterfaceTable             `json:"interface"`
	Parameter             []*ParameterTable             `json:"parameter"`
	Source                []*SourceTable                `json:"source"`
	TfArgument            []*TfArgumentTable            `json:"tf_argument"`
	TfstateAttribute      []*TfstateAttributeTable      `json:"tfstate_attribute"`
}
