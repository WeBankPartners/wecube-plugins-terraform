# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

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


def fetch_columns(defines):
    result = []
    if not defines:
        return result

    for key, define in defines.items:
        if isinstance(define, basestring):
            result.append(key)
        else:
            if define.get("define"):
                if define.get("convert"):
                    result.append(key)
                result += fetch_columns(defines=define.get("define"))
            else:
                result.append(key)

    return result


class ResBase(object):
    def resource_objets(self, name):
        _, datas = ResourceObject().list(filters={"resource_type": name})
        return datas

    def register_resource_infos(self, datas):
        x_columns = []
        x_output = []
        for data in datas:
            # x_columns += data.get("resource_property").keys()
            # x_columns += data.get("extend_info").keys()
            # x_output += data.get("resource_output").keys()
            x_columns += fetch_columns(defines=data.get("resource_property"))
            x_columns += fetch_columns(data.get("extend_info"))
            x_output += fetch_columns(data.get("resource_output"))

        columns = list(set(x_columns))
        output = list(set(x_output))

        return columns, output

    def _upgrade_apply_info(self, name, inputkeys, outputkey):
        datas = self.resource_objets(name)
        x_input, x_output = self.register_resource_infos(datas)
        inputkeys = list(set(inputkeys + x_input))
        outputkey = list(set(outputkey + x_output))
        return inputkeys, outputkey

    def upgrade_apply_info(self, name, define):
        inputkeys, outputkey = self._upgrade_apply_info(name,
                                                        inputkeys=define.get("inputParameters"),
                                                        outputkey=define.get("outputParameters"))

        define["inputParameters"] = inputkeys
        define["outputParameters"] = outputkey

        return define

    def register_source_infos(self, datas):
        x_columns = []
        x_output = []
        for data in datas:
            # x_columns += data.get("data_source").keys()
            x_columns += fetch_columns(data.get("data_source"))
            # x_output += data.get("data_source_output").keys()
            x_output += fetch_columns(data.get("data_source_output"))
            # data_source_output = data.get("data_source_output")
            # for key, value in data_source_output.items():
            #     if isinstance(value, dict):
            #         if value.get("equivalence"):
            #             x_columns.append(value.get("equivalence"))

        columns = list(set(x_columns))
        output = list(set(x_output))

        return columns, output

    def _upgrade_query_info(self, name, inputkeys, outputkey):
        datas = self.resource_objets(name)
        x_input, x_output = self.register_source_infos(datas)
        inputkeys = list(set(inputkeys + x_input))
        outputkey = list(set(outputkey + x_output))
        return inputkeys, outputkey

    def upgrade_query_info(self, name, define):
        inputkeys, outputkey = self._upgrade_query_info(name,
                                                        inputkeys=define.get("inputParameters"),
                                                        outputkey=define.get("outputParameters"))

        define["inputParameters"] = inputkeys
        define["outputParameters"] = outputkey

        return define

    def plugin_tag(self, name):
        return '<plugin name="%s">' % name

    def interface(self, action, path, method):
        return '<interface action="%s" path="%s" httpMethod="%s">' % (action, path, method)

    def inputparameter(self, notnull, keys):
        result = ''
        for key in keys:
            if key == "password":
                x = '<parameter datatype="string" mappingType="entity" required="N" sensitiveData="Y">password</parameter>'
            else:
                if key in notnull:
                    x = '<parameter datatype="string" mappingType="entity" required="Y">%s</parameter>' % key
                else:
                    x = '<parameter datatype="string" mappingType="entity" required="N">%s</parameter>' % key

            result += x

        x_result = "<inputParameters>%s</inputParameters>" % result
        return x_result

    def outputparameter(self, keys):
        result = ''
        for key in keys:
            if key == "password":
                x = '<parameter datatype="string" sensitiveData="Y">password</parameter>'
            else:
                x = '<parameter datatype="string">%s</parameter>' % key

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
            interface_str = self.interface(action=key, path=define.get("path"), method=define.get("method"))
            input_str = self.inputparameter(notnull=define.get("notnull"), keys=define.get("inputParameters"))
            out_str = self.outputparameter(keys=define.get("outputParameters"))
            x_result = interface_str + input_str + out_str + "</interface>"

            result += x_result

        return result

    def generate_resource_xml(self):
        '''
        package  -> template -> plugins
        :return:
        '''

        result = ''
        for key, defines in xml_register.items():
            plugin_str = self.plugin_tag(key)
            body_str = self.format_plugin_interface(key, defines)
            x_result = plugin_str + body_str + "</plugin>"
            result += x_result

        result = '''<plugins>%s</plugins>''' % result

        xml_result = '''<package name="terraform" version="{{PLUGIN_VERSION}}">''' + template + result + '''</package>'''
        title = '''<?xml version="1.0" encoding="UTF-8"?>'''

        xml_result = title + xml_result
        xml_result = xml_result.replace('\n', '').replace('\r', '').replace('\t', '')
        xml_result = minidom.parseString(xml_result.encode('utf-8'))
        return xml_result.toprettyxml(indent='	', encoding='UTF-8')


class ResourceXmlController(BackendController):
    allow_methods = ('GET',)
    resource = None

    def list(self, request, data, orderby=None, page=None, pagesize=None, **kwargs):
        xml_str = ResBase().generate_resource_xml()
        return 1, {"result": xml_str}
