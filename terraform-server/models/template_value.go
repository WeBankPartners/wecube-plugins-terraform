package models

type TemplateValueTable struct {
	Id         string `json:"id" xorm:"id"`
	Value      string `json:"value" xorm:"value"`
	Template   string `json:"template" xorm:"template"`
	CreateTime string `json:"createTime" xorm:"create_time"`
	CreateUser string `json:"createUser" xorm:"create_user"`
	UpdateTime string `json:"updateTime" xorm:"update_time"`
	UpdateUser string `json:"updateUser" xorm:"update_user"`
}

type TemplateValueQuery struct {
	Id         string `json:"id" xorm:"id"`
	Value      string `json:"value" xorm:"value"`
	Template   string `json:"template" xorm:"template"`
	ProviderTemplateValueInfo map[string]map[string]string `json:"providerTemplateValueInfo"`
}

