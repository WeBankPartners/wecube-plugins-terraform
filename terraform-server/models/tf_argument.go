package models

type TfArgumentTable struct {
	Id                string `json:"id" xorm:"id"`
	Name              string `json:"name" xorm:"name"`
	Source            string `json:"source" xorm:"source"`
	Parameter         string `json:"parameter" xorm:"parameter"`
	TfstateAttribute  string `json:"tfstateAttribute" xorm:"tfstate_attribute"`
	DefaultValue      string `json:"defaultValue" xorm:"default_value"`
	IsNull            bool   `json:"isNull" xorm:"is_null"`
	Type              string `json:"type" xorm:"type"`
	IsMulti           bool   `json:"isMulti" xorm:"is_multi"`
	ConvertWay        string `json:"convertWay" xorm:"convert_way" binding:"required"`
	RelativeParameter string `json:"relativeParameter" xorm:"relative_parameter"`
	RelativeValue     string `json:"relativeValue" xorm:"relative_value"`
	CreateTime        string `json:"createTime" xorm:"create_time"`
	CreateUser        string `json:"createUser" xorm:"create_user"`
	UpdateTime        string `json:"updateTime" xorm:"update_time"`
	UpdateUser        string `json:"updateUser" xorm:"update_user"`
}
