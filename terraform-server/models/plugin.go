package models

type PluginTable struct {
	Id         string `json:"id" xorm:"id"`
	Name       string `json:"name" xorm:"name"`
	CreateTime string `json:"createTime" xorm:"create_time"`
	CreateUser string `json:"createUser" xorm:"create_user"`
	UpdateTime string `json:"updateTime" xorm:"update_time"`
	UpdateUser string `json:"updateUser" xorm:"update_user"`
}
