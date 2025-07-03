import 'regenerator-runtime/runtime'
import ViewUI from 'view-design'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
// import 'view-design/dist/styles/iview.css'
import locale from 'view-design/dist/locale/en-US'
import VueI18n from 'vue-i18n'
import i18n from './locale/i18n'
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
  i18n,
  render: h => h(App)
}).$mount('#app')
