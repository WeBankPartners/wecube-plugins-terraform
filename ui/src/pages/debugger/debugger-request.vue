<template>
  <!-- 'max-height': PAGEHEIGHT + 'px', 'overflow': 'auto' -->
  <div class="" :style="{ width: '1100px', margin: '0 auto' }">
    <div>
      <Row>
        <Col span="12">
          <div style="width:80px;display: inline-block">{{ $t('t_plugin') }}</div>
          <Select
            v-model="plugin"
            clearable
            @on-clear="clearPlugin"
            @on-change="currentInterface = ''"
            filterable
            style="width:400px"
          >
            <Option v-for="item in pluginOptions" :value="item.name" :key="item.name">{{ item.name }}</Option>
          </Select>
        </Col>
        <Col span="12">
          <div style="width:80px;display: inline-block">{{ $t('t_interface') }}</div>
          <Select
            v-model="currentInterface"
            clearable
            @on-clear="clearInterface"
            filterable
            @on-open-change="getPluginInterface"
            :disabled="!plugin"
            style="width:400px"
          >
            <Option v-for="item in interfaceOptions" :value="item.name" :key="item.id">{{ item.name }}</Option>
          </Select>
        </Col>
      </Row>
      <Row style="margin: 24px 0">
        <Col span="24">
          <div style="width:80px;display: inline-block">{{ $t('t_request_body') }}</div>
          <Input style="width:845px" v-model="requestBody" type="textarea" :rows="6"></Input>
          <Button
            @click="debuggerRequest"
            style="height: 60px;width:100px"
            :disabled="!plugin || !currentInterface || !requestBody || disabledBtn"
            type="primary"
            >{{ $t('debugger') }}</Button
          >
        </Col>
      </Row>
    </div>
    <template v-if="showResult">
      <Table :columns="tableColums" :data="tableData" border></Table>
      <div style="margin: 24px 0">
        <span>{{ $t('debugger_result') }}</span>
        <div style="background: #dcdee2; max-height:400px;overflow:auto">
          <pre>{{ result }}</pre>
        </div>
      </div>
    </template>
    <Modal v-model="dataDetail.isShow" :fullscreen="fullscreen" width="800" footer-hide>
      <p slot="header">
        <span>{{ $t('t_detail') }}</span>
        <Icon v-if="!fullscreen" @click="fullscreen = true" class="header-icon" type="ios-expand" />
        <Icon v-else @click="fullscreen = false" class="header-icon" type="ios-contract" />
      </p>
      <div style="overflow: auto;max-height: 500px;">
        <pre>{{ dataDetail.data }}</pre>
      </div>
    </Modal>
  </div>
</template>

<script>
import { getInterfaceByPlugin, debuggerRequest, getPluginList } from '@/api/server'
export default {
  name: '',
  data () {
    return {
      PAGEHEIGHT: 0,
      fullscreen: false,
      dataDetail: {
        isShow: false,
        data: {}
      },
      plugin: '',
      pluginOptions: [],
      currentInterface: '',
      interfaceOptions: [],
      requestBody: '',
      showResult: false,

      tableColums: [],
      queryTableColums: [
        {
          title: 'num',
          key: 'num'
        },
        {
          title: 'source_name',
          key: 'source_name',
          width: 200
        },
        {
          title: 'tf_json',
          key: 'tf_json_new',
          width: 300,
          render: (h, params) => {
            return (
              <div>
                <div style="display:inline-block;width: 200px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_json_new}
                </div>
                {params.row.tf_json_new && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tf_json_new)
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
          title: 'tf_state',
          key: 'tf_state',
          width: 300,
          render: (h, params) => {
            return (
              <div>
                <div style="display:inline-block;width: 200px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_state_new}
                </div>
                {params.row.tf_state_new && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tf_state_new)
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
      destoryApplyTableColums: [
        {
          title: 'num',
          key: 'num',
          width: 80
        },
        {
          title: 'source_name',
          key: 'source_name',
          width: 200
        },
        {
          title: 'tf_json_old',
          key: 'tf_json_old',
          width: 200,
          render: (h, params) => {
            return (
              <div>
                <div style="display:inline-block;width: 130px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_json_old}
                </div>
                {params.row.tf_json_old && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tf_json_old)
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
          title: 'tf_json_new',
          key: 'tf_json_new',
          width: 200,
          render: (h, params) => {
            return (
              <div>
                <div style="display:inline-block;width: 130px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_json_new}
                </div>
                {params.row.tf_json_new && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tf_json_new)
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
          title: 'tf_state_old',
          key: 'tf_state_old',
          width: 200,
          render: (h, params) => {
            return (
              <div>
                <div style="display:inline-block;width: 130px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_state_old}
                </div>
                {params.row.tf_state_old && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tf_state_old)
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
          title: 'tf_state_new',
          key: 'tf_state_new',
          width: 200,
          render: (h, params) => {
            console.log(params.row)
            return (
              <div>
                <div style="display:inline-block;width: 130px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_state_new}
                </div>
                {params.row.tf_state_new && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tf_state_new)
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
          title: 'tf_state_import',
          key: 'tf_state_import',
          width: 200,
          render: (h, params) => {
            console.log(params.row)
            return (
              <div>
                <div style="display:inline-block;width: 130px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_state_import}
                </div>
                {params.row.tf_state_import && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tf_state_import)
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
          title: 'plan_message',
          key: 'plan_message',
          width: 200,
          render: (h, params) => {
            console.log(params.row)
            return (
              <div>
                <div style="display:inline-block;width: 130px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.plan_message}
                </div>
                {params.row.plan_message && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.plan_message)
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
      result: {},
      disabledBtn: false
    }
  },
  mounted () {
    this.PAGEHEIGHT = document.body.scrollHeight
    this.getPlugin()
  },
  methods: {
    showInfo (data) {
      this.dataDetail.data = ''
      this.dataDetail.isShow = true
      const isJson = data.startsWith('{') && data.endsWith('}')
      this.dataDetail.data = isJson ? JSON.parse(data) : data
    },
    clearInterface () {
      this.currentInterface = ''
      this.tableData = []
      this.result = {}
      this.showResult = false
    },
    clearPlugin () {
      this.plugin = ''
      this.currentInterface = ''
      this.tableData = []
      this.result = {}
      this.showResult = false
    },
    managementData (data) {
      if (this.currentInterface === 'query') {
        this.tableColums = this.queryTableColums
      } else {
        this.tableColums = this.destoryApplyTableColums
      }
      this.tableData = []
      this.result = {}
      data.results.outputs.forEach((element, index) => {
        this.result['res_' + index] = element.result_data
        element.resource_results.forEach((ele, eleIndex) => {
          ele.num = index + '-' + eleIndex
          this.tableData.push(ele)
        })
      })
      this.showResult = true
    },
    async debuggerRequest () {
      this.$Notice.success({
        title: 'Successful',
        desc: 'Need 10s ……'
      })
      this.showResult = false
      this.disabledBtn = true
      const result = await debuggerRequest(this.plugin, this.currentInterface, this.requestBody)
      this.disabledBtn = false
      if (result.statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.managementData(result)
        this.showResult = true
      }
    },
    async getPlugin () {
      this.pluginOptions = []
      const { statusCode, data } = await getPluginList()
      if (statusCode === 'OK') {
        this.pluginOptions = data
      }
    },
    async getPluginInterface () {
      const plugin = this.pluginOptions.find(p => p.name === this.plugin)
      const { statusCode, data } = await getInterfaceByPlugin(plugin.id)
      if (statusCode === 'OK') {
        this.interfaceOptions = data
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
</style>
