<template>
  <div class=" ">
    <Table border :columns="tableColumns" :data="tableData"></Table>
    <Modal v-model="dataDetail.isShow" :title="$t('t_detail')" footer-hide>
      <div
        style="overflow: auto;
    max-height: 400px;"
      >
        <pre>{{ dataDetail.data }}</pre>
      </div>
    </Modal>
  </div>
</template>

<script>
import { getDebugInfo } from '@/api/server'
export default {
  name: '',
  data () {
    return {
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
          key: 'resource'
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
      tableData: []
    }
  },
  mounted () {
    this.getDebugInfo()
  },
  methods: {
    async getDebugInfo () {
      const { statusCode, data } = await getDebugInfo()
      if (statusCode === 'OK') {
        this.tableData = data
      }
    },
    showInfo (data) {
      this.dataDetail.isShow = true
      this.dataDetail.data = JSON.parse(data)
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
