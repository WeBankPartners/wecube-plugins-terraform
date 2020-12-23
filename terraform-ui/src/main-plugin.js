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

import DangerousPageTable from '@/pages/components/table-page/page'
import ModalComponent from '@/pages/components/modal'

window.addOptions({
  JQ: jquery,
  $itsCommonUtil: commonUtil,
  $validate: validate
})

window.component('DangerousPageTable', DangerousPageTable)
window.component('ModalComponent', ModalComponent)

window.locale('zh-CN', zhCN)
window.locale('en-US', enUS)
const implicitRoute = {
  'dangerousIndex/boxes': {
    parentBreadcrumb: { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
    childBreadcrumb: { 'zh-CN': '试盒', 'en-US': 'Boxes' }
  },
  'dangerousIndex/policy': {
    parentBreadcrumb: { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
    childBreadcrumb: { 'zh-CN': '策略', 'en-US': 'Policy' }
  },
  'dangerousIndex/rule': {
    parentBreadcrumb: { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
    childBreadcrumb: { 'zh-CN': '规则', 'en-US': 'Rule' }
  },
  'dangerousIndex/subjects': {
    parentBreadcrumb: { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
    childBreadcrumb: { 'zh-CN': '角色', 'en-US': 'Subjects' }
  },
  'dangerousIndex/targets': {
    parentBreadcrumb: { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
    childBreadcrumb: { 'zh-CN': '目标对象', 'en-US': 'Targets' }
  },
  'dangerousIndex/match-params': {
    parentBreadcrumb: { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
    childBreadcrumb: { 'zh-CN': '调用参数', 'en-US': 'Match Params' }
  },
  'dangerousIndex/plugin-params': {
    parentBreadcrumb: { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
    childBreadcrumb: { 'zh-CN': '插件参数', 'en-US': 'Plugin Params' }
  }
}
window.addImplicitRoute(implicitRoute)
window.addRoutes && window.addRoutes(router, 'dangerous')
