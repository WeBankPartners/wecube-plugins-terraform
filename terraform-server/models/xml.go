package models

import "encoding/xml"

type XmlPackage struct {
	XMLName      xml.Name `xml:"package"`
	Name         string   `xml:"name,attr"`
	Version      string   `xml:"version,attr"`
	ParamObjects XmlParamObjects
	Plugins      XmlPlugins
}

type XmlPlugins struct {
	XMLName xml.Name `xml:"plugins"`
	Plugins []*XmlPlugin
}

type XmlPlugin struct {
	XMLName                xml.Name `xml:"plugin"`
	Name                   string   `xml:"name,attr"`
	TargetPackage          string   `xml:"targetPackage,attr"`
	TargetEntity           string   `xml:"targetEntity,attr"`
	RegisterName           string   `xml:"registerName,attr"`
	TargetEntityFilterRule string   `xml:"targetEntityFilterRule,attr"`
	Interfaces             []*XmlInterface
}

type XmlInterface struct {
	XMLName          xml.Name `xml:"interface"`
	Action           string   `xml:"action,attr"`
	Path             string   `xml:"path,attr"`
	FilterRule       string   `xml:"filterRule,attr"`
	InputParameters  XmlInputParameters
	OutputParameters XmlOutputParameters
}

type XmlInputParameters struct {
	XMLName    xml.Name `xml:"inputParameters"`
	Parameters []*XmlParameter
}

type XmlOutputParameters struct {
	XMLName    xml.Name `xml:"outputParameters"`
	Parameters []*XmlParameter
}

type XmlParameter struct {
	XMLName                 xml.Name `xml:"parameter"`
	Datatype                string   `xml:"datatype,attr"`
	Required                string   `xml:"required,attr"`
	SensitiveData           string   `xml:"sensitiveData,attr"`
	MappingType             string   `xml:"mappingType,attr"`
	MappingEntityExpression string   `xml:"mappingEntityExpression,attr,omitempty"`
	Multiple                string   `xml:"multiple,attr"`
	RefObjectName           string   `xml:"refObjectName,attr,omitempty"`
	Value                   string   `xml:",chardata"`
}

type XmlParamObjects struct {
	XMLName      xml.Name `xml:"paramObjects"`
	ParamObjects []*XmlParamObject
}

type XmlParamObject struct {
	XMLName    xml.Name `xml:"paramObject"`
	Name       string   `xml:"name,attr"`
	MapExpr    string   `xml:"mapExpr,attr,omitempty"`
	Properties []*XmlParamProperty
}

type XmlParamProperty struct {
	XMLName       xml.Name `xml:"property"`
	Name          string   `xml:"name,attr"`
	DataType      string   `xml:"dataType,attr"`
	RefObjectName string   `xml:"refObjectName,attr,omitempty"`
	Multiple      string   `xml:"multiple,attr"`
	MapType       string   `xml:"mapType,attr,omitempty"`
	MapExpr       string   `xml:"mapExpr,attr,omitempty"`
	Required      string   `xml:"required,attr"`
	SensitiveData string   `xml:"sensitiveData,attr"`
}
