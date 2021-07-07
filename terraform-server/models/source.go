package models

type SourceTable struct {
	Id                       string `json:"id" xorm:"id"`
	Name                     string `json:"name" xorm:"name"`
	Plugin                   string `json:"plugin" xorm:"plugin"`
	Provider                 string `json:"provider" xorm:"provider"`
	ResourceAssetIdAttribute string `json:"resourceAssetIdAttribute" xorm:"resource_asset_id_attribute"`
	Action                   string `json:"action" xorm:"action"`
	CreateTime               string `json:"createTime" xorm:"create_time"`
	CreateUser               string `json:"createUser" xorm:"create_user"`
	UpdateTime               string `json:"updateTime" xorm:"update_time"`
	UpdateUser               string `json:"updateUser" xorm:"update_user"`
}
