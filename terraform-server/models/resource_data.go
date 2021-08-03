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

type ResourceDataQuery struct {
	Id              string `json:"id" xorm:"id"`
	Resource        string `json:"resource" xorm:"resource"`
	ResourceTitle   string `json:"resourceTitle" xorm:"resource_title"`
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

type TfstateFileData struct {
	Resources []TfstateFileResources `json:"resources"`
}

type TfstateFileResources struct {
	Instances []TfstateFileAttributes `json:"instances"`
}

type TfstateFileAttributes struct {
	Attributes map[string]interface{} `json:"attributes"`
}

type SortTfstateAttributes struct {
	TfstateAttr *TfstateAttributeTable `json:"tfstateAttr"`
	Point       int                    `json:"point"`
	IsExist     bool                   `json:"isExist"`
}

type FunctionDefine struct {
	Function string              `json:"function"`
	Args     *FunctionDefineArgs `json:"args"`
	Return   string              `json:"return"`
}

type FunctionDefineArgs struct {
	SplitChar  []string            `json:"splitChar"`
	ReplaceVal []map[string]string `json:"replaceVal"`
	RegExp     []string            `json:"regExp"`
	RemoveKey  []string            `json:"keys"`
}

type TfFileAttrFetchResult struct {
	AttrBytes  []byte
	FileContent string
	StartIndex int
	EndIndex   int
}