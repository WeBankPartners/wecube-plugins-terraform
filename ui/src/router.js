import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
export default new Router({
  routes: [
    {
      path: '/',
      name: '/',
      redirect: '/terraformIndex/templateData',
      component: () => import('@/pages/index'),
      children: [
        {
          path: '/terraformIndex',
          name: 'terraformIndex',
          component: () => import('@/pages/terraform-index'),
          params: {},
          props: true,
          children: [
            {
              path: 'conversionConfiguration',
              name: 'conversionConfiguration',
              title: '转化配置',
              meta: {},
              component: () => import('@/pages/conversion-configuration')
            },
            {
              path: 'pluginDefinition',
              name: 'pluginDefinition',
              title: '插件定义',
              meta: {},
              component: () => import('@/pages/plugin-definition')
            },
            {
              path: 'templateData',
              name: 'templateData',
              title: '模板数据',
              meta: {},
              component: () => import('@/pages/template-data')
            },
            {
              path: 'providerInfo',
              name: 'providerInfo',
              title: '认证信息',
              meta: {},
              component: () => import('@/pages/provider-info')
            },
            {
              path: 'provider',
              name: 'provider',
              title: '云厂商',
              meta: {},
              component: () => import('@/pages/provider')
            },
            {
              path: 'importAndExport',
              name: 'importAndExport',
              title: '导入导出',
              meta: {},
              component: () => import('@/pages/import-export')
            }
          ]
        },
        {
          path: '/debuggerIndex',
          name: 'debuggerIndex',
          component: () => import('@/pages/debugger/debugger-index'),
          params: {},
          redirect: '/debuggerIndex/debuggerData',
          props: true,
          children: [
            {
              path: 'debuggerData',
              name: 'debuggerData',
              title: '调试数据',
              meta: {},
              component: () => import('@/pages/debugger/debugger-data')
            },
            {
              path: 'debuggerRequest',
              name: 'debuggerRequest',
              title: '调试请求',
              meta: {},
              component: () => import('@/pages/debugger/debugger-request')
            }
          ]
        }
      ]
    }
  ]
})
