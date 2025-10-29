<template>
  <div class=" ">
    <!-- 搜索区 -->
    <div>
      <span>{{ $t('t_plugin') }}</span>
      <Select
        v-model="plugin"
        clearable
        filterable
        @on-open-change="getPlugin"
        @on-clear="clearPlugin"
        style="width: 300px; margin-left: 10px; margin-right: 10px"
      >
        <Option v-for="item in pluginOptions" :value="item.id" :key="item.id">{{ item.name }}</Option>
      </Select>
      <Button type="primary" @click="getTemplates" :disabled="!plugin">{{ $t('t_search') }}</Button>
    </div>
    <!-- 配置区 -->
    <div
      v-if="showOperateZone"
      :style="{ 'margin-top': '36px', 'max-height': pageHeight + 'px', overflow: 'auto' }"
      class="template-data-container"
    >
      <table class="template-data-table">
        <!-- 表头 -->
        <thead>
          <tr>
            <th class="template-name-header">{{ $t('t_template') }}</th>
            <th class="template-value-header">{{ $t('t_template_value') }}</th>
            <th v-for="provider in providerList" :key="provider.id" class="provider-header">{{ provider.name }}</th>
            <th class="action-header">{{ $t('t_action') }}</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(template, tIndex) in pluginTemplates">
            <tr v-for="(tv, tvIndex) in template.templateValue" :key="`${template.id}-${tvIndex}`">
              <!-- 模板名称列 -->
              <td class="template-name-cell" v-if="tvIndex === 0" :rowspan="template.templateValue.length">
                <div class="template-name-content">
                  <span class="template-name-text">{{ template.name }}</span>
                  <Button
                    type="primary"
                    @click="addTemplateValue(template, tIndex)"
                    ghost
                    icon="md-add"
                    size="small"
                    class="add-button"
                  ></Button>
                </div>
              </td>
              <!-- 模板值列 -->
              <td class="template-value-cell">
                <Input v-model="tv.value" size="small" />
              </td>
              <!-- 云厂商列 -->
              <td v-for="provider in providerList" :key="provider.id" class="provider-cell">
                <Input v-model="tv.providerTemplateValueInfo[provider.name].value" size="small" />
              </td>
              <!-- 操作列 -->
              <td class="action-cell">
                <div class="action-buttons">
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
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
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
  createProviderTemplateValues
} from '@/api/server'
export default {
  name: '',
  data () {
    return {
      pageHeight: '',
      showOperateZone: false,
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
    clearPlugin () {
      this.showOperateZone = false
    },
    async getProviderList () {
      this.provider = []
      const { statusCode, data } = await getProviderList()
      if (statusCode === 'OK') {
        this.providerList = data
        this.provider = this.providerList.map(p => p.name)
      }
    },
    async getPlugin () {
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
      let { statusCode, data } = await getTemplateValue(template.id)
      if (statusCode === 'OK') {
        if (data.length === 0) {
          data = [
            {
              id: '',
              template: template.id,
              providerTemplateValueInfo: this.buildEmptyProvider(),
              value: ''
            }
          ]
        }
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
        template: template.id,
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
          const find = this.providerList.find(pro => pro.name === p)
          providerValue.push({
            id: templateValue.providerTemplateValueInfo[p].id,
            value: templateValue.providerTemplateValueInfo[p].value,
            provider: find.id,
            templateValue: data[0].id,
            createTime: templateValue.providerTemplateValueInfo[p].createTime
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
.template-data-container {
  width: 100%;
  overflow-x: auto;
}

.template-data-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e9e9e9;
  font-size: 14px;

  th,
  td {
    border: 1px solid #e9e9e9;
    padding: 8px 12px;
    text-align: left;
    vertical-align: middle;
  }

  th {
    background-color: #fafafa;
    font-weight: bold;
    color: #515a6e;
    text-align: center;
  }

  .template-name-header {
    width: 200px;
    min-width: 200px;
  }

  .template-value-header {
    width: 200px;
    min-width: 200px;
  }

  .provider-header {
    width: 150px;
    min-width: 150px;
  }

  .action-header {
    width: 150px;
    min-width: 150px;
  }

  .template-name-cell {
    background-color: #fafafa;
    vertical-align: top;
    text-align: center;
  }

  .template-name-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .template-name-text {
    font-weight: bold;
    color: #515a6e;
    word-break: break-all;
  }

  .add-button {
    margin-top: 4px;
  }

  .template-value-cell,
  .provider-cell {
    padding: 4px 8px;
  }

  .action-cell {
    text-align: center;
    padding: 4px 8px;
  }

  .action-buttons {
    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: center;
  }

  .action-buttons .ivu-btn {
    width: 60px;
    font-size: 12px;
  }

  // 响应式设计
  @media (max-width: 1200px) {
    .template-name-header,
    .template-name-cell {
      width: 150px;
      min-width: 150px;
    }

    .template-value-header,
    .template-value-cell {
      width: 150px;
      min-width: 150px;
    }

    .provider-header,
    .provider-cell {
      width: 120px;
      min-width: 120px;
    }
  }

  @media (max-width: 768px) {
    .template-data-container {
      font-size: 12px;
    }

    th,
    td {
      padding: 4px 6px;
    }

    .action-buttons .ivu-btn {
      width: 50px;
      font-size: 11px;
      padding: 2px 4px;
    }
  }
}
</style>
