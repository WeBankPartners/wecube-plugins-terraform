import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
export default new Router({
  routes: [
    {
      path: '/',
      name: '/',
      redirect: '/terraformIndex/keyconfig',
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
              path: 'keyconfig',
              name: 'keyconfig',
              title: '策略',
              meta: {},
              component: () => import('@/pages/keyconfig')
            },
            {
              path: 'resource',
              name: 'resource',
              title: '资源',
              meta: {},
              component: () => import('@/pages/resource')
            },
            {
              path: 'provider',
              name: 'provider',
              title: '云厂商',
              meta: {},
              component: () => import('@/pages/provider')
            },
            {
              path: 'instanceType',
              name: 'instanceType',
              title: '资源规格',
              meta: {},
              component: () => import('@/pages/instance-type')
            }
          ]
        }
      ]
    }
  ]
})
