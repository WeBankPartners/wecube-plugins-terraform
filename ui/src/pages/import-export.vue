<template>
  <div class=" ">
    <Row>
      <Col span="5">
        <Card>
          <p slot="title">
            {{ $t('t_plugin') }}
          </p>
          <a href="#" slot="extra" @click.prevent="selectAllPlugin">
            {{ $t('t_select_all') }}
          </a>
          <a href="#" slot="extra" style="color:red" @click.prevent="plugin = []">
            {{ $t('t_cancle') }}
          </a>
          <div :style="{ 'max-height': PAGEHEIGHT + 'px', overflow: 'auto' }">
            <CheckboxGroup v-model="plugin">
              <Checkbox
                v-for="item in pluginOptions"
                :key="item.name"
                :label="item.name"
                style="display: block;padding: 4px 0"
              >
                {{ item.name }}
              </Checkbox>
            </CheckboxGroup>
          </div>
        </Card>
      </Col>
      <Col span="5" offset="1">
        <Card>
          <p slot="title">
            {{ $t('t_provider') }}
          </p>
          <a href="#" slot="extra" @click.prevent="selectProvider">
            {{ $t('t_select_all') }}
          </a>
          <a href="#" slot="extra" style="color:red" @click.prevent="currentProvider = []">
            {{ $t('t_cancle') }}
          </a>
          <CheckboxGroup v-model="currentProvider">
            <Checkbox
              v-for="item in providerList"
              :key="item.name"
              :label="item.name"
              style="display: block;padding: 4px 0"
            >
              {{ item.name }}
            </Checkbox>
          </CheckboxGroup>
        </Card>
      </Col>
      <Col span="5" offset="1">
        <Button class="btn-upload" @click="exportData" :disabled="plugin.length === 0 || currentProvider.length === 0 || isExport">
          <img src="@/styles/icon/DownloadOutlined.svg" class="upload-icon" />
          {{ $t('t_export') }}
        </Button>
        <Upload
          style="float:right"
          :action="uploadUrl"
          :headers="{ Authorization: authToken }"
          :before-upload="handleUpload"
          :show-upload-list="false"
          :max-size="10000"
          with-credentials
          :on-success="uploadSucess"
          :on-error="uploadFailed"
        >
          <Button class="btn-upload">
            <img src="@/styles/icon/UploadOutlined.svg" class="upload-icon" />
            {{ $t('t_import') }}
          </Button>
        </Upload>
      </Col>
    </Row>
  </div>
</template>

<script>
import axios from 'axios'
import { getPluginList, getProviderList } from '@/api/server'
import { getCookie } from '../pages/util/cookie'
export default {
  name: '',
  data () {
    return {
      PAGEHEIGHT: 0,
      isExport: false,
      plugin: [],
      pluginOptions: [],
      currentProvider: [],
      providerList: [],
      uploadUrl: '/terraform/api/v1/provider_plugin_config/import',
      authToken: 'Bearer ' + getCookie('accessToken')
    }
  },
  mounted () {
    this.PAGEHEIGHT = document.body.scrollHeight - 200
    this.getProviderList()
    this.getPlugin()
  },
  methods: {
    selectAllPlugin () {
      this.plugin = this.pluginOptions.map(item => item.name)
    },
    selectProvider () {
      this.currentProvider = this.providerList.map(item => item.name)
    },
    async exportData () {
      this.isExport = true
      axios({
        method: 'GET',
        url: `/terraform/api/v1/provider_plugin_config/export?provider=${this.currentProvider.join(
          ','
        )}&plugin=${this.plugin.join(',')}`,
        headers: {
          Authorization: 'Bearer ' + getCookie('accessToken')
        }
      })
        .then(response => {
          this.isExport = false
          console.log(response)
          if (response.status < 400) {
            let content = JSON.stringify(response.data)
            let fileName = `terraform_${new Date().getFullYear() +
              '-' +
              new Date().getMonth() +
              '-' +
              new Date().getDay() +
              '_' +
              new Date().getHours() +
              ':' +
              new Date().getMinutes() +
              ':' +
              new Date().getSeconds()}.json`
            let blob = new Blob([content])
            if ('msSaveOrOpenBlob' in navigator) {
              window.navigator.msSaveOrOpenBlob(blob, fileName)
            } else {
              if ('download' in document.createElement('a')) {
                // 非IE下载
                let elink = document.createElement('a')
                elink.download = fileName
                elink.style.display = 'none'
                elink.href = URL.createObjectURL(blob)
                document.body.appendChild(elink)
                elink.click()
                URL.revokeObjectURL(elink.href) // 释放URL 对象
                document.body.removeChild(elink)
              } else {
                // IE10+下载
                navigator.msSaveOrOpenBlob(blob, fileName)
              }
            }
          }
        })
        .catch(() => {
          this.$Message.warning('Error')
        })
    },
    async getProviderList () {
      const { statusCode, data } = await getProviderList()
      if (statusCode === 'OK') {
        this.providerList = data
      }
    },
    async getPlugin () {
      const { statusCode, data } = await getPluginList()
      if (statusCode === 'OK') {
        this.pluginOptions = data
      }
    },
    handleUpload (file) {
      if (!file.name.endsWith('.json')) {
        this.$Notice.warning({
          title: 'Warning',
          desc: 'Must be a json file'
        })
        return false
      }
      return true
    },
    uploadFailed (val) {
      this.$Notice.error({
        title: 'Error',
        desc: 'Import Faild'
      })
    },
    async uploadSucess (val) {
      this.$Notice.success({
        title: 'Successful',
        desc: 'Successful'
      })
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
