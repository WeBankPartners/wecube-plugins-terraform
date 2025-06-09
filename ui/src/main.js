/*
 * @Author: wanghao7717 792974788@qq.com
 * @Date: 2025-02-08 19:50:40
 * @LastEditors: wanghao7717 792974788@qq.com
 * @LastEditTime: 2025-06-09 15:52:02
 * @FilePath: \wecube-plugins-terraform\ui\src\main.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import 'regenerator-runtime/runtime'
import ViewUI from 'view-design'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
// import 'view-design/dist/styles/iview.css'
import locale from 'view-design/dist/locale/en-US'
import VueI18n from 'vue-i18n'
import './locale/i18n'
import './styles/index.less'

Vue.config.productionTip = false

Vue.use(ViewUI, {
  transfer: true,
  size: 'default',
  VueI18n,
  locale
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
