<template>
  <div style="width: 100%;overflow: auto">
    <!-- 搜索区 -->
    <div>
      <Row>
        <Col span="5">
          <span>{{ $t('t_plugin') }}</span>
          <Select
            v-model="plugin"
            clearable
            @on-clear="currentInterface = ''"
            @on-change="currentInterface = ''"
            filterable
            style="width:200px"
          >
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
    <div
      :style="{
        'margin-top': '36px',
        'text-align': 'center',
        width: '1900px',
        overflow: 'auto',
        'max-height': MODALHEIGHT + 'px'
      }"
    >
      <header>
        <div style="font-size: 0">
          <div class="table-title title-width-level2">
            source
            <Button
              @click="addSource"
              :disabled="!plugin || !currentInterface || !currentProvider"
              type="success"
              ghost
              size="small"
              style="color: #19be6b;"
              icon="ios-add"
            ></Button>
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_name') }}
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_data_type') }}
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_parameter') }}
          </div>
          <div class="table-title title-width-level1">
            {{ $t('t_default_value') }}
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
          <div class="table-title title-width-level0">
            {{ $t('key_argument') }}
          </div>
          <div class="table-title title-width-level3" style="vertical-align: top;">
            <div style="line-height:40px">
              {{ $t('t_conversion') }}
            </div>
            <div style="font-size: 0;margin-top: -1px;margin-left:-1px">
              <div class="table-title title-width-level1 title-style">
                {{ $t('t_conversion_type') }}
              </div>
              <div class="table-title title-width-level1 title-style">
                {{ $t('t_related_params') }}
              </div>
              <div class="table-title title-width-level1 title-style">
                {{ $t('t_related_value') }}
              </div>
              <div class="table-title title-width-level1 title-style">
                关联source
              </div>
              <div class="table-title title-width-level1 title-style">
                {{ $t('t_related_attr') }}
              </div>
              <div class="table-title title-width-level1 title-style">
                {{ $t('function_define') }}
              </div>
            </div>
          </div>
          <div class="table-title title-width-level1" style="margin-left: 0px;position: relative;left: -1px;">
            {{ $t('t_action') }}
          </div>
        </div>
      </header>
      <div style="margin-left: 8px">
        <div
          v-for="(source, sourceIndex) in sourceInfo"
          :key="source.id"
          style="font-size: 0;margin-top:-1px;margin-left:-4px;"
        >
          <div class="style-widthout-height" style="font-size: 0;margin-left:-6px">
            <div
              class="style-widthout-height"
              :style="{
                width: '120px',
                height: (source.args.length + source.attrs.length) * 39 + 'px',
                overflow: 'hidden',
                padding: ((source.args.length + source.attrs.length) * 30) / 2 + 'px ' + ' 0',
                'text-overflow': 'ellipsis',
                'white-space': 'nowrap',
                'margin-top': '-1px'
              }"
            >
              <span :title="source.name" class="xx">
                {{ source.name }}
              </span>
              <div>
                <Button
                  @click="editSource(source)"
                  type="info"
                  ghost
                  size="small"
                  style="color: #19be6b;"
                  icon="ios-create-outline"
                ></Button>
                <Button
                  @click="deleteSource(source, sourceIndex)"
                  type="error"
                  ghost
                  size="small"
                  style="color: #ed4014;"
                  icon="md-trash"
                ></Button>
              </div>
            </div>
            <div class="style-widthout-height" style="width:120px;vertical-align: top;border:none">
              <div class="style-widthout-height" style="font-size: 0;margin-left:0px;border:none">
                <div
                  class="style-widthout-height"
                  :style="{ width: '120px', 'line-height': source.args.length * 39 - 1 + 'px', border: 'none' }"
                >
                  Arg
                  <Button
                    @click="addParams(source, 'args')"
                    type="success"
                    ghost
                    size="small"
                    style="color: #19be6b;"
                    icon="ios-add"
                  ></Button>
                </div>
                <div
                  class="attr-style-widthout-height"
                  :style="{
                    width: '120px',
                    'line-height': source.attrs.length * 39 - 1 + 'px',
                    'margin-left': '-1px',
                    'border-top': '1px solid #dcdee2'
                  }"
                >
                  Attr
                  <Button
                    @click="addParams(source, 'attrs')"
                    type="success"
                    ghost
                    size="small"
                    style="color: #19be6b;"
                    icon="ios-add"
                  ></Button>
                </div>
              </div>
            </div>
          </div>
          <div style="display:inline-block;vertical-align: top;margin-top:1px;margin-left:-1px;">
            <div>
              <div style="margin-top: -1px;" v-for="(item, argIndex) in source.args" :key="argIndex">
                <template>
                  <div class="table-col title-width-level1" style="margin-left: -1px">
                    <Input v-model="item.name" size="small" />
                  </div>
                  <div class="table-col title-width-level1">
                    <Select v-model="item.type" clearable filterable @on-clear="item.type = ''" size="small">
                      <Option v-for="item in dataTypeOptions" :value="item.value" :key="item.value">{{
                        item.label
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.parameter"
                      size="small"
                      clearable
                      @on-clear="item.parameter = ''"
                      filterable
                      @on-open-change="getInterfaceParamsWithTemplate(item)"
                    >
                      <template v-if="item.parameter && item.interfaceInputParamsWithTemplate.length === 0">
                        <Option :value="item.parameter" :key="item.parameter">{{ item.parameterTitle }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.interfaceInputParamsWithTemplate" :value="item.id" :key="item.id">{{
                          item.name
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.defaultValue"
                      @on-open-change="openDefaultValue(item, 'interfaceInputParamsWithTemplate')"
                      allow-create
                      @on-create="createDefaultValueOptions(item, $event)"
                      ref="sss"
                      clearable
                      @on-clear="item.defaultValue = ''"
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
                    <Select
                      v-model="item.objectName"
                      @on-clear="item.objectName = ''"
                      clearable
                      filterable
                      size="small"
                      @on-open-change="getArgsObjetcNameOptions(source, item)"
                    >
                      <template v-if="item.objectName && item.argsObjetcNameOptions.length === 0">
                        <Option :value="item.objectName" :key="item.objectName">{{ item.objectNameTitle }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.argsObjetcNameOptions" :value="item.id" :key="item.id">{{
                          item.name
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.isMulti" filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.isNull" filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.keyArgument" filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>

                  <div class="table-col title-width-level1" style="margin-left: -1px;">
                    <Select v-model="item.convertWay" @on-change="changeConverWay(item)" size="small">
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
                      :disabled="!['context_direct', 'context_data'].includes(item.convertWay)"
                      clearable
                      @on-clear="item.relativeParameter = ''"
                      filterable
                      @on-open-change="getInterfaceParamter(item)"
                      @on-change="getRelativeValueOptions(item, sourceIndex, 'args', argIndex)"
                      size="small"
                    >
                      <template v-if="item.relativeParameter && item.interfaceInputParams.length === 0">
                        <Option :value="item.relativeParameter" :key="item.relativeParameter">{{
                          item.relativeParameterTitle
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.interfaceInputParams" :value="item.id" :key="item.id">{{
                          item.name
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeParameterValue"
                      :disabled="!['context_direct', 'context_data'].includes(item.convertWay)"
                      @on-open-change="openRelativeParameterValue(item, 'interfaceInputParams')"
                      clearable
                      @on-clear="item.relativeParameterValue = ''"
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
                      v-model="item.relativeSource"
                      size="small"
                      :disabled="!['attribute', 'data', 'context_data'].includes(item.convertWay)"
                      clearable
                      @on-clear="item.relativeSource = ''"
                      filterable
                      @on-open-change="getSourceByProvider(item)"
                    >
                      <template v-if="item.relativeSource && item.sourceWithFilter.length === 0">
                        <Option :value="item.relativeSource" :key="item.relativeSource">{{
                          item.relativeSourceTitle
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.sourceWithFilter" :value="item.id" :key="item.id">{{
                          item.name
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeTfstateAttribute"
                      :disabled="!['attribute'].includes(item.convertWay)"
                      clearable
                      @on-clear="item.relativeTfstateAttribute = ''"
                      @on-open-change="getSourceAttrOptions(item, 'args')"
                      filterable
                      size="small"
                    >
                      <template v-if="item.relativeTfstateAttribute && item.sourceAttr.length === 0">
                        <Option :value="item.relativeTfstateAttribute" :key="item.relativeTfstateAttribute">{{
                          item.relativeTfstateAttributeTitle
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.sourceAttr" :value="item.id" :key="item.id"
                          >{{ item.name }} ({{ item.parameter }})</Option
                        >
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Input
                      v-model="item.functionDefine"
                      :disabled="!['function'].includes(item.convertWay)"
                      size="small"
                    />
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
              <div style="margin-top: -1px;" v-for="(item, attrIndex) in source.attrs" :key="attrIndex">
                <template>
                  <div class="table-col title-width-level1" style="margin-left: 0px">
                    <Input v-model="item.name" size="small" />
                  </div>
                  <div class="table-col title-width-level1">
                    <Select v-model="item.type" @on-clear="item.type = ''" clearable filterable size="small">
                      <Option v-for="item in dataTypeOptions" :value="item.value" :key="item.value">{{
                        item.label
                      }}</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1" style="margin-left: -1px;">
                    <Select
                      v-model="item.parameter"
                      size="small"
                      clearable
                      @on-clear="item.parameter = ''"
                      filterable
                      @on-open-change="getInterfaceParamsWithTemplate(item)"
                    >
                      <template v-if="item.parameter && item.interfaceOutputParamsWithTemplate.length === 0">
                        <Option :value="item.parameter" :key="item.parameter">{{ item.parameterTitle }}</Option>
                      </template>
                      <template v-else>
                        <Option
                          v-for="item in item.interfaceOutputParamsWithTemplate"
                          :value="item.id"
                          :key="item.id"
                          >{{ item.name }}</Option
                        >
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.defaultValue"
                      @on-open-change="openDefaultValue(item, 'interfaceOutputParamsWithTemplate')"
                      clearable
                      allow-create
                      @on-create="createDefaultValueOptions(item, $event)"
                      @on-clear="item.defaultValue = ''"
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
                    <Select
                      v-model="item.objectName"
                      @on-clear="item.objectName = ''"
                      clearable
                      filterable
                      size="small"
                      @on-open-change="getAttrsObjetcNameOptions(source, item)"
                    >
                      <template v-if="item.objectName && item.attrsObjetcNameOptions.length === 0">
                        <Option :value="item.objectName" :key="item.objectName">{{ item.objectNameTitle }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.attrsObjetcNameOptions" :value="item.id" :key="item.id">{{
                          item.name
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.isMulti" filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.isNull" filterable size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>
                  <div class="table-col title-width-level0">
                    <Select v-model="item.keyArgument" filterable disabled size="small">
                      <Option value="Y">Y</Option>
                      <Option value="N">N</Option>
                    </Select>
                  </div>

                  <div class="table-col title-width-level1" style="margin-left: -1px;">
                    <Select v-model="item.convertWay" @on-change="changeConverWay(item)" size="small">
                      <Option
                        v-for="item in conversionTypeOptions"
                        clearable
                        @on-clear="item.convertWay = ''"
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
                      :disabled="!['context_direct', 'context_data', 'context_attribute'].includes(item.convertWay)"
                      @on-open-change="getInterfaceParamter(item)"
                      clearable
                      @on-clear="item.relativeParameter = ''"
                      filterable
                      @on-change="getRelativeValueOptions(item, sourceIndex, 'attrs', attrIndex)"
                      size="small"
                    >
                      <template v-if="item.relativeParameter && item.interfaceOutputParams.length === 0">
                        <Option :value="item.relativeParameter" :key="item.relativeParameter">{{
                          item.relativeParameterTitle
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.interfaceOutputParams" :value="item.id" :key="item.id">{{
                          item.name
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeParameterValue"
                      :disabled="!['context_direct', 'context_data', 'context_attribute'].includes(item.convertWay)"
                      @on-open-change="openRelativeParameterValue(item, 'interfaceOutputParams')"
                      clearable
                      @on-clear="item.relativeParameterValue = ''"
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
                      v-model="item.relativeSource"
                      size="small"
                      :disabled="!['attribute', 'data', 'context_data', 'context_attribute'].includes(item.convertWay)"
                      @on-open-change="getSourceByProvider(item)"
                      clearable
                      @on-clear="item.relativeSource = ''"
                      filterable
                    >
                      <template v-if="item.relativeSource && item.sourceWithFilter.length === 0">
                        <Option :value="item.relativeSource" :key="item.relativeSource">{{
                          item.relativeSourceTitle
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.sourceWithFilter" :value="item.id" :key="item.id">{{
                          item.name
                        }}</Option>
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Select
                      v-model="item.relativeTfstateAttribute"
                      :disabled="!['attribute', 'context_attribute'].includes(item.convertWay)"
                      clearable
                      @on-clear="item.relativeTfstateAttribute = ''"
                      @on-open-change="getSourceAttrOptions(item, 'attrs')"
                      filterable
                      size="small"
                    >
                      <template v-if="item.relativeTfstateAttribute && item.sourceAttr.length === 0">
                        <Option :value="item.relativeTfstateAttribute" :key="item.relativeTfstateAttribute">{{
                          item.relativeTfstateAttributeTitle
                        }}</Option>
                      </template>
                      <template v-else>
                        <Option v-for="item in item.sourceAttr" :value="item.id" :key="item.id"
                          >{{ item.name }} ({{ item.parameter }})</Option
                        >
                      </template>
                    </Select>
                  </div>
                  <div class="table-col title-width-level1">
                    <Input
                      v-model="item.functionDefine"
                      :disabled="!['function'].includes(item.convertWay)"
                      size="small"
                    />
                  </div>
                  <div class="table-col title-width-level1">
                    <Button type="primary" @click="updateAttr(item, sourceIndex, attrIndex)" ghost size="small">{{
                      $t('t_save')
                    }}</Button>
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
    <Modal
      v-model="newSource.isShow"
      :title="(newSource.isAdd ? $t('t_add') : $t('t_add')) + $t('t_source')"
      @on-ok="confirmSource"
      @on-cancel="newSource.isShow = false"
    >
      <Form inline :label-width="100">
        <FormItem :label="$t('t_name')">
          <Input type="text" v-model="newSource.form.name" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_resource_asset_id_Attribute')">
          <Input type="text" v-model="newSource.form.assetIdAttribute" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('key_argument')">
          <Select v-model="newSource.form.terraformUsed" style="width:400px">
            <Option value="Y">Y</Option>
            <Option value="N">N</Option>
          </Select>
        </FormItem>
        <FormItem :label="$t('import_support')">
          <Select v-model="newSource.form.importSupport" style="width:400px">
            <Option value="Y">Y</Option>
            <Option value="N">N</Option>
          </Select>
        </FormItem>
        <FormItem :label="$t('source_type')">
          <Select v-model="newSource.form.sourceType" style="width:400px">
            <Option value="resource">resource</Option>
            <Option value="data_resource">data_resource</Option>
          </Select>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  getInterfaceByPlugin,
  addSource,
  editSource,
  deleteSource,
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

      plugin: '',
      pluginOptions: [],
      currentInterface: '',
      interfaceOptions: [],
      currentProvider: '',
      providerList: [],
      sourceInfo: [],
      dataTypeOptions: [
        { label: 'string', value: 'string' },
        { label: 'object', value: 'object' },
        { label: 'int', value: 'int' }
      ],
      conversionTypeOptions: [
        { label: 'direct', value: 'direct' },
        { label: 'data', value: 'data' },
        { label: 'attribute', value: 'attribute' },
        { label: 'template', value: 'template' },
        { label: 'context_direct', value: 'context_direct' },
        { label: 'context_template', value: 'context_template' },
        { label: 'context_data', value: 'context_data' },
        { label: 'context_attribute', value: 'context_attribute' },
        { label: 'function', value: 'function' }
      ],
      emptyParams: {
        convertWay: 'direct',
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
        argsObjetcNameOptions: [],
        attrsObjetcNameOptions: [],
        interfaceInputParams: [],
        interfaceOutputParams: [],
        sourceWithFilter: [],
        relativeValueOptions: [],
        sourceAttr: [],
        interfaceInputParamsWithTemplate: [],
        interfaceOutputParamsWithTemplate: [],
        source: '',
        type: '',
        updateTime: '',
        updateUser: '',
        functionDefine: '',
        keyArgument: 'N'
      },
      newSource: {
        isShow: false,
        isAdd: true,
        form: {
          name: '',
          terraformUsed: 'Y',
          plugin: '',
          provider: '',
          assetIdAttribute: '',
          importSupport: 'Y',
          sourceType: ''
        }
      }
    }
  },
  mounted () {
    this.getPlugin()
    this.getProviderList()
    this.MODALHEIGHT = document.body.scrollHeight - 200
  },
  methods: {
    changeConverWay (item) {
      item.relativeParameter = ''
      item.relativeParameterValue = ''
      item.relativeSource = ''
      item.relativeTfstateAttribute = ''
      item.functionDefine = ''
    },
    createDefaultValueOptions (item, el) {
      item.defaultValueOptions.push({
        value: el
      })
    },
    editSource (source) {
      this.newSource = {
        isShow: true,
        isAdd: false,
        form: {
          ...source
        }
      }
    },
    deleteSource (source, index) {
      this.$Modal.confirm({
        title: this.$t('t_confirm_delete'),
        'z-index': 1000000,
        loading: true,
        onOk: async () => {
          let res = await deleteSource(source.id)
          this.$Modal.remove()
          if (res.statusCode === 'OK') {
            this.$Notice.success({
              title: 'Successful',
              desc: 'Successful'
            })
            this.sourceInfo.splice(index, 1)
          }
        },
        onCancel: () => {}
      })
    },
    addSource () {
      this.newSource = {
        isShow: true,
        isAdd: true,
        form: {
          name: '',
          plugin: this.plugin,
          terraformUsed: 'Y',
          sourceType: '',
          interface: this.currentInterface,
          provider: this.currentProvider,
          importSupport: 'Y',
          resourceAssetIdAttribute: ''
        }
      }
    },
    async confirmSource () {
      const method = this.newSource.isAdd ? addSource : editSource
      const { statusCode } = await method([this.newSource.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getSource()
      }
    },
    addParams (source, type) {
      let tmp = JSON.parse(JSON.stringify(this.emptyParams))
      tmp.source = source.id
      source[type].push(tmp)
    },
    async openRelativeParameterValue (val, interfaceParams) {
      const find = this[interfaceParams].find(ip => ip.id === val.relativeParameter)
      if (find && find.template) {
        const { statusCode, data } = await getTemplateValue(find.template)
        if (statusCode === 'OK') {
          val.relativeValueOptions = data
        }
      } else {
        val.relativeValueOptions = []
      }
    },
    async openDefaultValue (item, interfaceParamsWithTemplate) {
      await this.getInterfaceParamsWithTemplate(item)
      const find = item[interfaceParamsWithTemplate].find(ip => ip.id === item.parameter)
      if (find && find.template) {
        const { statusCode, data } = await getTemplateValue(find.template)
        if (statusCode === 'OK') {
          const find = data.filter(d => d.value === item.defaultValue)
          if (find && find.length === 0) {
            data.push({
              value: item.defaultValue
            })
          }
          item.defaultValueOptions = data
        }
      } else {
        item.defaultValueOptions = []
      }
    },
    async updateAttr (item, sourceIndex, attrIndex) {
      let tmp = JSON.parse(JSON.stringify(item))
      const { statusCode, data } = await updateAttrs([tmp])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        item.id = data[0].id
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
      let tmp = JSON.parse(JSON.stringify(item))
      const { statusCode, data } = await updateArgs([tmp])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        item.id = data[0].id
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
    async getInterfaceParamsWithTemplate (item) {
      const { statusCode, data } = await getParamaByInterface(this.currentInterface)
      if (statusCode === 'OK') {
        item.interfaceInputParamsWithTemplate = data.filter(d => d.type === 'input')
        item.interfaceOutputParamsWithTemplate = data.filter(d => d.type === 'output')
      }
    },
    async getRelativeValueOptions (item, sourceIndex, type, index) {
      item.relativeParameterValue = ''
      if (type === 'args') {
        const find = item.interfaceInputParams.find(ip => ip.id === item.relativeParameter)
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
        const find = item.interfaceOutputParams.find(ip => ip.id === item.relativeParameter)
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
    async getSourceAttrOptions (item, type) {
      const { statusCode, data } = await getAttrBySource(item.relativeSource)
      if (statusCode === 'OK') {
        item.sourceAttr = data
      } else {
        item.sourceAttr = []
      }
    },
    async getSource () {
      const { statusCode, data } = await getSourceByfilter(this.currentInterface, this.currentProvider)
      if (statusCode === 'OK') {
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
    async getInterfaceParamter (item) {
      const { statusCode, data } = await getParamaByInterface(this.currentInterface)
      if (statusCode === 'OK') {
        item.interfaceInputParams = data.filter(d => d.type === 'input').filter(dd => dd.template !== '')
        item.interfaceOutputParams = data.filter(d => d.type === 'output').filter(dd => dd.template !== '')
      }
    },
    async getArgsObjetcNameOptions (source, item) {
      const arg = await getArgBySource(source.id)
      if (arg.statusCode === 'OK') {
        const argData = sortedArgument(arg.data)
        item.argsObjetcNameOptions = argData.filter(argSingle => argSingle.type === 'object')
      }
    },
    async getAttrsObjetcNameOptions (source, item) {
      const attr = await getAttrBySource(source.id)
      if (attr.statusCode === 'OK') {
        const attrData = sortedArgument(attr.data)
        item.attrsObjetcNameOptions = attrData.filter(attrSingle => attrSingle.type === 'object')
      }
    },
    async getSourceParams (source) {
      const arg = await getArgBySource(source.id)
      if (arg.statusCode === 'OK') {
        if (arg.data.length === 0) {
          let tmp = JSON.parse(JSON.stringify(this.emptyParams))
          tmp.source = source.id
          tmp.sourceWithFilter = []
          tmp.interfaceInputParams = []
          tmp.argsObjetcNameOptions = []
          tmp.relativeValueOptions = []
          tmp.defaultValueOptions = []
          tmp.interfaceInputParamsWithTemplate = []
          tmp.interfaceOutputParamsWithTemplate = []
          tmp.sourceAttr = []
          source.args.push(tmp)
        } else {
          const argData = sortedArgument(arg.data)
          source.args = argData.map(ar => {
            ar.sourceWithFilter = []
            ar.interfaceInputParams = []
            ar.argsObjetcNameOptions = []
            ar.relativeValueOptions = []
            ar.defaultValueOptions = []
            ar.interfaceInputParamsWithTemplate = []
            ar.interfaceOutputParamsWithTemplate = []
            ar.sourceAttr = []
            return ar
          })
        }
      }
      const attr = await getAttrBySource(source.id)
      if (attr.statusCode === 'OK') {
        if (attr.data.length === 0) {
          let tmp = JSON.parse(JSON.stringify(this.emptyParams))
          tmp.source = source.id
          tmp.sourceWithFilter = []
          tmp.interfaceOutputParams = []
          tmp.attrsObjetcNameOptions = []
          tmp.relativeValueOptions = []
          tmp.defaultValueOptions = []
          tmp.interfaceInputParamsWithTemplate = []
          tmp.interfaceOutputParamsWithTemplate = []
          tmp.sourceAttr = []
          source.attrs.push(tmp)
        } else {
          const attrData = sortedArgument(attr.data)
          source.attrsObjetcNameOptions = attrData.filter(attrSingle => attrSingle.type === 'object')
          source.attrs = attrData.map(at => {
            at.sourceWithFilter = []
            at.interfaceOutputParams = []
            at.attrsObjetcNameOptions = []
            at.relativeValueOptions = []
            at.defaultValueOptions = []
            at.interfaceInputParamsWithTemplate = []
            at.interfaceOutputParamsWithTemplate = []
            at.sourceAttr = []
            return at
          })
        }
      }
    },
    async getSourceByProvider (item) {
      const { statusCode, data } = await getSourceByProvider(this.currentProvider)
      if (statusCode === 'OK') {
        item.sourceWithFilter = data
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
        this.interfaceOptions = data.filter(d => d.name !== 'destroy')
      }
    }
  }
}
</script>

<style scoped lang="scss">
.title-style {
  height: 40px !important;
  line-height: 40px !important;
  vertical-align: text-bottom;
}
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
.attr-style-widthout-height {
  display: inline-block;
  font-size: 12px;
  margin-left: -1px;
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
  width: 715px;
}
.xx {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
