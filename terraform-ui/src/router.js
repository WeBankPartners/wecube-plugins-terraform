import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
export default new Router({
  routes: [
    {
      path: '/',
      name: '/',
      redirect: '/dangerousIndex/policy',
      component: () => import('@/pages/index'),
      children: [
        {
          path: '/dangerousIndex',
          name: 'dangerousIndex',
          component: () => import('@/pages/dangerous-index'),
          params: {},
          props: true,
          children: [
            {
              path: 'policy',
              name: 'policy',
              title: '策略',
              meta: {},
              component: () => import('@/pages/policy')
            },
            {
              path: 'rule',
              name: 'rule',
              title: '规则',
              meta: {},
              component: () => import('@/pages/rule')
            },
            {
              path: 'subjects',
              name: 'subjects',
              title: '角色',
              meta: {},
              component: () => import('@/pages/subjects')
            },
            {
              path: 'targets',
              name: 'targets',
              title: '目标对象',
              meta: {},
              component: () => import('@/pages/targets')
            },
            {
              path: 'match-params',
              name: 'match-params',
              title: '调用参数',
              meta: {},
              component: () => import('@/pages/match-params')
            },
            {
              path: 'plugin-params',
              name: 'plugin-params',
              title: '插件参数',
              meta: {},
              component: () => import('@/pages/plugin-params')
            },
            {
              path: 'boxes',
              name: 'boxes',
              title: '试盒',
              meta: {},
              component: () => import('@/pages/boxes')
            }
          ]
        }
      ]
    }
  ]
})
