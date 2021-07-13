<template>
  <div class=" ">
    <!-- 搜索区 -->
    <div>
      <span>{{ $t('t_plugin') }}</span>
      <Select v-model="plugin" clearable filterable @on-clear="clearPlugin" style="width:300px">
        <Option v-for="item in pluginOptions" :value="item.id" :key="item.id">{{ item.name }}</Option>
      </Select>
      <Button type="primary" @click="getTemplates" :disabled="!plugin">{{ $t('t_search') }}</Button>
    </div>
    <!-- 配置区 -->
    <div
      v-if="showOperateZone"
      :style="{ 'margin-top': '36px', 'max-height': pageHeight + 'px', overflow: 'auto', 'text-align': 'center' }"
    >
      <!-- 表头 -->
      <div style="font-size: 0">
        <div class="config-title">
          {{ $t('t_template') }}
          <!-- <Button @click="newTempalte.isShow = true" type="primary" ghost icon="md-add" size="small"></Button> -->
        </div>
        <div class="config-title">
          {{ $t('t_template_value') }}
        </div>
        <template v-for="provider in providerList">
          <div class="config-title" :key="provider.id">
            {{ provider.name }}
          </div>
        </template>
        <div class="config-title action-width">
          {{ $t('t_action') }}
        </div>
      </div>
      <template v-for="(template, tIndex) in pluginTemplates">
        <div style="font-size: 0;margin-top: -1px" :key="template.id">
          <div
            class="config-title"
            :style="{ 'vertical-align': 'bottom', height: template.templateValue.length * 40 + 'px' }"
          >
            <span>
              {{ template.name }}
            </span>
            <Button
              type="primary"
              style="float:right"
              @click="addTemplateValue(template, tIndex)"
              ghost
              icon="md-add"
              size="small"
            ></Button>
          </div>
          <div style="display: inline-block;">
            <template v-for="(tv, tvIndex) in template.templateValue">
              <div :key="tv.key">
                <div class="config-title">
                  <Input v-model="tv.value" size="small" />
                </div>
                <template v-for="provider in providerList">
                  <div class="config-title" :key="provider.id">
                    <Input v-model="tv.providerTemplateValueInfo[provider.name].value" size="small" />
                  </div>
                </template>
                <div class="config-title action-width">
                  <Button type="primary" @click="saveTemplateValue(tv, tIndex, tvIndex)" ghost size="small">{{
                    $t('t_save')
                  }}</Button>
                  <Button
                    type="error"
                    v-if="tv.id"
                    @click="deleteTemplateValue(tv, tIndex, tvIndex)"
                    ghost
                    size="small"
                    >{{ $t('t_delete') }}</Button
                  >
                </div>
              </div>
            </template>
          </div>
        </div>
      </template>
    </div>
    <!-- <Modal
      v-model="newTempalte.isShow"
      :title="$t('t_add_template')"
      @on-ok="addTempalte"
      @on-cancel="newTempalte.isShow = false">
      <Form>
        <FormItem :label="$t('t_name')">
          <Input type="text" v-model="newTempalte.form.name"></Input>
        </FormItem>
        <FormItem :label="$t('t_description')">
          <Input type="password" v-model="newTempalte.form.description"></Input>
        </FormItem>
      </Form>
    </Modal> -->
  </div>
