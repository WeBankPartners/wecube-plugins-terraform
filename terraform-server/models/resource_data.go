package models

import (
	"encoding/json"
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common/log"
)

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

	ProviderId                string `json:"providerId" xorm:"provider_id"`
	ProviderName              string `json:"providerName" xorm:"provider_name"`
	ProviderVersion           string `json:"providerVersion" xorm:"provider_version"`
	ProviderSecretIdAttrName  string `json:"providerSecretIdAttrName" xorm:"provider_secret_id_attr_name"`
	ProviderSecretKeyAttrName string `json:"providerSecretKeyAttrName" xorm:"provider_secret_key_attr_name"`
	ProviderRegionAttrName    string `json:"providerRegionAttrName" xorm:"provider_region_attr_name"`
	ProviderInitialized       string `json:"providerInitialized" xorm:"provider_initialized"`
	ProviderNamespace         string `json:"providerNamespace" xorm:"provider_namespace"`
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
	AttrBytes   []byte
	FileContent string
	StartIndex  int
	EndIndex    int
}

// ParseTfstateFileData 兼容 resources 为数组或对象，并兼容 instances 为对象或数组
func ParseTfstateFileData(data []byte) (TfstateFileData, error) {
	log.Logger.Debug("[ParseTfstateFileData] input", log.String("data", string(data)))
	var result TfstateFileData
	// 先尝试数组
	type arrType struct {
		Resources []TfstateFileResources `json:"resources"`
	}
	var arr arrType
	if err := json.Unmarshal(data, &arr); err == nil && len(arr.Resources) > 0 {
		for i, res := range arr.Resources {
			if len(res.Instances) == 0 {
				tmp := struct {
					Instances map[string]TfstateFileAttributes `json:"instances"`
				}{}
				b, _ := json.Marshal(res)
				if err2 := json.Unmarshal(b, &tmp); err2 == nil && len(tmp.Instances) > 0 {
					for _, v := range tmp.Instances {
						arr.Resources[i].Instances = append(arr.Resources[i].Instances, v)
					}
				}
			}
		}
		result.Resources = arr.Resources
		log.Logger.Debug("[ParseTfstateFileData] result", log.JsonObj("result", result))
		return result, nil
	}
	// 再尝试对象
	type objType struct {
		Resources map[string]TfstateFileResources `json:"resources"`
	}
	var obj objType
	if err := json.Unmarshal(data, &obj); err == nil && len(obj.Resources) > 0 {
		for _, v := range obj.Resources {
			if len(v.Instances) == 0 {
				tmp := struct {
					Instances map[string]TfstateFileAttributes `json:"instances"`
				}{}
				b, _ := json.Marshal(v)
				if err2 := json.Unmarshal(b, &tmp); err2 == nil && len(tmp.Instances) > 0 {
					for _, vv := range tmp.Instances {
						v.Instances = append(v.Instances, vv)
					}
				}
			}
			result.Resources = append(result.Resources, v)
		}
		log.Logger.Debug("[ParseTfstateFileData] result", log.JsonObj("result", result))
		return result, nil
	}
	// 如果 resources 只有一层，且 instances 为空，但有 attributes，兜底
	if len(result.Resources) == 0 {
		type attrType struct {
			Resources struct {
				Instances struct {
					Attributes map[string]interface{} `json:"attributes"`
				} `json:"instances"`
			} `json:"resources"`
		}
		var at attrType
		if err := json.Unmarshal(data, &at); err == nil && len(at.Resources.Instances.Attributes) > 0 {
			result.Resources = append(result.Resources, TfstateFileResources{
				Instances: []TfstateFileAttributes{
					{Attributes: at.Resources.Instances.Attributes},
				},
			})
			log.Logger.Debug("[ParseTfstateFileData] result", log.JsonObj("result", result))
			return result, nil
		}
	}
	log.Logger.Debug("[ParseTfstateFileData] parse failed", log.String("input", string(data)))
	return result, fmt.Errorf("resources is neither array nor object or is empty")
}
