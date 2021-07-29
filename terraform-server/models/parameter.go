package models

type ParameterTable struct {
	Id         string `json:"id" xorm:"id"`
	Name       string `json:"name" xorm:"name"`
	Type       string `json:"type" xorm:"type"`
	Multiple   string `json:"multiple" xorm:"multiple"`
	Interface  string `json:"interface" xorm:"interface"`
	Template   string `json:"template" xorm:"template"`
	DataType   string `json:"dataType" xorm:"datatype"`
	ObjectName string `json:"objectName" xorm:"object_name"`
	Source     string `json:"source" xorm:"source"`
	CreateTime string `json:"createTime" xorm:"create_time"`
	CreateUser string `json:"createUser" xorm:"create_user"`
	UpdateTime string `json:"updateTime" xorm:"update_time"`
	UpdateUser string `json:"updateUser" xorm:"update_user"`
	Nullable   string `json:"nullable" xorm:"nullable"`
	Sensitive  string `json:"sensitive" xorm:"sensitive"`
}

type ParameterQuery struct {
	Id              string `json:"id" xorm:"id"`
	Name            string `json:"name" xorm:"name"`
	Type            string `json:"type" xorm:"type"`
	Multiple        string `json:"multiple" xorm:"multiple"`
	Interface       string `json:"interface" xorm:"interface"`
	Template        string `json:"template" xorm:"template"`
	DataType        string `json:"dataType" xorm:"datatype"`
	ObjectName      string `json:"objectName" xorm:"object_name"`
	ObjectNameTitle string `json:"objectNameTitle" xorm:"object_name_title"`
	Source          string `json:"source" xorm:"source"`
	CreateTime      string `json:"createTime" xorm:"create_time"`
	CreateUser      string `json:"createUser" xorm:"create_user"`
	UpdateTime      string `json:"updateTime" xorm:"update_time"`
	UpdateUser      string `json:"updateUser" xorm:"update_user"`
}
