import 'regenerator-runtime/runtime'
import router from './router-plugin'
import 'view-design/dist/styles/iview.css'
import './locale/i18n'
import zhCN from '@/locale/i18n/zh-CN.json'
import enUS from '@/locale/i18n/en-US.json'

window.locale('zh-CN', zhCN)
window.locale('en-US', enUS)
const implicitRoute = {
  'terraformIndex/conversionConfiguration': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '转换配置', 'en-US': 'Conversion Configuration' }
  },
  'terraformIndex/pluginDefinition': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '插件定义', 'en-US': 'Plugin Definition' }
  },
  'terraformIndex/templateData': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '模板数据', 'en-US': 'Template Data' }
  }
}
window.addImplicitRoute(implicitRoute)
window.addRoutes && window.addRoutes(router, 'dangerous')
