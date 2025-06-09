/*
 * @Author: wanghao7717 792974788@qq.com
 * @Date: 2025-02-08 19:50:40
 * @LastEditors: wanghao7717 792974788@qq.com
 * @LastEditTime: 2025-06-09 15:52:18
 * @FilePath: \wecube-plugins-terraform\ui\src\locale\i18n\index.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import Vue from 'vue'
import VueI18n from 'vue-i18n'

import zh from 'view-design/dist/locale/zh-CN'
import en from 'view-design/dist/locale/en-US'

import ZH from './zh-CN.json'
import EN from './en-US.json'

Vue.use(VueI18n)

Vue.locale('zh-CN', Object.assign(zh, ZH))
Vue.locale('en-US', Object.assign(en, EN))

const navLang = navigator.language

const localLang = navLang === 'zh-CN' || navLang === 'en-US' ? navLang : false

const lang = window.localStorage.getItem('lang') || localLang || 'en-US'
Vue.config.lang = lang
