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
            }
          ]
        }
      ]
    }
  ]
})
