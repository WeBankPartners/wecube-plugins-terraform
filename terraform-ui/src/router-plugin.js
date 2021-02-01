import terraformIndex from '@/pages/terraform-index'
import keyconfig from '@/pages/keyconfig'
import resource from '@/pages/resource'
import provider from '@/pages/provider'
import instanceType from '@/pages/instance-type'

const router = [
  {
    path: '/terraformIndex',
    name: 'terraformIndex',
    component: terraformIndex,
    params: {},
    props: true,
    redirect: '/terraformIndex/provider',
    children: [
      {
        path: 'keyconfig',
        name: 'keyconfig',
        title: '策略',
        meta: {},
        component: keyconfig
      },
      {
        path: 'resource',
        name: 'resource',
        title: '资源',
        meta: {},
        component: resource
      },
      {
        path: 'provider',
        name: 'provider',
        title: '云厂商',
        meta: {},
        component: provider
      },
      {
        path: 'instanceType',
        name: 'instanceType',
        title: '资源规格',
        meta: {},
        component: instanceType
      }
    ]
  }
]
export default router
