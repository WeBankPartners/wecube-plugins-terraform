package models

type ResourceDataTable struct {
	Id              string `json:"id" xorm:"id"`
	Resource        string `json:"resource" xorm:"resource"`
	ResourceId      string `json:"resourceId" xorm:"resource_id"`
	ResourceAssetId string `json:"resourceAssetId" xorm:"resource_asset_id"`
	TfFile          string `json:"tfFile" xorm:"tf_file"`
	TfStateFile     string `json:"tfStateFile" xorm:"tf_state_file"`
	RegionId        string `json:"regionId" xorm:"region_id"`
	CreateTime      string `json:"createTime" xorm:"create_time"`
	CreateUser      string `json:"createUser" xorm:"create_user"`
	UpdateTime      string `json:"updateTime" xorm:"update_time"`
	UpdateUser      string `json:"updateUser" xorm:"update_user"`
}

type RegionProviderData struct {
	ProviderName      string `json:"providerName"`
	ProviderVersion   string `json:"providerVersion"`
	SecretId          string `json:"secretId"`
	SecretKey         string `json:"secretKey"`
	SecretIdAttrName  string `json:"secretIdAttrName"`
	SecretKeyAttrName string `json:"secretKeyAttrName"`
	RegionAttrName    string `json:"regionAttrName"`
	ProviderInfoId    string `json:"providerInfoId"`
}