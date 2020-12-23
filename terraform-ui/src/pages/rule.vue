<template>
  <div class=" ">
    <DangerousPageTable :pageConfig="pageConfig"></DangerousPageTable>
    <Modal v-model="showAddRulesModal" :z-index="1051" :title="$t('match_value')" @on-ok="generateExpression()">
      <Form label-position="top" label-colon>
        <FormItem
          :label="$t('match_value')"
          v-if="['sql', 'text', 'fulltext'].includes(this.modelConfig.addRow.match_type)"
        >
          <Input v-model="addRulesModal.diyRules"></Input>
        </FormItem>
        <FormItem :label="$t('hr_service_name')" v-if="this.modelConfig.addRow.match_type === 'filter'">
          <Select v-model="addRulesModal.serviceName" @on-change="changeService" filterable style="width:475px">
            <Option
              v-for="service in addRulesModal.ruleConfig.serviceList"
              :value="service.serviceName"
              :key="service.serviceName"
              >{{ service.serviceName }}</Option
            >
          </Select>
          <!-- <Button @click="getRulesAttr('getRuleAttrByServiceName'), clearRuleResult()" type="success">获取配置</Button> -->
        </FormItem>
        <FormItem :label="$t('match_value')" v-if="this.addRulesModal.ruleConfig.attr.length > 0">
          <div style="margin: 4px 12px;padding:8px 12px;border:1px solid #dcdee2;border-radius:4px">
            <template v-for="(item, index) in addRulesModal.ruleResult">
              <p :key="index">
                <Button
                  @click="deleterule(index)"
                  size="small"
                  style="background-color: #ff9900;border-color: #ff9900;"
                  type="error"
                  icon="md-close"
                ></Button>
                <Select v-model="item.attr" filterable style="width:140px">
                  <Option v-for="attr in addRulesModal.ruleConfig.attr" :value="attr.value" :key="attr.value">{{
                    attr.name
                  }}</Option>
                </Select>
                <Select v-model="item.symbolValue" style="width:100px">
                  <Option v-for="rule in addRulesModal.ruleConfig.filterRuleOp" :value="rule" :key="rule">{{
                    rule
                  }}</Option>
                </Select>
                <Input
                  :disabled="setInputValue(item.symbolValue, index)"
                  v-model="item.inputValue"
                  style="width: 160px"
                  placeholder=""
                />
              </p>
            </template>
            <Button
              @click="addEmptyRule"
              type="success"
              size="small"
              style="background-color: #0080FF;border-color: #0080FF;"
              long
              >{{ $t('hr_add_rule') }}</Button
            >
          </div>
          <!-- </template> -->
        </FormItem>
      </Form>
    </Modal>
    <ModalComponent :modelConfig="modelConfig">
      <div slot="rule">
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('hr_level') }}:</label>
          <Select v-model="modelConfig.addRow.level" style="width: 338px">
            <Option v-for="item in modelConfig.v_select_configs.levelOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('effect_on') }}:</label>
          <Select v-model="modelConfig.addRow.effect_on" style="width: 338px" @on-change="changeEffectOn">
            <Option v-for="item in modelConfig.v_select_configs.effectOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('match_type') }}:</label>
          <Select v-model="modelConfig.addRow.match_type" style="width: 338px" @on-change="clearMatchValue">
            <Option v-for="item in matchOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('match_param_id') }}:</label>
          <Select
            v-model="modelConfig.addRow.match_param_id"
            :disabled="modelConfig.addRow.match_type === 'filter'"
            style="width: 338px"
            clearable
            @on-clear="modelConfig.addRow.match_param_id = ''"
            @on-change="clearMatchValue"
          >
            <Option v-for="item in modelConfig.v_select_configs.matchParamOption" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('match_value') }}:</label>
          <input
            v-model="modelConfig.addRow.match_value"
            disabled
            style="min-width:64%"
            class="col-md-6 form-control model-input"
          />
          <Button
            :disabled="disableRuleBtn"
            @click="configMatchValaue"
            size="small"
            style="background-color: #57a3f3;border-color: #57a3f3;"
            type="primary"
            icon="ios-create-outline"
          ></Button>
          <Button
            @click="modelConfig.addRow.match_value = ''"
            size="small"
            style="background-color: #ed4015;border-color: #ed4015;"
            type="primary"
            icon="md-close"
          ></Button>
        </div>
      </div>
    </ModalComponent>
  </div>
