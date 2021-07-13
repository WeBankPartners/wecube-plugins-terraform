package models

type ProviderTable struct {
	Id                string `json:"id" xorm:"id"`
	Name              string `json:"name" xorm:"name"`
	Version           string `json:"version" xorm:"version"`
	SecretIdAttrName  string `json:"secretIdAttrName" xorm:"secret_id_attr_name"`
	SecretKeyAttrName string `json:"secretKeyAttrName" xorm:"secret_key_attr_name"`
	RegionAttrName    string `json:"regionAttrName" xorm:"region_attr_name"`
	CreateTime        string `json:"createTime" xorm:"create_time"`
	CreateUser        string `json:"createUser" xorm:"create_user"`
	UpdateTime        string `json:"updateTime" xorm:"update_time"`
	UpdateUser        string `json:"updateUser" xorm:"update_user"`
}
