<template>
  <div class=" ">
    <!-- 搜索区 -->
    <div>
      <Row>
        <Col span="5">
          <span>{{ $t('t_plugin') }}</span>
          <Select v-model="plugin" clearable filterable style="width:200px">
            <Option v-for="item in pluginOptions" :value="item.id" :key="item.id">{{ item.name }}</Option>
          </Select>
        </Col>
        <Col span="5">
          <span>{{ $t('t_interface') }}</span>
          <Select
            v-model="currentInterface"
            clearable
            filterable
            @on-open-change="getPluginInterface"
            :disabled="!plugin"
            style="width:200px"
          >
            <Option v-for="item in interfaceOptions" :value="item.id" :key="item.id">{{ item.name }}</Option>
          </Select>
        </Col>
        <Col span="5">
          <span>{{ $t('t_provider') }}</span>
          <Select v-model="currentProvider" clearable filterable style="width:200px">
            <Option v-for="item in providerList" :value="item.id" :key="item.id">{{ item.name }}</Option>
          </Select>
        </Col>
        <Col span="5">
          <Button @click="getSource" :disabled="!plugin || !currentInterface || !currentProvider" type="primary">{{
            $t('t_search')
          }}</Button>
        </Col>
      </Row>
    </div>
    <!-- 配置区 -->
    <div style="margin-top: 36px; text-align: center;width:1800px;overflow:auto">
      <header>
        <div style="font-size: 0">
          <div class="table-title title-width-level2">
            source
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_name') }}
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_data_type') }}
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_object_name') }}
          </div>
          <div class="table-title title-width-level0">
            {{ $t('t_multiple') }}
          </div>
          <div class="table-title title-width-level0">
            {{ $t('t_is_null') }}
          </div>
          <div class="table-title title-width-level3" style="vertical-align: top;">
            <div style="line-height:40px">
              {{ $t('t_conversion') }}
            </div>
            <div style="font-size: 0;margin-top: -2px;">
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                {{ $t('t_conversion_type') }}
              </div>
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                {{ $t('t_related_params') }}
              </div>
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                {{ $t('t_related_value') }}
              </div>
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                关联source
              </div>
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                {{ $t('t_related_attr') }}
              </div>
            </div>
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_parameter') }}
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_default_value') }}
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_action') }}
          </div>
        </div>
      </header>
      <div :style="{ 'max-height': MODALHEIGHT + 'px', overflow: 'auto' }">
        <div
          v-for="(source, sourceIndex) in sourceInfo"
          :key="source.id"
          style="font-size: 0;margin-top:-1px;margin-left:-4px;"
        >
          <div class="style-widthout-height" style="font-size: 0;margin-left:-1px">
            <div
              class="style-widthout-height"
              :style="{
                width: '120px',
                'line-height': (source.args.length + source.attrs.length) * 39 + 'px',
                overflow: 'hidden',
                'text-overflow': 'ellipsis',
                'white-space': 'nowrap'
              }"
            >
              <span :title="source.name" class="xx">
                {{ source.name }}
              </span>
            </div>
            <div class="style-widthout-height" style="width:120px;vertical-align: top;border:none">
              <div class="style-widthout-height" style="font-size: 0;margin-left:-1px;border:none">
                <div
                  class="style-widthout-height"
                  :style="{ width: '120px', 'line-height': source.args.length * 39 + 'px' }"
                >
                  Arg
                  <Button @click="addParams(source, 'args')" type="primary" ghost size="small" icon="ios-add"></Button>
                </div>
                <div
                  class="style-widthout-height"
                  :style="{ width: '120px', 'line-height': source.attrs.length * 39 + 'px' }"
                >
                  Attr
                  <Button @click="addParams(source, 'attrs')" type="primary" ghost size="small" icon="ios-add"></Button>
                </div>
              </div>
            </div>
          </div>
          <div style="display:inline-block;vertical-align: top;margin-top:1px;margin-letf:-1px;">
            <div>
              <div style="margin-top: -1px;" v-for="(item, argIndex) in source.args" :key="item.id">
                <template>
                  <div class="table-col title-width-level1">
                    <Input v-model="item.name" size="small" />
                  </div>
                  <div class="table-col title-width-level1">
                    <Select v-model="item.type" clearable filterable size="small">
                      <Option v-for="item in dataTypeOptions" :value="item.value" :key="item.value">{{
                        item.label
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select v-model="item.objectName" clearable filterable size="small">
                      <Option v-for="item in source.argsObjetcNameOptions" :value="item.id" :key="item.id">{{
                        item.name
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.isMulti" clearable filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.isNull" clearable filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>

                  <div class="table-col title-width-level1">
                    <Select v-model="item.convertWay" size="small">
                      <Option
                        v-for="item in conversionTypeOptions"
                        clearable
                        filterable
                        :value="item.value"
                        :key="item.value"
                        >{{ item.label }}</Option
                      >
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeParameter"
                      :disabled="!['context', 'context_data'].includes(item.convertWay)"
                      clearable
                      filterable
                      @on-change="getRelativeValueOptions(item, sourceIndex, 'args', argIndex)"
                      size="small"
                    >
                      <Option v-for="item in interfaceInputParams" :value="item.id" :key="item.id">{{
                        item.name
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeParameterValue"
                      :disabled="!['context', 'context_data'].includes(item.convertWay)"
                      @on-open-change="openRelativeParameterValue(item, 'interfaceInputParams')"
                      clearable
                      filterable
                      size="small"
                    >
                      <template v-if="item.relativeParameterValue && item.relativeValueOptions.length === 0">
                        <Option :value="item.relativeParameterValue" :key="item.relativeParameterValue">{{
                          item.relativeParameterValue
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="pv in item.relativeValueOptions" :value="pv.value" :key="pv.value">{{
                          pv.value
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.source"
                      size="small"
                      :disabled="!['attr'].includes(item.convertWay)"
                      clearable
                      filterable
                      @on-change="getSourceAttrOptions(item, sourceIndex, 'args', argIndex)"
                    >
                      <Option v-for="item in sourceWithFilter" :value="item.id" :key="item.id">{{ item.name }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeTfstateAttribute"
                      :disabled="!['attr'].includes(item.convertWay)"
                      clearable
                      filterable
                      size="small"
                    >
                      <template v-if="item.relativeTfstateAttribute && item.sourceAttr.length === 0">
                        <Option :value="item.relativeTfstateAttribute" :key="item.relativeTfstateAttribute">{{
                          item.relativeTfstateAttribute
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.sourceAttr" :value="item.id" :key="item.id">{{ item.name }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.parameter"
                      size="small"
                      clearable
                      filterable
                      @on-change="getDefaultValueOptions(item, sourceIndex, 'args', argIndex)"
                    >
                      <Option v-for="item in interfaceInputParamsWithTemplate" :value="item.id" :key="item.id">{{
                        item.name
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.defaultValue"
                      @on-open-change="openDefaultValue(item, 'interfaceInputParamsWithTemplate')"
                      allow-create
                      ref="sss"
                      clearable
                      filterable
                      size="small"
                    >
                      <template v-if="item.defaultValue && item.defaultValueOptions.length === 0">
                        <Option :value="item.defaultValue" :key="item.defaultValue">{{ item.defaultValue }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.defaultValueOptions" :value="item.value" :key="item.value">{{
                          item.value
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Button type="primary" @click="updateArg(item, argIndex)" ghost size="small">{{
                      $t('t_save')
                    }}</Button>
                    <Button type="error" @click="deleteArg(source.args, item, argIndex)" ghost size="small">{{
                      $t('t_delete')
                    }}</Button>
                  </div>
                </template>
              </div>
            </div>
            <div>
              <div style="margin-top: -1px;" v-for="(item, attrIndex) in source.attrs" :key="item.id">
                <template>
                  <div class="table-col title-width-level1">
                    <Input v-model="item.name" size="small" />
                  </div>
                  <div class="table-col title-width-level1">
                    <Select v-model="item.type" clearable filterable size="small">
                      <Option v-for="item in dataTypeOptions" :value="item.value" :key="item.value">{{
                        item.label
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select v-model="item.objectName" clearable filterable size="small">
                      <Option v-for="item in source.attrsObjetcNameOptions" :value="item.id" :key="item.id">{{
                        item.name
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.isMulti" clearable filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.isNull" clearable filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>

                  <div class="table-col title-width-level1">
                    <Select v-model="item.convertWay" size="small">
                      <Option
                        v-for="item in conversionTypeOptions"
                        clearable
                        filterable
                        :value="item.value"
                        :key="item.value"
                        >{{ item.label }}</Option
                      >
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeParameter"
                      :disabled="!['context', 'context_data'].includes(item.convertWay)"
                      clearable
                      filterable
                      @on-change="getRelativeValueOptions(item, sourceIndex, 'attrs', attrIndex)"
                      size="small"
                    >
                      <Option v-for="item in interfaceOutputParams" :value="item.id" :key="item.id">{{
                        item.name
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeParameterValue"
                      :disabled="!['context', 'context_data'].includes(item.convertWay)"
                      @on-open-change="openRelativeParameterValue(item, 'interfaceOutputParams')"
                      clearable
                      filterable
                      size="small"
                    >
                      <template v-if="item.relativeParameterValue && item.relativeValueOptions.length === 0">
                        <Option :value="item.relativeParameterValue" :key="item.relativeParameterValue">{{
                          item.relativeParameterValue
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="pv in item.relativeValueOptions" :value="pv.value" :key="pv.value">{{
                          pv.value
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.source"
                      size="small"
                      :disabled="!['attr'].includes(item.convertWay)"
                      clearable
                      filterable
                    >
                      <Option v-for="item in sourceWithFilter" :value="item.id" :key="item.id">{{ item.name }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select v-model="item.relativeTfstateAttribute" disabled clearable filterable size="small">
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.parameter"
                      size="small"
                      clearable
                      filterable
                      @on-change="getDefaultValueOptions(item, sourceIndex, 'attrs', attrIndex)"
                    >
                      <Option v-for="item in interfaceOutputParamsWithTemplate" :value="item.id" :key="item.id">{{
                        item.name
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.defaultValue"
                      @on-open-change="openDefaultValue(item, 'interfaceOutputParamsWithTemplate')"
                      clearable
                      filterable
                      size="small"
                    >
                      <template v-if="item.defaultValue && item.defaultValueOptions.length === 0">
                        <Option :value="item.defaultValue" :key="item.defaultValue">{{ item.defaultValue }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.defaultValueOptions" :value="item.value" :key="item.value">{{
                          item.value
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Button type="primary" @click="updateAttr(item)" ghost size="small">{{ $t('t_save') }}</Button>
                    <Button type="error" @click="deleteAttr(source.attrs, item, attrIndex)" ghost size="small">{{
                      $t('t_delete')
                    }}</Button>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  getInterfaceByPlugin,
  getProviderList,
  getArgBySource,
  getTemplateValue,
  getAttrBySource,
  getSourceByfilter,
  updateArgs,
  deleteArg,
  updateAttrs,
  deleteAttrs,
  getSourceByProvider,
  getParamaByInterface,
  getPluginList
} from '@/api/server'
import sortedArgument from '@/pages/util/sort-array'
export default {
  name: '',
  data () {
    return {
      MODALHEIGHT: 300,

      plugin: 'cvm',
      pluginOptions: [],
      currentInterface: 'cvm__apply',
      interfaceOptions: [],
      currentProvider: 'tencentcloud',
      providerList: [],
      sourceInfo: [],
      dataTypeOptions: [
        { label: 'string', value: 'string' },
        { label: 'object', value: 'object' },
        { label: 'int', value: 'int' }
      ],
      conversionTypeOptions: [
        { label: 'data', value: 'data' },
        { label: 'temp', value: 'temp' },
        { label: 'context', value: 'context' },
        { label: 'context_data', value: 'context_data' },
        { label: 'attr', value: 'attr' },
        { label: 'direct', value: 'direct' }
      ],
      interfaceInputParams: [],
      interfaceOutputParams: [],
      interfaceInputParamsWithTemplate: [], // 供arg parameter 使用
      interfaceOutputParamsWithTemplate: [], // 供attr parameter 使用
      sourceWithFilter: [], // 关联source列表，依据provider过滤
      emptyParams: {
        convertWay: '',
        createTime: '',
        createUser: '',
        defaultValue: '',
        defaultValueOptions: [],
        id: '',
        isMulti: 'N',
        isNull: 'N',
        name: '',
        objectName: '',
        parameter: '',
        relativeParameter: '',
        relativeParameterValue: '',
        relativeSource: '',
        relativeTfstateAttribute: '',
        relativeValueOptions: [],
        source: '',
        sourceAttr: [],
        type: '',
        updateTime: '',
        updateUser: ''
      }
    }
  },
  mounted () {
    this.getPlugin()
    this.getProviderList()
    this.MODALHEIGHT = window.innerHeight - 300
  },
  methods: {
    // createOption (item, argIndex) {
    //   const query = this.$refs.sss[argIndex].query
    //   item.defaultValueOptions.push({
    //     id:
    //   })
    //   console.log(item)
    // },
    addParams (source, type) {
      source[type].push(JSON.parse(JSON.stringify(this.emptyParams)))
    },
    async openRelativeParameterValue (val, interfaceParams) {
      const find = this[interfaceParams].find(ip => ip.id === val.relativeParameter)
      if (find && find.template) {
        const { statusCode, data } = await getTemplateValue(find.template)
        if (statusCode === 'OK') {
          val.relativeValueOptions = data
        }
      }
    },
    async openDefaultValue (val, interfaceParamsWithTemplate) {
      const find = this.interfaceInputParamsWithTemplate.find(ip => ip.id === val.parameter)
      console.log(find)
      if (find) {
        const { statusCode, data } = await getTemplateValue(find.template)
        if (statusCode === 'OK') {
          const find = data.filter(d => d.value === val.defaultValue)
          console.log(find)
          if (find.length === 0) {
            data.push({
              value: val.defaultValue
            })
          }
          val.defaultValueOptions = data
          console.log(val.defaultValueOptions)
        }
      }
    },
    async updateAttr (item) {
      let tmp = JSON.parse(JSON.stringify(item))
      const { statusCode } = await updateAttrs([tmp])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
      }
    },
    async deleteAttr (attrs, item, index) {
      this.$Modal.confirm({
        title: this.$t('t_confirm_delete'),
        'z-index': 1000000,
        loading: true,
        onOk: async () => {
          let res = await deleteAttrs(item.id)
          this.$Modal.remove()
          if (res.statusCode === 'OK') {
            this.$Notice.success({
              title: 'Successful',
              desc: 'Successful'
            })
            attrs.splice(index, 1)
          }
        },
        onCancel: () => {}
      })
    },
    async updateArg (item, index) {
      const defaultValue = this.$refs.sss[index].query
      console.log(defaultValue)
      console.log(item)
      if (defaultValue) {
        item.defaultValue = defaultValue
      }
      let tmp = JSON.parse(JSON.stringify(item))
      const { statusCode } = await updateArgs([tmp])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
      }
    },
    async deleteArg (args, item, index) {
      this.$Modal.confirm({
        title: this.$t('t_confirm_delete'),
        'z-index': 1000000,
        loading: true,
        onOk: async () => {
          let res = await deleteArg(item.id)
          this.$Modal.remove()
          if (res.statusCode === 'OK') {
            this.$Notice.success({
              title: 'Successful',
              desc: 'Successful'
            })
            args.splice(index, 1)
          }
        },
        onCancel: () => {}
      })
    },
    async getDefaultValueOptions (val, sourceIndex, type, index) {
      val.defaultValue = ''
      if (type === 'args') {
        const find = this.interfaceInputParamsWithTemplate.find(ip => ip.id === val.parameter)
        if (find) {
          const { statusCode, data } = await getTemplateValue(find.template)
          if (statusCode === 'OK') {
            this.sourceInfo[sourceIndex][type][index].defaultValueOptions = data
          }
        }
      }
      if (type === 'attrs') {
        const find = this.interfaceOutputParamsWithTemplate.find(ip => ip.id === val.parameter)
        if (find) {
          const { statusCode, data } = await getTemplateValue(find.template)
          if (statusCode === 'OK') {
            this.sourceInfo[sourceIndex][type][index].defaultValueOptions = data
          }
        }
      }
    },
    async getRelativeValueOptions (val, sourceIndex, type, index) {
      val.relativeParameterValue = ''
      if (type === 'args') {
        const find = this.interfaceInputParams.find(ip => ip.id === val.relativeParameter)
        if (find && find.template) {
          const { statusCode, data } = await getTemplateValue(find.template)
          if (statusCode === 'OK') {
            this.sourceInfo[sourceIndex][type][index].relativeValueOptions = data
          }
        } else {
          this.sourceInfo[sourceIndex][type][index].relativeValueOptions = []
        }
      }
      if (type === 'attrs') {
        const find = this.interfaceOutputParams.find(ip => ip.id === val.relativeParameter)
        if (find && find.template) {
          const { statusCode, data } = await getTemplateValue(find.template)
          if (statusCode === 'OK') {
            this.sourceInfo[sourceIndex][type][index].relativeValueOptions = data
          }
        } else {
          this.sourceInfo[sourceIndex][type][index].relativeValueOptions = []
        }
      }
    },
    async getSourceAttrOptions (val, sourceIndex, type, index) {
      val.relativeTfstateAttribute = ''
      if (type === 'args') {
        const { statusCode, data } = await getAttrBySource(val.source)
        if (statusCode === 'OK') {
          this.sourceInfo[sourceIndex][type][index].sourceAttr = data
        }
      } else {
        this.sourceInfo[sourceIndex][type][index].sourceAttr = []
      }
    },
    async getSource () {
      const { statusCode, data } = await getSourceByfilter(this.currentInterface, this.currentProvider)
      if (statusCode === 'OK') {
        this.getInterfaceParamter()
        this.getSourceByProvider()
        this.sourceInfo = data.map(d => {
          d.args = []
          d.attrs = []
          return d
        })

        this.sourceInfo.forEach(source => {
          this.getSourceParams(source)
        })
      }
    },
    async getSourceParams (source) {
      this.getInterfaceParamter()
      const arg = await getArgBySource(source.id)
      if (arg.statusCode === 'OK') {
        const argData = sortedArgument(arg.data)
        source.argsObjetcNameOptions = argData.filter(argSingle => argSingle.type === 'object')
        source.args = argData.map(ar => {
          ar.relativeValueOptions = []
          ar.defaultValueOptions = []
          ar.sourceAttr = []
          return ar
        })
      }
      const attr = await getAttrBySource(source.id)
      if (attr.statusCode === 'OK') {
        const attrData = sortedArgument(attr.data)
        source.attrsObjetcNameOptions = attrData.filter(attrSingle => attrSingle.type === 'object')
        source.attrs = attrData.map(at => {
          at.relativeValueOptions = []
          at.defaultValueOptions = []
          at.sourceAttr = []
          return at
        })
      }
    },
    async getSourceByProvider () {
      this.sourceWithFilter = []
      const { statusCode, data } = await getSourceByProvider(this.currentProvider)
      if (statusCode === 'OK') {
        this.sourceWithFilter = data
      }
    },
    async getInterfaceParamter () {
      const { statusCode, data } = await getParamaByInterface(this.currentInterface)
      if (statusCode === 'OK') {
        this.interfaceInputParams = data.filter(d => d.type === 'input')
        this.interfaceOutputParams = data.filter(d => d.type === 'output')
        this.interfaceInputParamsWithTemplate = this.interfaceInputParams.filter(d => d.template !== '')
        this.interfaceOutputParamsWithTemplate = this.interfaceOutputParams.filter(d => d.template !== '')
      }
    },
    async getProviderList () {
      this.providerList = []
      const { statusCode, data } = await getProviderList()
      if (statusCode === 'OK') {
        this.providerList = data
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
  }
}
</script>

<style scoped lang="scss">
.table-title {
  display: inline-block;
  border: 1px solid #e9e9e9;
  font-size: 12px;
  margin-left: -1px;
  height: 80px;
  line-height: 80px;
  // width: 250px;
  // padding: 8px 4px;
  font-weight: bold;
  color: #515a6e;
  font-size: 14px;
}
.table-col {
  display: inline-block;
  border: 1px solid #e9e9e9;
  font-size: 12px;
  margin-left: -1px;
  height: 40px;
  // width: 250px;
  padding: 8px 4px;
  font-weight: bold;
  color: #515a6e;
  font-size: 14px;
}
.style-widthout-height {
  display: inline-block;
  border: 1px solid #e9e9e9;
  font-size: 12px;
  margin-left: -1px;
  // padding: 8px 4px;
  font-weight: bold;
  color: #515a6e;
  font-size: 14px;
}
.title-width-level0 {
  width: 60px;
}
.title-width-level1 {
  width: 120px;
}
.title-width-level2 {
  width: 240px;
}
.title-width-level3 {
  width: 600px;
}
.xx {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
