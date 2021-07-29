package models

type SourceTable struct {
	Id               string `json:"id" xorm:"id"`
	Interface        string `json:"interface" xorm:"interface"`
	Provider         string `json:"provider" xorm:"provider"`
	Name             string `json:"name" xorm:"name"`
	AssetIdAttribute string `json:"assetIdAttribute" xorm:"asset_id_attribute"`
	TerraformUsed    string `json:"terraformUsed" xorm:"terraform_used"`
	CreateTime       string `json:"createTime" xorm:"create_time"`
	CreateUser       string `json:"createUser" xorm:"create_user"`
	UpdateTime       string `json:"updateTime" xorm:"update_time"`
	UpdateUser       string `json:"updateUser" xorm:"update_user"`
	ImportPrefix     string `json:"importPrefix" xorm:"import_prefix"`
	ImportSupport    string `json:"importSupport" xorm:"import_support"`
	ExecutionSeqNo   int    `json:"executionSeqNo" xorm:"execution_seq_no"`
	SourceType       string `json:"sourceType" xorm:"source_type"`
}
