<template>
  <div class="" style="width: 1100px;margin: 0 auto">
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
            <Option v-for="item in pluginOptions" :value="item.id" :key="item.id">{{ item.name }}</Option>
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
            :disabled="!plugin || !currentInterface || !requestBody"
            type="primary"
            >{{ $t('debugger') }}</Button
          >
          <Button @click="test">{{ $t('debugger') }}</Button>
        </Col>
      </Row>
    </div>
    <template v-if="showResult">
      <Table :columns="tableColums" :data="tableData" border></Table>
      <div style="margin: 24px 0">
        <span>{{ $t('debugger_result') }}</span>
        <div style="background: #dcdee2; max-height:300px;overflow:auto">
          <pre>{{ result }}</pre>
        </div>
      </div>
    </template>
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
import { getInterfaceByPlugin, debuggerRequest, getPluginList } from '@/api/server'
export default {
  name: '',
  data () {
    return {
      dataDetail: {
        isShow: false,
        data: {}
      },
      plugin: 'vpc',
      pluginOptions: [],
      currentInterface: 'query',
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
          title: 'sourc_name',
          key: 'sourc_name'
        },
        {
          title: 'tf_json',
          key: 'tf_json',
          width: 300,
          render: (h, params) => {
            console.log(params.row)
            return (
              <div>
                <div style="display:inline-block;width: 200px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_json}
                </div>
                {params.row.tf_json !== '' && (
                  <Button
                    onClick={() => {
                      this.showInfo(params.row.tf_json)
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
          key: 'tf_state'
        }
      ],
      destoryApplyTableColums: [
        {
          title: 'num',
          key: 'num',
          width: 80
        },
        {
          title: 'sourc_name',
          key: 'sourc_name'
        },
        {
          title: 'tf_json_old',
          key: 'tf_json_old',
          width: 200,
          render: (h, params) => {
            console.log(params.row)
            return (
              <div>
                <div style="display:inline-block;width: 130px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_json_old}
                </div>
                {params.row.tf_json_old !== '' && (
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
            console.log(params.row)
            return (
              <div>
                <div style="display:inline-block;width: 130px;overflow: hidden;text-overflow:ellipsis;white-space: nowrap">
                  {params.row.tf_json_new}
                </div>
                {params.row.tf_json_new !== '' && (
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
          title: 'tf_state_new',
          key: 'tf_state_new'
        },
        {
          title: 'tf_state_import',
          key: 'tf_state_import'
        },
        {
          title: 'plan_message',
          key: 'plan_message'
        }
      ],
      tableData: [],
      result: {}
    }
  },
  mounted () {
    this.getPlugin()
  },
  methods: {
    showInfo (data) {
      this.dataDetail.isShow = true
      this.dataDetail.data = JSON.parse(data)
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
    test () {
      if (this.currentInterface !== 'query') {
        this.tableColums = this.queryTableColums
      } else {
        this.tableColums = this.destoryApplyTableColums
      }
      let xx = {
        resultCode: '0',
        resultMessage: 'success',
        results: {
          outputs: [
            {
              result_data: [
                {
                  asset_id: '1111-1',
                  callbackParameter: '1111-1',
                  cidr: '111-1',
                  errorCode: '1111-1',
                  errorMessage: '1111-1',
                  id: '1111-1',
                  name: '1111-1'
                },
                {
                  asset_id: '1111-1',
                  callbackParameter: '1111-1',
                  cidr: '111-1',
                  errorCode: '1111-1',
                  errorMessage: '1111-1',
                  id: '1111-1',
                  name: '1111-1'
                }
              ],
              resource_results: [
                {
                  plan_message: '11111',
                  sourc_name: '1111',
                  tf_json_new: '1111',
                  tf_json_old: '1111',
                  tf_state_import: '1111',
                  tf_state_new: '111111'
                },
                {
                  plan_message: '11111',
                  sourc_name: '1111',
                  tf_json_new: '1111',
                  tf_json_old: '1111',
                  tf_state_import: '1111',
                  tf_state_new: '111111'
                }
              ]
            },
            {
              result_data: [
                {
                  asset_id: '222',
                  callbackParameter: '222',
                  cidr: '222',
                  errorCode: '222',
                  errorMessage: '222',
                  id: '222',
                  name: '222'
                },
                {
                  asset_id: '222',
                  callbackParameter: '222',
                  cidr: '222',
                  errorCode: '222',
                  errorMessage: '222',
                  id: '222',
                  name: '222'
                }
              ],
              resource_results: [
                {
                  plan_message: '222',
                  sourc_name: '222',
                  tf_json_new: '222',
                  tf_json_old: '222',
                  tf_state_import: '222',
                  tf_state_new: '222'
                },
                {
                  plan_message: '222',
                  sourc_name: '222',
                  tf_json_new: '222',
                  tf_json_old: '222',
                  tf_state_import: '222',
                  tf_state_new: '222'
                }
              ]
            }
          ]
        }
      }
      this.tableData = []
      this.result = {}
      xx.results.outputs.forEach((element, index) => {
        this.result['res_' + index] = element.result_data
        element.resource_results.forEach((ele, eleIndex) => {
          ele.num = index + '-' + eleIndex
          this.tableData.push(ele)
        })
      })
      console.log(this.tableData)
      this.showResult = true
    },
    async debuggerRequest () {
      const { statusCode, data } = await debuggerRequest(this.plugin, this.currentInterface, this.requestBody)
      if (statusCode === 'OK') {
        if (this.currentInterface === 'query') {
          this.tableColums = this.queryTableColums
        } else {
          this.tableColums = this.destoryApplyTableColums
        }
        this.tableTable = data
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
      const { statusCode, data } = await getInterfaceByPlugin(this.plugin)
      if (statusCode === 'OK') {
        this.interfaceOptions = data
      }
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
