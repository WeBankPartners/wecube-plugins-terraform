package models

type ParameterTable struct {
	Id            string `json:"id" xorm:"id"`
	Name          string `json:"name" xorm:"name"`
	Type          string `json:"type" xorm:"type"`
	ReferenceType string `json:"referenceType" xorm:"reference_type"`
	Interface     string `json:"interface" xorm:"interface"`
	Template      string `json:"template" xorm:"template"`
	Value         string `json:"value" xorm:"value"`
	CreateTime    string `json:"createTime" xorm:"create_time"`
	CreateUser    string `json:"createUser" xorm:"create_user"`
	UpdateTime    string `json:"updateTime" xorm:"update_time"`
	UpdateUser    string `json:"updateUser" xorm:"update_user"`
}
