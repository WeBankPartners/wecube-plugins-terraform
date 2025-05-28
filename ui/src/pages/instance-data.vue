<template>
  <div>
    <div class="search">
      <Select
        v-model="serachParams.resource"
        filterable
        clearable
        :placeholder="$t('t_resource')"
        @on-change="handleSearch"
        @on-clear="handleSearch"
        class="search-input"
      >
        <Option v-for="item in resourceList" :value="item.id" :key="item.id" :label="item.name">
          {{ item.name }}
        </Option>
      </Select>
      <Input
        v-model="serachParams.resource_id"
        :placeholder="$t('t_resource_id')"
        class="search-input"
        @on-change="handleSearch"
        clearable
      />
      <Input
        v-model="serachParams.resource_asset_id"
        :placeholder="$t('t_resource_asset_id')"
        class="search-input"
        @on-change="handleSearch"
        clearable
      />
      <Button @click="handleReset">{{ $t('t_reset') }}</Button>
    </div>
    <Table
      border
      size="small"
      :columns="tableColumns"
      :data="tableData"
      :max-height="MODALHEIGHT"
      :loading="tableLoading"
    ></Table>
    <Page
      style="float: right; margin-top: 16px"
      :total="pageable.total"
      @on-change="changPage"
      show-sizer
      :current="pageable.current"
      :page-size="pageable.pageSize"
      @on-page-size-change="changePageSize"
      show-total
    />
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
import { getInstanceData, getResourceList } from '@/api/server'
import { debounce } from '@/pages/util'
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
      resourceList: [],
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
      tableLoading: false,
      pageable: {
        pageSize: 10,
        startIndex: 1,
        current: 1,
        total: 0
      },
      serachParams: {
        resource: '',
        resource_id: '',
        resource_asset_id: ''
      },
      uploadUrl: ''
    }
  },
  mounted () {
    this.MODALHEIGHT = document.body.scrollHeight - 200
    this.getInstanceData()
    this.getResourceList()
  },
  methods: {
    changePageSize (pageSize) {
      this.pageable.current = 1
      this.pageable.pageSize = pageSize
      this.getInstanceData()
    },
    changPage (current) {
      this.pageable.current = current
      this.getInstanceData()
    },
    handleSearch: debounce(function () {
      this.pageable.current = 1
      this.getInstanceData()
    }, 600),
    handleReset () {
      this.serachParams = {
        resource: '',
        resource_id: '',
        resource_asset_id: ''
      }
      this.handleSearch()
    },
    async getInstanceData () {
      const params = {
        params: {
          resource: this.serachParams.resource,
          resource_id: this.serachParams.resource_id,
          resource_asset_id: this.serachParams.resource_asset_id,
          page: this.pageable.current,
          pageSize: this.pageable.pageSize
        }
      }
      this.tableLoading = true
      const { statusCode, data } = await getInstanceData(params)
      this.tableLoading = false
      if (statusCode === 'OK') {
        this.tableData = data.contents || []
        this.pageable.total = data.pageInfo.totalRows || 0
      }
    },
    showInfo (data) {
      this.dataDetail.data = ''
      this.dataDetail.isShow = true
      this.dataDetail.data = JSON.parse(data)
    },
    async getResourceList () {
      const { statusCode, data } = await getResourceList()
      if (statusCode === 'OK') {
        this.resourceList = data || []
      }
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
.search {
  margin-bottom: 10px;
  .search-input {
    width: 240px;
    margin-right: 10px;
  }
}
</style>
