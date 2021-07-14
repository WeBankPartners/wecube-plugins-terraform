<template>
  <div class="">
    <Row>
      <Col span="5" style="border-right: 1px solid #e8eaec;">
        <div style="height: calc(100vh - 180px);overflow-y:auto;">
          <div style="">
            <Menu
              theme="light"
              accordion
              @on-select="getInterfaceParamter"
              @on-open-change="getPluginInterface"
              style="width: 100%;z-index:10"
            >
              <Submenu v-for="(plugin, index) in pluginOptions" :name="plugin.name" style="padding: 0;" :key="index">
                <template slot="title">
                  <Icon type="md-grid" />
                  <span style="font-size: 15px;">{{ plugin.name }}</span>
                  <div style="float:right;color: #2d8cf0;margin-right:30px">
                    <Tooltip :content="$t('t_add')" :delay="1000">
                      <Icon @click.stop.prevent="addInterface(plugin)" style="" type="md-add" />
                    </Tooltip>
                    <Tooltip :content="$t('t_add')" :delay="1000">
                      <Icon
                        @click.stop.prevent="editPlugin(plugin)"
                        style="color: #19be6b;"
                        type="ios-create-outline"
                      />
                    </Tooltip>
                  </div>
                </template>
                <MenuItem
                  v-for="(interfaceSingle, index) in plugin.interfaces"
                  :name="interfaceSingle.id"
                  :key="index"
                  style="padding: 5px 32px 5px 32px;"
                >
                  <span
                    style="display: inline-block;white-space: nowrap; overflow: hidden; text-overflow: ellipsis;font-size: 15px; font-weight:400"
                    >{{ interfaceSingle.name }}</span
                  >
                  <div style="vertical-align: top;display: inline-block;float: right;">
                    <Tooltip :content="$t('t_edit')" :delay="500">
                      <Icon
                        size="16"
                        style="color: #19be6b;"
                        @click.stop.prevent="editInterface(interfaceSingle)"
                        type="ios-create-outline"
                      />
                    </Tooltip>
                    <Tooltip :content="$t('t_delete')" :delay="500">
                      <Icon
                        size="16"
                        style="color: #ed4014;"
                        @click.stop.prevent="deleteInterface(interfaceSingle, plugin)"
                        type="ios-trash-outline"
                      />
                    </Tooltip>
                  </div>
                </MenuItem>
              </Submenu>
            </Menu>
          </div>
        </div>
      </Col>
      <Col v-if="currentInterface" span="18" offset="1">
        <div class="modal-paramsContainer">
          <Row style="border-bottom: 1px solid #e5dfdf;margin-bottom:5px">
            <Col span="3" offset="0">
              <strong style="font-size:15px;">{{ $t('t_params_type') }}</strong>
            </Col>
            <Col span="3" offset="0">
              <strong style="font-size:15px;">{{ $t('t_name') }}</strong>
            </Col>
            <Col span="3" offset="1">
              <strong style="font-size:15px;">{{ $t('t_data_type') }}</strong>
            </Col>
            <Col span="4" offset="0" style="margin-left:24px">
              <strong style="font-size:15px;">{{ $t('t_template') }}</strong>
            </Col>
            <Col span="4" offset="0">
              <strong style="font-size:15px;">
                {{ $t('t_object_name') }}
              </strong>
            </Col>
            <Col span="2" offset="0">
              <strong style="font-size:15px;">
                {{ $t('t_multiple') }}
              </strong>
            </Col>
            <Col span="3" offset="0">
              <strong style="font-size:15px;">
                {{ $t('t_action') }}
              </strong>
            </Col>
          </Row>
          <div class="modal-interfaceContainers">
            <Form>
              <Row>
                <Col span="3">
                  <FormItem :label-width="0">
                    <span>{{ $t('t_input_params') }}</span>
                    <Button @click="addParams('input')" size="small" icon="ios-add"></Button>
                  </FormItem>
                </Col>
                <Col span="20" offset="0">
                  <Row v-for="(param, index) in interfaceParamter['input']" :key="index">
                    <Col span="4">
                      <FormItem :label-width="0">
                        <Input v-model="param.name" />
                      </FormItem>
                    </Col>
                    <Col span="4" offset="1">
                      <FormItem :label-width="0">
                        <Select v-model="param.dataType" filterable clearable style="width: 80%">
                          <Option v-for="dt in dataTypeOptions" :value="dt.value" :key="dt.value">{{
                            dt.label
                          }}</Option>
                        </Select>
                      </FormItem>
                    </Col>
                    <Col span="4" offset="0">
                      <FormItem :label-width="0">
                        <Select v-model="param.template" ref="inputSelect" filterable clearable>
                          <Button type="success" style="width:100%" @click="addTemplate" size="small">
                            <Icon type="ios-add" size="24"></Icon>
                          </Button>
                          <Option v-for="template in templateOptions" :value="template.name" :key="template.name">{{
                            template.name
                          }}</Option>
                        </Select>
                      </FormItem>
                    </Col>
                    <Col span="3" offset="1">
                      <FormItem :label-width="0">
                        <Select v-model="param.objectName" filterable clearable>
                          <Option v-for="objName in inputObjectNameOptions" :value="objName.id" :key="objName.id">{{
                            objName.name
                          }}</Option>
                        </Select>
                      </FormItem>
                    </Col>
                    <Col span="2" offset="1">
                      <Select v-model="param.multiple" filterable>
                        <Option value="Y">Y</Option>
                        <Option value="N">N</Option>
                      </Select>
                    </Col>
                    <Col span="3" offset="1">
                      <FormItem :label-width="0">
                        <Button type="primary" ghost @click="saveParams(param)" size="small">
                          {{ $t('t_save') }}
                        </Button>
                        <Button type="error" ghost size="small" @click="deleteParams(param)">{{
                          $t('t_delete')
                        }}</Button>
                      </FormItem>
                    </Col>
                  </Row>
                </Col>
              </Row>
              <hr style="margin:16px 0" />
              <Row>
                <Col span="3">
                  <FormItem :label-width="0">
                    <span>{{ $t('t_output_params') }}</span>
                    <Button @click="addParams('output')" size="small" icon="ios-add"></Button>
                  </FormItem>
                </Col>
                <Col span="20" offset="0">
                  <Row v-for="(param, index) in interfaceParamter['output']" :key="index">
                    <Col span="4">
                      <FormItem :label-width="0">
                        <Input v-model="param.name" style="width:100%" />
                      </FormItem>
                    </Col>
                    <Col span="4" offset="1">
                      <FormItem :label-width="0">
                        <Select v-model="param.dataType" filterable clearable style="width: 80%">
                          <Option v-for="dt in dataTypeOptions" :value="dt.value" :key="dt.value">{{
                            dt.label
                          }}</Option>
                        </Select>
                      </FormItem>
                    </Col>
                    <Col span="4" offset="0">
                      <FormItem :label-width="0">
                        <Select v-model="param.template" ref="outputSelect" filterable clearable>
                          <Button type="success" style="width:100%" @click="addTemplate" size="small">
                            <Icon type="ios-add" size="24"></Icon>
                          </Button>
                          <Option v-for="template in templateOptions" :value="template.name" :key="template.name">{{
                            template.name
                          }}</Option>
                        </Select>
                      </FormItem>
                    </Col>
                    <Col span="3" offset="1">
                      <FormItem :label-width="0">
                        <Select v-model="param.objectName" filterable clearable>
                          <Option v-for="objName in outputObjectNameOptions" :value="objName.id" :key="objName.id">{{
                            objName.name
                          }}</Option>
                        </Select>
                      </FormItem>
                    </Col>
                    <Col span="2" offset="1">
                      <FormItem :label-width="0">
                        <Select v-model="param.multiple" filterable>
                          <Option value="Y">Y</Option>
                          <Option value="N">N</Option>
                        </Select>
                      </FormItem>
                    </Col>
                    <Col span="3" offset="1">
                      <FormItem :label-width="0">
                        <Button type="primary" ghost @click="saveParams(param)" size="small">
                          {{ $t('t_save') }}
                        </Button>
                        <Button type="error" ghost size="small" @click="deleteParams(param)"
                          >{{ $t('t_delete') }}
                        </Button>
                      </FormItem>
                    </Col>
                  </Row>
                </Col>
              </Row>
            </Form>
          </div>
        </div>
      </Col>
    </Row>
    <Modal
      v-model="newTemplate.isShow"
      :title="$t('t_add_template')"
      @on-ok="confirmAddTemplate"
      @on-cancel="newTemplate.isShow = false"
    >
      <Form inline>
        <FormItem :label="$t('t_name')">
          <Input type="text" v-model="newTemplate.form.name"></Input>
        </FormItem>
        <FormItem :label="$t('t_description')">
          <Input type="password" v-model="newTemplate.form.description"></Input>
        </FormItem>
      </Form>
    </Modal>
    <Modal
      v-model="newPlugin.isShow"
      :title="$t('t_add') + $t('t_plugin')"
      @on-ok="confirmPlugin"
      @on-cancel="newPlugin.isShow = false"
    >
      <Form inline :label-width="80">
        <FormItem :label="$t('t_name')">
          <Input type="text" v-model="newPlugin.form.name" style="width:300px"></Input>
        </FormItem>
      </Form>
    </Modal>
    <Modal
      v-model="newInterface.isShow"
      :title="newInterface.isShow.isAdd ? $t('t_add') : $t('t_edit') + $t('t_interface')"
      @on-ok="confirmInterface"
      @on-cancel="newInterface.isShow = false"
    >
      <Form inline :label-width="80">
        <FormItem :label="$t('t_name')">
          <Input type="text" v-model="newInterface.form.name" style="width:300px"></Input>
        </FormItem>
        <FormItem :label="$t('t_description')">
          <Input type="text" v-model="newInterface.form.description" style="width:300px"></Input>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  getPluginList,
  getTemplate,
  getInterfaceByPlugin,
  editInterface,
  deleteInterface,
  getParamaByInterface,
  addPlugin,
  editPlugin,
  addParameter,
  deleteParameter,
  createTemplate,
  editParameter,
  addInterface
} from '@/api/server'
export default {
  name: '',
  data () {
    return {
      currentPlugin: '',
      currentInterface: '',
      pluginOptions: [],
      templateOptions: [],
      dataTypeOptions: [
        { label: 'string', value: 'string' },
        { label: 'object', value: 'object' },
        { label: 'int', value: 'int' }
      ],
      inputObjectNameOptions: [],
      outputObjectNameOptions: [],
      newPlugin: {
        isShow: false,
        form: {
          name: ''
        }
      },
      newInterface: {
        isShow: false,
        isAdd: true,
        form: {
          name: '',
          plugin: '',
          description: ''
        }
      },
      interfaceParamter: {
        input: [],
        output: []
      },
      emptyParamter: {
        createTime: '',
        createUser: '',
        dataType: '',
        id: '',
        interface: '',
        multiple: 'N',
        name: '',
        objectName: '',
        template: '',
        type: '',
        updateTime: '',
        updateUser: ''
      },
      newTemplate: {
        isShow: false,
        form: {
          name: '',
          description: ''
        }
      }
    }
  },
  mounted () {
    this.getPlugin()
  },
  methods: {
    async confirmAddTemplate () {
      const { statusCode } = await createTemplate([this.newTemplate.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getTemplates()
      }
    },
    addTemplate () {
      this.$refs.inputSelect.visible = false
      this.$refs.outputSelect.visible = false
      this.newTemplate = {
        isShow: true,
        form: {
          name: '',
          description: ''
        }
      }
    },
    async saveParams (param) {
      console.log(param)
      const method = param.id === '' ? addParameter : editParameter
      const { statusCode } = await method([param])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
      }
    },
    deleteParams (param) {
      this.$Modal.confirm({
        title: this.$t('t_confirm_delete'),
        'z-index': 1000000,
        loading: true,
        onOk: async () => {
          let res = await deleteParameter(param.id)
          this.$Modal.remove()
          if (res.statusCode === 'OK') {
            this.$Notice.success({
              title: 'Successful',
              desc: 'Successful'
            })
            this.getInterfaceParamter(param.interface)
          }
        },
        onCancel: () => {}
      })
    },
    async getTemplates () {
      const { statusCode, data } = await getTemplate()
      if (statusCode === 'OK') {
        this.templateOptions = data
      }
    },
    addParams (type) {
      let tmp = JSON.parse(JSON.stringify(this.emptyParamter))
      tmp.interface = this.currentInterface
      tmp.type = type
      this.interfaceParamter[type].push({
        ...tmp
      })
    },
    getObjectNameOptions () {
      const interfaceParamter = JSON.parse(JSON.stringify(this.interfaceParamter))
      this.inputObjectNameOptions = interfaceParamter.input.filter(p => p.dataType === 'object')
      this.outputObjectNameOptions = interfaceParamter.output.filter(p => p.dataType === 'object')
    },
    async getInterfaceParamter (interfaceSingleId) {
      console.log(interfaceSingleId)
      this.currentInterface = interfaceSingleId
      const { statusCode, data } = await getParamaByInterface(interfaceSingleId)
      if (statusCode === 'OK') {
        this.interfaceParamter.input = data.filter(d => d.type === 'input')
        this.interfaceParamter.output = data.filter(d => d.type === 'output')
        this.getObjectNameOptions()
        this.getTemplates()
      }
    },
    async getPluginInterface (pluginName) {
      let plugin = this.pluginOptions.find(plugin => plugin.name === pluginName[0])
      if (plugin) {
        const { statusCode, data } = await getInterfaceByPlugin(pluginName[0])
        if (statusCode === 'OK') {
          plugin.interfaces = data
        }
      }
    },
    addInterface (plugin) {
      this.newInterface = {
        isShow: true,
        isAdd: true,
        form: {
          name: '',
          plugin: plugin.name,
          description: ''
        }
      }
    },
    async confirmInterface () {
      const method = this.newInterface.isAdd ? addInterface : editInterface
      const { statusCode } = await method([this.newInterface.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getPluginInterface([this.newInterface.form.plugin])
      }
    },
    editPlugin (plugin) {
      this.newPlugin = {
        isShow: true,
        isAdd: false,
        form: {
          ...plugin
        }
      }
    },
    async confirmPlugin () {
      const method = this.newPlugin.isAdd ? addPlugin : editPlugin
      delete this.newPlugin.form.interfaces
      const { statusCode } = await method([this.newPlugin.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getPlugin([this.newInterface.form.plugin])
      }
    },
    editInterface (interfaceSingle) {
      this.newInterface = {
        isShow: true,
        isAdd: false,
        form: {
          ...interfaceSingle
        }
      }
    },
    deleteInterface (interfaceSingle, plugin) {
      this.$Modal.confirm({
        title: this.$t('t_confirm_delete'),
        'z-index': 1000000,
        loading: true,
        onOk: async () => {
          let res = await deleteInterface(interfaceSingle.id)
          this.$Modal.remove()
          if (res.statusCode === 'OK') {
            this.$Notice.success({
              title: 'Successful',
              desc: 'Successful'
            })
            this.getPluginInterface([plugin.name])
          }
        },
        onCancel: () => {}
      })
    },
    async getPlugin () {
      this.pluginOptions = []
      const { statusCode, data } = await getPluginList()
      if (statusCode === 'OK') {
        this.pluginOptions = data.map(d => {
          d.interfaces = []
          return d
        })
      }
    }
  }
}
</script>

<style scoped lang="scss"></style>
<style lang="scss">
.modal-paramsContainer {
  height: calc(100vh - 300px);
  .modal-interfaceContainers {
    overflow: auto;
    height: calc(100vh - 160px);
  }
  .ivu-form-item {
    margin-bottom: 2px;
  }
}
.plugin-register-page {
  .interfaceContainers {
    overflow: auto;
    height: calc(100vh - 450px);
  }
  .ivu-menu-vertical .ivu-menu-submenu-title {
    padding: 8px 0px;
  }
  .ivu-menu-vertical .ivu-menu-submenu-title-icon {
    right: 0;
  }
  .ivu-menu-vertical .ivu-menu-opened > * > .ivu-menu-submenu-title-icon {
    color: #2d8cf0;
  }
  .ivu-menu-opened {
    .ivu-menu-submenu-title {
      background: rgb(224, 230, 231);
      border-radius: 5px;
    }
  }
  .role-transfer-title {
    text-align: center;
    font-size: 13px;
    font-weight: 700;
    background-color: rgb(226, 222, 222);
    margin-bottom: 5px;
  }
}
</style>
