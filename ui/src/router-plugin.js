import terraformIndex from '@/pages/terraform-index'
import conversionConfiguration from '@/pages/conversion-configuration'
import pluginDefinition from '@/pages/plugin-definition'
import templateData from '@/pages/template-data'
import providerInfo from '@/pages/provider-info'
import provider from '@/pages/provider'
import importAndExport from '@/pages/import-export'
const router = [
  {
    path: '/terraformIndex',
    name: 'terraformIndex',
    component: terraformIndex,
    params: {},
    props: true,
    redirect: '/terraformIndex/templateData',
    children: [
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
        path: 'pluginDefinition',
        name: 'pluginDefinition',
        title: '插件定义',
        meta: {},
        component: pluginDefinition
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
        path: 'importAndExport',
        name: 'importAndExport',
        title: '导入导出',
        meta: {},
        component: importAndExport
      }
    ]
  }
]
export default router
