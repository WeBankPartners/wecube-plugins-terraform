# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import copy
from xml.dom import minidom
from lib.logs import logger
from core.controller import BackendController
from apps.api.configer.resource import ResourceObject
from apps.controller.configer.defines import xml_register

template = '''
	<!-- 1.依赖分析 - 描述运行本插件包需要的其他插件包 -->
	<packageDependencies>
		<packageDependency name="platform" version="v2.7.0" />
	</packageDependencies>
 	
	<!-- 2.菜单注入 - 描述运行本插件包需要注入的菜单 -->
	<menus>
		<menu code='ADMIN_TERRAFORM_CONFIG' cat='ADMIN' displayName="Terraform" localDisplayName="Terraform配置管理">/terraformIndex</menu>
	</menus>
 	
	<!-- 3.数据模型 - 描述本插件包的数据模型,并且描述和Framework数据模型的关系 -->
	<dataModel>
	</dataModel>
 	
	<!-- 4.系统参数 - 描述运行本插件包需要的系统参数 -->
	<systemParameters>
		<systemParameter name="TERRAFORM_PROVIDER_PATH" scopeType="plugins" defaultValue=""/>
	</systemParameters>
 	
	<!-- 5.权限设定 -->
	<authorities>
		<authority systemRoleName="SUPER_ADMIN" >
			<menu code="ADMIN_TERRAFORM_CONFIG" />
		</authority>
	</authorities>
 	
	<!-- 6.运行资源 - 描述部署运行本插件包需要的基础资源(如主机、虚拟机、容器、数据库等) -->
	<resourceDependencies>
		<docker imageName="{{IMAGENAME}}" containerName="{{CONTAINERNAME}}"
        portBindings="{{ALLOCATE_PORT}}:8999"
        volumeBindings="{{BASE_MOUNT_PATH}}/certs:/data,/etc/localtime:/etc/localtime,{{BASE_MOUNT_PATH}}/terraform/logs:/app/wecube_plugins_terraform/logs,{{BASE_MOUNT_PATH}}/terraform/terraform:/app/wecube_plugins_terraform/terraform"
        envVariables="MYSQL_USERNAME={{DB_USER}},MYSQL_PASSWORD={{DB_PWD}},MYSQL_HOST={{DB_HOST}},MYSQL_PORT={{DB_PORT}},MYSQL_DATABASE={{DB_SCHEMA}},JWT_SIGNING_KEY={{JWT_SIGNING_KEY}},ENCRYPT_SEED={{ENCRYPT_SEED}}"/>
		<mysql schema="terraform" initFileName="init.sql"/>
	</resourceDependencies>
 	
	<!-- 7.插件列表 - 描述插件包中单个插件的输入和输出 -->
'''


def fetch_columns(provider, defines):
    result = []
    if not defines:
        return result

    for key, define in defines.items():
        if isinstance(define, basestring):
            _t = {key: "[%s N]" % provider}
            result.append(_t)
        else:
            try:
                if define.get("define"):
                    if define.get("convert"):
                        x = "N" if int(define.get("allow_null", "1")) else "Y"
                        _t = {key: "[%s %s]" % (provider, x)}
                        result.append(_t)
                    result += fetch_columns(provider=provider, defines=define.get("define"))
                else:
                    x = "N" if int(define.get("allow_null", "1")) else "Y"
                    _t = {key: "[%s %s]" % (provider, x)}
                    result.append(_t)
            except Exception, e:
                raise e


    return result


