import terraformIndex from '@/pages/terraform-index'
import conversionConfiguration from '@/pages/conversion-configuration'
import pluginDefinition from '@/pages/plugin-definition'
import templateData from '@/pages/template-data'
import providerInfo from '@/pages/provider-info'
import provider from '@/pages/provider'
import instanceData from '@/pages/instance-data'
import importAndExport from '@/pages/import-export'
import debuggerIndex from '@/pages/debugger/debugger-index'
import debuggerData from '@/pages/debugger/debugger-data'
import debuggerRequest from '@/pages/debugger/debugger-request'
const router = [
  {
    path: '/terraformIndex',
    name: 'terraformIndex',
    component: terraformIndex,
    params: {},
    props: true,
    redirect: 'terraformIndex/pluginDefinition',
    children: [
      {
        path: 'pluginDefinition',
        name: 'pluginDefinition',
        title: '插件定义',
        meta: {},
        component: pluginDefinition
      },
      {
        path: 'templateData',
        name: 'templateData',
        title: '模板数据',
        meta: {},
        component: templateData
      },
      {
        path: 'conversionConfiguration',
        name: 'conversionConfiguration',
        title: '转换配置',
        meta: {},
        component: conversionConfiguration
      },
      {
        path: 'providerInfo',
        name: 'providerInfo',
        title: '认证信息',
        meta: {},
        component: providerInfo
      },
      {
        path: 'provider',
        name: 'provider',
        title: '云厂商',
        meta: {},
        component: provider
      },
      {
        path: 'instanceData',
        name: 'instanceData',
        title: '实例数据',
        meta: {},
        component: instanceData
      },
      {
        path: 'importAndExport',
        name: 'importAndExport',
        title: '导入导出',
        meta: {},
        component: importAndExport
      }
    ]
  },
  {
    path: '/debuggerIndex',
    name: 'debuggerIndex',
    component: debuggerIndex,
    params: {},
    redirect: '/debuggerIndex/debuggerData',
    props: true,
    children: [
      {
        path: 'debuggerData',
        name: 'debuggerData',
        title: '调试数据',
        meta: {},
        component: debuggerData
      },
      {
        path: 'debuggerRequest',
        name: 'debuggerRequest',
        title: '调试请求',
        meta: {},
        component: debuggerRequest
      }
    ]
  }
]
export default router
