import 'regenerator-runtime/runtime'
import router from './router-plugin'
import 'view-design/dist/styles/iview.css'
import './locale/i18n'
import { validate } from '@/assets/js/validate.js'
import { commonUtil } from '@/pages/util/common-util.js'
import '@/assets/css/local.bootstrap.css'
import 'bootstrap/dist/js/bootstrap.min.js'
import 'font-awesome/css/font-awesome.css'
import jquery from 'jquery'
import zhCN from '@/locale/i18n/zh-CN.json'
import enUS from '@/locale/i18n/en-US.json'

import TerraformPageTable from '@/pages/components/table-page/page'
import TfModalComponent from '@/pages/components/modal'

window.addOptions({
  JQ: jquery,
  $tfCommonUtil: commonUtil,
  $validate: validate
})

window.component('TerraformPageTable', TerraformPageTable)
window.component('TfModalComponent', TfModalComponent)

window.locale('zh-CN', zhCN)
window.locale('en-US', enUS)
const implicitRoute = {
  'terraformIndex/provider': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '云厂商', 'en-US': 'provider' }
  },
  'terraformIndex/keyconfig': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '策略', 'en-US': 'keyconfig' }
  },
  'terraformIndex/resource': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '资源', 'en-US': 'resource' }
  },
  'terraformIndex/secret': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '云认证', 'en-US': 'secret' }
  },
  'terraformIndex/instanceType': {
    parentBreadcrumb: { 'zh-CN': 'Terraform配置', 'en-US': 'Terraform Config' },
    childBreadcrumb: { 'zh-CN': '实例规格', 'en-US': 'Instance Type' }
  }
}
window.addImplicitRoute(implicitRoute)
window.addRoutes && window.addRoutes(router, 'dangerous')
