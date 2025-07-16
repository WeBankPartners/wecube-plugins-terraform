<template>
  <!-- 'max-height': PAGEHEIGHT + 'px', 'overflow': 'auto' -->
  <div class="" :style="{ width: '1100px', margin: '0 auto' }">
    <Form :label-width="120">
      <Row>
        <Col span="12">
          <FormItem :label="$t('t_plugin')">
            <Select
              v-model="plugin"
              clearable
              @on-clear="clearPlugin"
              @on-change="currentInterface = ''"
              @on-open-change="getPlugin"
              filterable
              style="width: 100%"
            >
              <Option v-for="item in pluginOptions" :value="item.name" :key="item.name">{{ item.name }}</Option>
            </Select>
          </FormItem>
        </Col>
        <Col span="12">
          <FormItem :label="$t('t_interface')">
            <Select
              v-model="currentInterface"
              clearable
              @on-clear="clearInterface"
              filterable
              @on-open-change="getPluginInterface"
              :disabled="!plugin"
              style="width: 100%"
            >
              <Option v-for="item in interfaceOptions" :value="item.name" :key="item.id">{{ item.name }}</Option>
            </Select>
          </FormItem>
        </Col>
      </Row>
      <Row>
        <Col span="24">
          <FormItem :label="$t('t_request_body')">
            <Input style="width: 100%" v-model="requestBody" type="textarea" :rows="25"></Input>
            <div style="height: 50px; width: 100%; margin-top: 10px; display: flex; justify-content: flex-end">
              <Tooltip :content="$t('t_format_parameter')" :delay="1000">
                <Icon @click="formatRequestBody" style="color: #00cb91; cursor: pointer" :size="28" type="md-apps" />
              </Tooltip>
              <!-- @click.stop.prevent="editPlugin(plugin)" -->
              <Button
                @click="debuggerRequest"
                style="height: 40px; width: 100px"
                :disabled="!plugin || !currentInterface || !requestBody || disabledBtn"
                type="primary"
                >{{ $t('debugger') }}</Button
              >
            </div>
          </FormItem>
        </Col>
      </Row>
    </Form>
    <template v-if="showResult">
      <Table size="small" :columns="tableColums" :data="tableData" border></Table>
      <div style="margin: 24px 0">
        <span>{{ $t('debugger_result') }}</span>
        <div style="background: #dcdee2; max-height: 400px; overflow: auto">
          <pre>{{ result }}</pre>
        </div>
      </div>
    </template>
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
import { getInterfaceByPlugin, debuggerRequest, getPluginList, getParamaByInterface } from '@/api/server'
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
      emptyBody: {
        requestId: 'request-',
        operator: 'debugger',
        inputs: [
          {
            confirmToken: '',
            callbackParameter: '',
            id: '',
            asset_id: '',
            provider_info: '',
            region_id: ''
          }
        ]
      },
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
  watch: {
    async currentInterface () {
      // 获取插件入参，将入参自动填充到请求报文中
      const interfaceItem = this.interfaceOptions.find(i => i.name === this.currentInterface)
      const { statusCode, data } = await getParamaByInterface(interfaceItem.id)
      if (statusCode === 'OK') {
        const inputParams = (data && data.filter(item => item.type === 'input')) || []
        let inputParamsObj = {}
        inputParams.forEach(item => {
          if (item.dataType === 'object') {
            inputParamsObj[item.name] = {}
          } else {
            inputParamsObj[item.name] = ''
          }
        })
        this.requestBody = JSON.stringify(this.emptyBody, null, 4)
        const requestBody = JSON.parse(this.requestBody)
        requestBody.inputs = requestBody.inputs.map(item => {
          item = Object.assign({}, item, inputParamsObj)
          return item
        })
        this.requestBody = JSON.stringify(requestBody, null, 4)
      }
    }
  },
  mounted () {
    this.emptyBody.requestId = this.emptyBody.requestId + new Date().getUTCMilliseconds()
    this.requestBody = JSON.stringify(this.emptyBody, null, 4)
    this.PAGEHEIGHT = document.body.scrollHeight
    this.getPlugin()
  },
  methods: {
    formatRequestBody () {
      console.log(this.requestBody)
      try {
        this.requestBody = JSON.parse(this.requestBody)
        this.requestBody = JSON.stringify(this.requestBody, null, 4)
      } catch (error) {
        console.log(error)
        this.$Notice.warning({
          title: 'Warning',
          desc: 'JSON Format Error'
        })
      }
    },
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
