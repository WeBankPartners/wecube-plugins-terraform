import Vue from 'vue'
import VueI18n from 'vue-i18n'

import zh from 'view-design/dist/locale/zh-CN'
import en from 'view-design/dist/locale/en-US'

import ZH from './zh-CN.json'
import EN from './en-US.json'

Vue.use(VueI18n)

const i18n = new VueI18n({
  locale: 'zh-CN',
  messages: {
    'zh-CN': {
      ...zh,
      ...ZH
    },
    'en-US': {
      ...en,
      ...EN
    }
  }
})

export default i18n