</template>
<script>
import {
  getPluginList,
  getProviderList,
  getTemplateByPlugin,
  getTemplateValue,
  deleteTemplateValue,
  createTemplateValue,
  createTemplate,
  createProviderTemplateValues
} from '@/api/server'
export default {
  name: '',
  data () {
    return {
      pageHeight: '',
      showOperateZone: false,
      newTempalte: {
        isShow: false,
        form: {
          name: '',
          description: ''
        }
      },
      provider: [],
      providerList: [],
      plugin: '',
      pluginOptions: [],
      pluginTemplates: [],

      emptyProviderTemplate: {
        createTime: '',
        createUser: '',
        id: '',
        value: ''
      }
    }
  },
  mounted () {
    this.pageHeight = window.screen.height * 0.7
    this.getProviderList()
    this.getPlugin()
  },
  methods: {
    async addTempalte () {
      const { statusCode } = await createTemplate([this.newTempalte.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getTemplates()
      }
    },
    clearPlugin () {
      this.showOperateZone = false
    },
    async getProviderList () {
      this.providerList = []
      this.provider = []
      const { statusCode, data } = await getProviderList()
      if (statusCode === 'OK') {
        this.providerList = data
        this.provider = this.providerList.map(p => p.name)
      }
    },
    async getPlugin () {
      this.pluginOptions = []
      const { statusCode, data } = await getPluginList()
      if (statusCode === 'OK') {
        this.pluginOptions = data
      }
    },
    async getTemplates () {
      const { statusCode, data } = await getTemplateByPlugin(this.plugin)
      if (statusCode === 'OK') {
        this.pluginTemplates = data.map(d => {
          d.templateValue = []
          return d
        })
        this.pluginTemplates.forEach(template => {
          this.getTemplateValue(template)
        })
        this.showOperateZone = true
      }
    },
    async getTemplateValue (template) {
      const { statusCode, data } = await getTemplateValue(template.id)
      if (statusCode === 'OK') {
        template.templateValue = this.beautyTemplate(data)
      }
    },
    beautyTemplate (data) {
      const res = data.map(d => {
        this.provider.forEach(p => {
          if (!d.providerTemplateValueInfo[p]) {
            d.providerTemplateValueInfo[p] = JSON.parse(JSON.stringify(this.emptyProviderTemplate))
          }
        })
        return d
      })
      return res
    },
    addTemplateValue (template, index) {
      const newTemplate = {
        id: '',
        providerTemplateValueInfo: this.buildEmptyProvider(),
        template: template.name,
        value: ''
      }
      this.pluginTemplates[index].templateValue.push(newTemplate)
    },
    buildEmptyProvider () {
      let res = {}
      this.provider.forEach(p => {
        res[p] = JSON.parse(JSON.stringify(this.emptyProviderTemplate))
      })
      return res
    },
    async saveTemplateValue (templateValue, tIndex, tvIndex) {
      const params = {
        id: templateValue.id,
        value: templateValue.value,
        template: templateValue.template,
        createTime: templateValue.createTime
      }
      const { statusCode, data } = await createTemplateValue([params])
      if (statusCode === 'OK') {
        this.pluginTemplates[tIndex].templateValue[tvIndex].id = data[0].id
        this.pluginTemplates[tIndex].templateValue[tvIndex].value = data[0].value
        let providerValue = []
        this.provider.forEach(p => {
          providerValue.push({
            value: templateValue.providerTemplateValueInfo[p].value,
            provider: p,
            templateValue: data[0].id
          })
        })
        const newTemplateValue = await createProviderTemplateValues(providerValue)
        if (newTemplateValue.statusCode === 'OK') {
          this.$Notice.success({
            title: 'Successful',
            desc: 'Successful'
          })
        }
      }
    },
    deleteTemplateValue (templateValue, tIndex, tvIndex) {
      this.$Modal.confirm({
        title: this.$t('t_confirm_delete'),
        'z-index': 1000000,
        loading: true,
        onOk: async () => {
          let res = await deleteTemplateValue(templateValue.id)
          this.$Modal.remove()
          if (res.statusCode === 'OK') {
            this.$Notice.success({
              title: 'Successful',
              desc: 'Successful'
            })
            this.pluginTemplates[tIndex].templateValue.splice(tvIndex, 1)
          }
        },
        onCancel: () => {}
      })
    }
  }
}
</script>

<style scoped lang="scss">
.config-title {
  display: inline-block;
  border: 1px solid #e9e9e9;
  font-size: 12px;
  margin-left: -1px;
  height: 40px;
  width: 250px;
  padding: 8px 4px;
  font-weight: bold;
  color: #515a6e;
  font-size: 14px;
}
.action-width {
  width: 150px;
}
</style>
