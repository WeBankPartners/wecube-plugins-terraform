package models

type ParameterTable struct {
	Id         string `json:"id" xorm:"id"`
	Name       string `json:"name" xorm:"name"`
	Type       string `json:"type" xorm:"type"`
	Multiple   string `json:"multiple" xorm:"multiple"`
	Interface  string `json:"interface" xorm:"interface"`
	Template   string `json:"template" xorm:"template"`
	DataType   string `json:"dataType" xorm:"data_type"`
	ObjectName string `json:"objectName" xorm:"object_name"`
	CreateTime string `json:"createTime" xorm:"create_time"`
	CreateUser string `json:"createUser" xorm:"create_user"`
	UpdateTime string `json:"updateTime" xorm:"update_time"`
	UpdateUser string `json:"updateUser" xorm:"update_user"`
}
