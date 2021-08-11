package models

type ProviderTemplateValueTable struct {
	Id            string `json:"id" xorm:"id"`
	Value         string `json:"value" xorm:"value"`
	Provider      string `json:"provider" xorm:"provider"`
	TemplateValue string `json:"templateValue" xorm:"template_value"`
	CreateTime    string `json:"createTime" xorm:"create_time"`
	CreateUser    string `json:"createUser" xorm:"create_user"`
	UpdateTime    string `json:"updateTime" xorm:"update_time"`
	UpdateUser    string `json:"updateUser" xorm:"update_user"`
}
