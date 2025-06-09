import 'regenerator-runtime/runtime'
import ViewUI from 'view-design'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './locale/i18n'
import './styles/index.less'

Vue.config.productionTip = false

Vue.use(ViewUI)

new Vue({
  router,
  i18n,
  render: h => h(App)
}).$mount('#app')