</template>

<script>
import {
  getTableData,
  addTableRow,
  editTableRow,
  deleteTableRow,
  getRuleAttrById,
  getService,
  getRuleAttrByServiceName
} from '@/api/server'
let tableEle = [
  {
    title: 'hr_name',
    value: 'name',
    display: true
  },
  {
    title: 'hr_description', // 不必
    value: 'description',
    display: true
  },
  {
    title: 'hr_enabled',
    value: 'enabled',
    display: true,
    render: item => {
      return item.enabled ? 'Yes' : 'No'
    }
  },
  {
    title: 'hr_level',
    value: 'level', // 优先级
    display: true
  },
  {
    title: 'effect_on',
    value: 'effect_on', // 作用域
    display: true
  },
  {
    title: 'match_type',
    value: 'match_type', // 匹配方式
    display: true
  },
  {
    title: 'match_value',
    value: 'match_value', // 匹配表达式
    display: true
  },
  {
    title: 'match_param_id', // 不必
    value: 'match_param.name', // 调用参数
    display: true
  },
  {
    title: 'hr_created_by',
    value: 'created_by', //
    display: true
  },
  {
    title: 'hr_created_time',
    value: 'created_time', //
    display: true
  },
  {
    title: 'hr_updated_by',
    value: 'updated_by', //
    display: true
  },
  {
    title: 'hr_updated_time',
    value: 'updated_time', //
    display: true
  }
]
const btn = [
  { btn_name: 'button.edit', btn_func: 'editF' },
  { btn_name: 'button.remove', btn_func: 'deleteConfirmModal' }
]
export default {
  name: '',
  data () {
    return {
      pageConfig: {
        CRUD: '/itsdangerous/ui/v1/rules',
        researchConfig: {
          input_conditions: [
            {
              value: 'name__icontains',
              type: 'input',
              placeholder: 'placeholder.input',
              style: ''
            }
          ],
          btn_group: [
            {
              btn_name: 'button.search',
              btn_func: 'search',
              class: 'btn-confirm-f',
              btn_icon: 'fa fa-search'
            },
            {
              btn_name: 'button.add',
              btn_func: 'add',
              class: 'btn-cancel-f',
              btn_icon: 'fa fa-plus'
            }
          ],
          filters: {
            search: ''
          }
        },
        table: {
          tableData: [],
          tableEle: tableEle,
          // filterMoreBtn: 'filterMoreBtn',
          primaryKey: 'guid',
          btn: btn,
          pagination: this.pagination,
          handleFloat: true
        },
        pagination: {
          total: 0,
          page: 1,
          size: 10
        }
      },
      modelConfig: {
        modalId: 'add_edit_Modal',
        modalTitle: 'hr_rule',
        isAdd: true,
        config: [
          {
            label: 'hr_name',
            value: 'name',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          { label: 'hr_description', value: 'description', placeholder: '', disabled: false, type: 'text' },
          { label: 'hr_enabled', value: 'enabled', placeholder: '', disabled: false, type: 'checkbox' },
          { name: 'rule', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: null,
          description: null,
          enabled: true,
          level: 'high',
          effect_on: 'script',
          match_type: 'cli',
          match_value: '',
          match_param_id: ''
        },
        v_select_configs: {
          levelOptions: [
            { label: 'critical', value: 'critical' },
            { label: 'high', value: 'high' },
            { label: 'medium', value: 'medium' },
            { label: 'low', value: 'low' }
          ],
          effectOptions: [
            { label: 'param', value: 'param' },
            { label: 'script', value: 'script' }
          ],
          matchParamOption: []
        },
        ruleConfig: {
          filterRuleOp: ['eq', 'neq', 'in', 'like', 'gt', 'lt', 'is', 'isnot'],
          attr: [
            { label: 'id', value: 'id' },
            { label: 'name', value: 'name' }
          ]
        },
        ruleResult: [{ attr: 'id', symbolValue: 'eq', inputValue: '123' }]
      },
      showAddRulesModal: false,
      addRulesModal: {
        serviceName: '', // filter时配置
        diyRules: '', // sql、text、fulltext时配置
        ruleConfig: {
          filterRuleOp: [
            'set',
            'notset',
            'is',
            'isnot',
            'like',
            'ilike',
            'eq',
            'neq',
            'regex',
            'iregex',
            'lt',
            'gt',
            'lte',
            'gte',
            'in',
            'notin'
          ],
          serviceList: [],
          attr: []
        },
        ruleResult: [{ attr: '', symbolValue: '', inputValue: '' }]
      },
      modelTip: {
        key: 'name',
        value: null
      },
      id: ''
    }
  },
  watch: {
    matchOptions: function (val) {
      this.modelConfig.addRow.match_type = val.length > 1 ? this.modelConfig.addRow.match_type || 'cli' : 'filter'
    },
    'modelConfig.addRow.match_type': function (val) {
      if (val !== 'filter' && val) {
        this.getConfigData()
      }
    }
  },
  computed: {
    disableRuleBtn: function () {
      if (this.modelConfig.addRow.match_type === 'cli') {
        if (!this.modelConfig.addRow.match_param_id) {
          return true
        }
      }
      return false
    },
    matchOptions: function () {
      let res = []
      if (this.modelConfig.addRow.effect_on === 'script') {
        res = [
          { label: 'cli', value: 'cli' },
          { label: 'sql', value: 'sql' },
          { label: 'text', value: 'text' },
          { label: 'fulltext', value: 'fulltext' }
        ]
      } else {
        res = [{ label: 'filter', value: 'filter' }]
      }
      return res
    }
  },
  mounted () {
    this.initTableData()
    this.getConfigData()
  },
  methods: {
    changeService () {
      this.getRulesAttr('getRuleAttrByServiceName')
      this.clearRuleResult()
    },
    clearRuleResult () {
      this.addRulesModal.ruleResult = []
    },
    clearMatchValue () {
      this.modelConfig.addRow.match_value = ''
    },
    async configMatchValaue () {
      await this.manageEditRules()
      // if (this.modelConfig.addRow.match_type === 'cli' && this.modelConfig.addRow.match_param_id) {
      //   this.getRulesAttr('getRuleAttrById')
      // }
      this.showAddRulesModal = true
    },
    async manageEditRules () {
      let editData = {
        match_type: this.modelConfig.addRow.match_type,
        match_value: this.modelConfig.addRow.match_value || ''
      }

      this.addRulesModal.ruleResult = []
      this.addRulesModal.serviceName = ''
      this.addRulesModal.diyRules = ''
      this.addRulesModal.ruleConfig.attr = []
      if (['sql', 'text', 'fulltext'].includes(editData.match_type)) {
        this.addRulesModal.diyRules = editData.match_value
        this.getConfigData()
      }
      if (editData.match_type === 'cli') {
        this.getRulesAttr('getRuleAttrById')
        let singleMatchValue = editData.match_value.split('}{')
        singleMatchValue[0] = singleMatchValue[0].substring(1)
        // eslint-disable-next-line no-unused-vars
        let lastRule = singleMatchValue[singleMatchValue.length - 1]
        lastRule = lastRule.substring(0, lastRule.lastIndexOf('}'))
        singleMatchValue[singleMatchValue.length - 1] = lastRule
        singleMatchValue.forEach(item => {
          const sRule = item.split(' ')
          this.addRulesModal.ruleResult.push({
            attr: sRule[0],
            symbolValue: sRule[1],
            inputValue: this.tirmComma(sRule[1], sRule[2])
          })
        })
      }
      if (editData.match_type === 'filter') {
        const { status, data } = await getService()
        if (status === 'OK') {
          this.addRulesModal.ruleConfig.serviceList = data.data
        }
        let singleMatchValue = editData.match_value.split('}{')
        singleMatchValue[0] = singleMatchValue[0].substring(1)
        // eslint-disable-next-line no-unused-vars
        let lastRule = singleMatchValue[singleMatchValue.length - 1]
        lastRule = lastRule.substring(0, lastRule.lastIndexOf('}'))
        singleMatchValue[singleMatchValue.length - 1] = lastRule
        singleMatchValue.forEach(item => {
          const sRule = item.split(' ')
          if (sRule[0] === 'serviceName') {
            this.addRulesModal.serviceName = sRule[2].substring(1, sRule[2].length - 1)
            this.getRulesAttr('getRuleAttrByServiceName')
          } else {
            this.addRulesModal.ruleResult.push({
              attr: sRule[0],
              symbolValue: sRule[1],
              inputValue: this.tirmComma(sRule[1], sRule[2])
            })
          }
        })
      }
    },
    tirmComma (op, val) {
      if (['like', 'ilike', 'eq', 'neq', 'regex', 'iregex'].includes(op)) {
        return val.substring(1, val.lastIndexOf("'")) || ''
      }
      return val || ''
    },
    async getRulesAttr (fun) {
      if (fun === 'getRuleAttrByServiceName') {
        this.addRulesModal.ruleResult = []
      }
      const { status, data } =
        fun === 'getRuleAttrByServiceName'
          ? await getRuleAttrByServiceName(this.addRulesModal.serviceName)
          : await getRuleAttrById(this.modelConfig.addRow.match_param_id)
      if (status === 'OK') {
        this.addRulesModal.ruleConfig.attr = data.data
      }
    },
    setInputValue (symbolValue, index) {
      if (['set', 'notset', 'is', 'isnot'].includes(symbolValue)) {
        this.addRulesModal.ruleResult[index].inputValue = 'NULL'
        return true
      } else {
        return false
      }
    },
    generateExpression () {
      if (['sql', 'text', 'fulltext'].includes(this.modelConfig.addRow.match_type)) {
        this.modelConfig.addRow.match_value = this.addRulesModal.diyRules
      }
      if (this.modelConfig.addRow.match_type === 'cli') {
        this.modelConfig.addRow.match_value = this.manageRuleResult()
      }
      if (this.modelConfig.addRow.match_type === 'filter') {
        let tmp = this.manageRuleResult()
        this.modelConfig.addRow.match_value = `{serviceName eq '${this.addRulesModal.serviceName}'}` + tmp
      }
    },
    manageRuleResult () {
      // eslint-disable-next-line no-unused-vars
      let serviceNameResult = ''
      this.addRulesModal.ruleResult.forEach(item => {
        if (item.attr && item.symbolValue) {
          if (['like', 'ilike', 'eq', 'neq', 'regex', 'iregex'].includes(item.symbolValue)) {
            serviceNameResult += `{${item.attr} ${item.symbolValue} '${item.inputValue}'}`
          } else {
            serviceNameResult += `{${item.attr} ${item.symbolValue} ${item.inputValue}}`
          }
        }
      })
      return serviceNameResult
    },
    addEmptyRule () {
      this.addRulesModal.ruleResult.push({ attr: '', symbolValue: '', inputValue: '' })
    },
    deleterule (index) {
      this.addRulesModal.ruleResult.splice(index, 1)
    },
    changeEffectOn () {
      this.modelConfig.addRow.match_type = ''
      this.modelConfig.addRow.match_value = ''
    },
    async initTableData () {
      const params = this.$itsCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    async getConfigData () {
      // eslint-disable-next-line no-unused-vars
      let params = ''
      if (this.modelConfig.addRow.match_type === 'cli') {
        params = '/itsdangerous/ui/v1/matchparams?type=cli'
      }
      if (['sql', 'text', 'fulltext'].includes(this.modelConfig.addRow.match_type)) {
        params = '/itsdangerous/ui/v1/matchparams?type=regex'
      }
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.modelConfig.v_select_configs.matchParamOption = data.data.map(item => {
          return {
            label: item.name,
            value: item.id
          }
        })
      }
    },
    async add () {
      this.modelConfig.addRow.enabled = true
      this.modelConfig.addRow.level = 'high'
      this.modelConfig.addRow.effect_on = 'script'
      this.modelConfig.addRow.match_type = 'cli'
      this.modelConfig.isAdd = true
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async addPost () {
      this.modelConfig.addRow.enabled = Number(this.modelConfig.addRow.enabled)
      const { status, message } = await addTableRow(this.pageConfig.CRUD, [this.modelConfig.addRow])
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    async editF (rowData) {
      this.id = rowData.id
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.modelConfig.addRow = this.$itsCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      this.modelConfig.addRow.enabled = Number(this.modelConfig.addRow.enabled)
      this.modelConfig.addRow.match_param_id = this.modelConfig.addRow.match_param_id || null
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: rowData.name,
        'z-index': 1000000,
        onOk: async () => {
          const { status, message } = await deleteTableRow(this.pageConfig.CRUD, rowData.id)
          if (status === 'OK') {
            this.initTableData()
            this.$Message.success(message)
          }
        },
        onCancel: () => {}
      })
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
