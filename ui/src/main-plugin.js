/*
 * @Author: wanghao7717 792974788@qq.com
 * @Date: 2025-02-08 19:50:40
 * @LastEditors: wanghao7717 792974788@qq.com
 * @LastEditTime: 2025-07-03 14:58:32
 * @FilePath: \wecube-plugins-terraform\ui\src\main-plugin.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import 'regenerator-runtime/runtime'
import router from './router-plugin'
// import 'view-design/dist/styles/iview.css'
import enUS from '@/locale/i18n/en-US.json'
import zhCN from '@/locale/i18n/zh-CN.json'
// import './locale/i18n'
import './styles/index.less'

window.locale('zh-CN', zhCN)
window.locale('en-US', enUS)
const implicitRoute = {
  'terraformIndex/pluginDefinition': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '插件定义', 'en-US': 'Plugin Definition' }
  },
  'terraformIndex/provider': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '云厂商', 'en-US': 'Provider' }
  },
  'terraformIndex/instanceData': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '实例数据', 'en-US': 'Instance Data' }
  },
  'terraformIndex/templateData': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '模板数据', 'en-US': 'Template Data' }
  },
  'terraformIndex/conversionConfiguration': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '转换配置', 'en-US': 'Conversion Configuration' }
  },
  'terraformIndex/providerInfo': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '认证信息', 'en-US': 'Provider Info' }
  },
  'terraformIndex/importAndExport': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '导入&导出', 'en-US': 'Import And Export' }
  },
  'debuggerIndex/debuggerData': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '调试数据', 'en-US': 'Debugger Data' }
  },
  'debuggerIndex/debuggerRequest': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '调试请求', 'en-US': 'Debugger Request' }
  }
}
window.addImplicitRoute(implicitRoute)
window.addRoutes && window.addRoutes(router, 'terraform')
