package models

type InterfaceTable struct {
	Id          string `json:"id" xorm:"id"`
	Name        string `json:"name" xorm:"name"`
	Plugin      string `json:"plugin" xorm:"plugin"`
	Description string `json:"description" xorm:"description"`
	CreateTime  string `json:"createTime" xorm:"create_time"`
	CreateUser  string `json:"createUser" xorm:"create_user"`
	UpdateTime  string `json:"updateTime" xorm:"update_time"`
	UpdateUser  string `json:"updateUser" xorm:"update_user"`
}