class ResBase(object):
    def resource_objets(self, name):
        _, datas = ResourceObject().list(filters={"resource_type": name})
        return datas

    def zip_columns(self, defines):
        result = {}
        for define in defines:
            key = define.keys()[0]
            if key in result.keys():
                result[key] = result[key] + "," + define[key]
            else:
                result[key] = define[key]

        return result

    def revert_common_columns(self, sys_define, defines):
        res = {}
        for s_define in sys_define:
            x_desc = defines.get(s_define) or ""
            if x_desc:
                x_desc = "," + str(x_desc)
            res[s_define] = "common" + x_desc

        defines.update(res)
        return defines

    def register_resource_infos(self, datas):
        x_columns = []
        x_output = []
        for data in datas:
            try:
                x_columns += fetch_columns(provider=data.get("provider"), defines=data.get("resource_property"))
                x_output += fetch_columns(provider=data.get("provider"), defines=data.get("resource_output"))
            except Exception, e:
                raise e

        columns = self.zip_columns(x_columns)
        output = self.zip_columns(x_output)

        return columns, output

    def _upgrade_apply_info(self, datas, inputkeys, outputkey):
        inputkeys = inputkeys + ["id", "asset_id"]
        inputkeys = list(set(inputkeys))
        outputkey = outputkey + ["id", "asset_id"]
        outputkey = list(set(outputkey))

        x_input, x_output = self.register_resource_infos(datas)
        inputkeys = self.revert_common_columns(inputkeys, x_input)
        outputkey = self.revert_common_columns(outputkey, x_output)
        return inputkeys, outputkey

    def upgrade_apply_info(self, name, define):
        datas = self.resource_objets(name)
        inputkeys, outputkey = self._upgrade_apply_info(datas,
                                                        inputkeys=define.get("inputParameters"),
                                                        outputkey=define.get("outputParameters"))


        p = []
        for data in datas:
            p.append(data["provider"])

        define["inputParameters"] = inputkeys
        define["outputParameters"] = outputkey
        define["provider"] = ",".join(p)

        return define

    def register_source_infos(self, datas):
        x_columns = []
        x_output = []
        for data in datas:
            x_columns += fetch_columns(provider=data.get("provider"), defines=data.get("data_source"))

            x_output += fetch_columns(provider=data.get("provider"), defines=data.get("data_source_output"))

        columns = self.zip_columns(x_columns)
        output = self.zip_columns(x_output)
        return columns, output

    def _upgrade_query_info(self, datas, inputkeys, outputkey):
        inputkeys = inputkeys + ["id", "asset_id"]
        inputkeys = list(set(inputkeys))
        outputkey = outputkey + ["id", "asset_id"]
        outputkey = list(set(outputkey))

        x_input, x_output = self.register_source_infos(datas)
        inputkeys = self.revert_common_columns(inputkeys, x_input)  #list(set(inputkeys + x_input))
        outputkey = self.revert_common_columns(outputkey, x_output)  #list(set(outputkey + x_output))
        return inputkeys, outputkey

    def upgrade_query_info(self, name, define):
        datas = self.resource_objets(name)
        inputkeys, outputkey = self._upgrade_query_info(datas,
                                                        inputkeys=define.get("inputParameters"),
                                                        outputkey=define.get("outputParameters"))

        define["inputParameters"] = inputkeys
        define["outputParameters"] = outputkey

        p = []
        for data in datas:
            p.append(data["provider"])
        define["provider"] = ",".join(p)

        return define

    def plugin_tag(self, name):
        return '<plugin name="%s">' % name

    def interface(self, action, path, method, description):
        description = description or "common"
        return '<interface action="%s" path="%s" httpMethod="%s" description="%s">' % (
            action, path, method, description)

    def inputparameter(self, notnull, columns):
        result = ''
        x_columns = columns if isinstance(columns, list) else columns.keys()

        for key in x_columns:
            description = "common" if isinstance(columns, list) else columns.get(key)

            if key == "password":
                x = '<parameter datatype="string" mappingType="entity" required="N" sensitiveData="Y" description="%s">password</parameter>' % description
            else:
                if key in notnull:
                    x = '<parameter datatype="string" mappingType="entity" required="Y" description="%s">%s</parameter>' % (
                        description, key)
                else:
                    x = '<parameter datatype="string" mappingType="entity" required="N" description="%s">%s</parameter>' % (
                        description, key)

            result += x

        x_result = "<inputParameters>%s</inputParameters>" % result
        return x_result

    def outputparameter(self, columns):
        result = ''
        x_columns = columns if isinstance(columns, list) else columns.keys()

        for key in x_columns:
            description = "common" if isinstance(columns, list) else columns.get(key)
            if key == "password":
                x = '<parameter datatype="string" sensitiveData="Y" description="%s">password</parameter>' % description
            else:
                x = '<parameter datatype="string" description="%s">%s</parameter>' % (description, key)

            result += x

        x_result = "<outputParameters>%s</outputParameters>" % result
        return x_result

    def format_plugin_interface(self, name, defines):
        result = ''
        for key, define in defines.items():
            if key not in ["region", "az"]:
                if key == "apply":
                    define = self.upgrade_apply_info(name, define)
                elif key == "query":
                    define = self.upgrade_query_info(name, define)
            interface_str = self.interface(action=key, path=define.get("path"),
                                           method=define.get("method"), description=define.get("provider", "common"))
            input_str = self.inputparameter(notnull=define.get("notnull"), columns=define.get("inputParameters"))
            out_str = self.outputparameter(columns=define.get("outputParameters"))
            x_result = interface_str + input_str + out_str + "</interface>"

            result += x_result

        return result

    def generate_resource_xml(self):
        '''
        package  -> template -> plugins
        :return:
        '''

        result = ''
        resource_register = copy.deepcopy(xml_register)
        for key, defines in resource_register.items():
            plugin_str = self.plugin_tag(key)
            body_str = self.format_plugin_interface(key, defines)
            x_result = plugin_str + body_str + "</plugin>"
            result += x_result

        result = '''<plugins>%s</plugins>''' % result

        xml_result = '''<package name="terraform" version="{{PLUGIN_VERSION}}">''' + template + result + '''</package>'''
        title = '''<?xml version="1.0" encoding="UTF-8"?>'''

        xml_result = title + xml_result
        # print(xml_result)
        xml_result = xml_result.replace('\n', '').replace('\r', '').replace('\t', '')
        xml_result = minidom.parseString(xml_result.encode('utf-8'))
        return xml_result.toprettyxml(indent='	', encoding='UTF-8')


class ResourceXmlController(BackendController):
    allow_methods = ('GET',)
    resource = None

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        xml_str = ResBase().generate_resource_xml()
        return 1, {"result": xml_str}
