<template>
  <div>
    <tooltip content=""> </tooltip>
    <Table border size="small" :columns="tableColumns" :data="tableData" :max-height="MODALHEIGHT"></Table>
    <Modal v-model="dataDetail.isShow" :fullscreen="fullscreen" width="800" :mask-closable="false" footer-hide>
      <p slot="header">
        <span>{{ $t('t_detail') }}</span>
        <Icon v-if="!fullscreen" @click="fullscreen = true" class="header-icon" type="ios-expand" />
        <Icon v-else @click="fullscreen = false" class="header-icon" type="ios-contract" />
      </p>
      <div :style="{ overflow: 'auto', 'max-height': fullscreen ? '' : '500px' }">
        <pre>{{ dataDetail.data }}</pre>
      </div>
    </Modal>
  </div>
</template>

<script>
import { getInstanceData, instanceDataDownload } from '@/api/server'
export default {
  name: '',
  data () {
    return {
      MODALHEIGHT: 500,
      fullscreen: false,
      dataDetail: {
        isShow: false,
        data: {}
      },
      tableColumns: [
        {
          title: this.$t('t_region'),
          key: 'regionId'
        },
        {
          title: this.$t('t_resource'),
          key: 'resourceTitle'
        },
        {
          title: this.$t('t_resource_asset_id'),
          key: 'resourceAssetId'
        },
        {
          title: this.$t('t_resource_id'),
          key: 'resourceId'
        },
        {
          title: this.$t('t_tf_file'),
          width: 300,
          render: (h, params) => {
            return (
              <div>
                <div style="display:inline-block;width: 200px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tfFile}
                </div>
                {params.row.tfFile !== '' && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tfFile)
                    }}
                    style="vertical-align: top;"
                    icon="ios-search"
                    type="primary"
                    ghost
                    size="small"
                  ></Button>
                )}
              </div>
            )
          }
        },
        {
          title: this.$t('t_tf_state_file'),
          width: 300,
          render: (h, params) => {
            return (
              <div>
                <div style="display:inline-block;width: 200px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tfStateFile}
                </div>
                {params.row.tfStateFile !== '' && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tfStateFile)
                    }}
                    style="vertical-align: top;"
                    icon="ios-search"
                    type="primary"
                    ghost
                    size="small"
                  ></Button>
                )}
              </div>
            )
          }
        },
        {
          title: this.$t('t_action'),
          key: 'action',
          width: 160,
          align: 'center',
          render: (h, params) => {
            if (params.row.providerInitialized === 'Y') {
              return ''
            }
            return h('div', [
              h(
                'Upload',
                {
                  props: {
                    type: 'select',
                    size: 'small',
                    action: `/terraform/api/v1/providers/upload?id=${params.row.providerId}`,
                    'on-success': this.handleSuccess,
                    'on-error': this.handleError,
                    'before-upload': this.handleUpload
                  },
                  style: {
                    display: 'inline-block'
                  },
                  on: {}
                },
                [
                  h(
                    'Button',
                    {
                      props: {
                        type: 'success',
                        size: 'small'
                      },
                      style: {},
                      on: {}
                    },
                    this.$t('t_import')
                  )
                ]
              ),
              h(
                'Button',
                {
                  props: Object.assign(
                    {},
                    {
                      type: 'primary',
                      size: 'small'
                    }
                  ),
                  style: {
                    'margin-left': '8px'
                  },
                  on: {
                    click: () => {
                      this.downloadInstance(params.row)
                    }
                  }
                },
                this.$t('t_export')
              )
            ])
          }
        }
      ],
      tableData: [],
      uploadUrl: ''
    }
  },
  mounted () {
    this.MODALHEIGHT = document.body.scrollHeight - 200
    this.getInstanceData()
  },
  methods: {
    handleUpload (file) {
      if (file.name.endsWith('.gz') || file.name.endsWith('.zip')) {
        return true
      } else {
        this.$Notice.warning({
          title: 'Warning',
          desc: 'Must be a .gz or .zip file'
        })
        return false
      }
    },
    handleError (val) {
      this.$Notice.error({
        title: 'Error',
        desc: 'Import Faild'
      })
    },
    handleSuccess (val) {
      this.$Notice.success({
        title: 'Successful',
        desc: 'Successful'
      })
      this.getInstanceData()
    },
    async downloadInstance (item) {
      this.$Notice.success({
        title: 'Info',
        desc: 'Need 10s ……'
      })
      const { statusCode } = await instanceDataDownload(item.providerId)
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getInstanceData()
      }
    },
    async getInstanceData () {
      const { statusCode, data } = await getInstanceData()
      if (statusCode === 'OK') {
        this.tableData = data
      }
    },
    showInfo (data) {
      this.dataDetail.data = ''
      this.dataDetail.isShow = true
      this.dataDetail.data = JSON.parse(data)
    }
  },
  components: {}
}
</script>

<style scoped lang="scss">
.header-icon {
  float: right;
  margin: 3px 40px 0 0 !important;
}
</style>
