package models

type ProviderInfoTable struct {
	Id         string `json:"id" xorm:"id"`
	Name       string `json:"name" xorm:"name"`
	Provider   string `json:"provider" xorm:"provider"`
	SecretId   string `json:"secretId" xorm:"secret_id"`
	SecretKey  string `json:"secretKey" xorm:"secret_key"`
	CreateTime string `json:"createTime" xorm:"create_time"`
	CreateUser string `json:"createUser" xorm:"create_user"`
	UpdateTime string `json:"updateTime" xorm:"update_time"`
	UpdateUser string `json:"updateUser" xorm:"update_user"`
}

type ProviderInfoQuery struct {
	Id            string `json:"id" xorm:"id"`
	Name          string `json:"name" xorm:"name"`
	Provider      string `json:"provider" xorm:"provider"`
	ProviderTitle string `json:"providerTitle" xorm:"provider_title"`
	SecretId      string `json:"secretId" xorm:"secret_id"`
	SecretKey     string `json:"secretKey" xorm:"secret_key"`
	CreateTime    string `json:"createTime" xorm:"create_time"`
	CreateUser    string `json:"createUser" xorm:"create_user"`
	UpdateTime    string `json:"updateTime" xorm:"update_time"`
	UpdateUser    string `json:"updateUser" xorm:"update_user"`
}
