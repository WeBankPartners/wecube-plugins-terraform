<template>
  <div>
    <tooltip content=""> </tooltip>
    <Table border :columns="tableColumns" :data="tableData" :max-height="MODALHEIGHT"></Table>
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
import { getInstanceData } from '@/api/server'
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
