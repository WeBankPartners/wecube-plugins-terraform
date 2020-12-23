<template>
  <div class=" ">
    <DangerousPageTable :pageConfig="pageConfig"></DangerousPageTable>
    <Modal v-model="showAddRulesModal" :z-index="1051" :title="$t('args_scope')" @on-ok="generateExpression()">
      <Form label-position="top" label-colon>
        <FormItem :label="$t('hr_service_name')">
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
                  style="width: 146px"
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
        </FormItem>
      </Form>
    </Modal>
    <ModalComponent :modelConfig="modelConfig">
      <div slot="rule">
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('args_scope') }}:</label>
          <input
            v-model="modelConfig.addRow.args_scope"
            style="min-width:61%"
            disabled
            class="col-md-6 form-control model-input"
          />
          <Button
            @click="configMatchValaue"
            size="small"
            style="background-color: #57a3f3;border-color: #57a3f3;"
            type="primary"
            icon="ios-create-outline"
          ></Button>
          <Button
            @click="modelConfig.addRow.args_scope = ''"
            size="small"
            style="background-color: #ed4015;border-color: #ed4015;"
            type="primary"
            icon="md-close"
          ></Button>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('entity_scope') }}:</label>
          <FilterRules
            style="display:inline-block;vertical-align: middle;padding:0"
            class="col-md-9"
            :needAttr="true"
            v-model="modelConfig.addRow.entity_scope"
            :allDataModelsWithAttrs="allEntityType"
          ></FilterRules>
        </div>
      </div>
    </ModalComponent>
  </div>
</template>

<script>
import FilterRules from './components/filter-rules.vue'
import {
  getTableData,
  addTableRow,
  editTableRow,
  deleteTableRow,
  getService,
  getRuleAttrByServiceName,
  getAllDataModels
} from '@/api/server'
let tableEle = [
  {
    title: 'hr_name',
    value: 'name',
    display: true
  },
  {
    title: 'args_scope', // 不必
    value: 'args_scope', // 过滤规则  *****
    display: true
  },
  {
    title: 'entity_scope', // 不必
    value: 'entity_scope', // 实体类型
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
        CRUD: '/itsdangerous/ui/v1/targets',
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
        modalTitle: 'hr_target',
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
          { label: 'hr_enabled', value: 'enabled', placeholder: '', disabled: false, type: 'checkbox' },
          { name: 'rule', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: null,
          args_scope: null,
          entity_scope: null,
          enabled: true
        }
      },
      showAddRulesModal: false,
      addRulesModal: {
        serviceName: '', // filter时配置
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
      id: '',
      routineExpression: '',
      allEntityType: []
    }
  },
  mounted () {
    this.initTableData()
  },
  methods: {
    changeService () {
      this.getRulesAttr('getRuleAttrByServiceName')
      this.clearRuleResult()
    },
    async getAllDataModels () {
      let { data, status } = await getAllDataModels()
      if (status === 'OK') {
        this.allEntityType = data
      }
    },
    // 规则配置函数-开始
    generateExpression () {
      let tmp = this.manageRuleResult()
      this.modelConfig.addRow.args_scope = `{serviceName eq '${this.addRulesModal.serviceName}'}` + tmp
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
    setInputValue (symbolValue, index) {
      if (['set', 'notset', 'is', 'isnot'].includes(symbolValue)) {
        this.addRulesModal.ruleResult[index].inputValue = 'NULL'
        return true
      } else {
        return false
      }
    },
    addEmptyRule () {
      this.addRulesModal.ruleResult.push({ attr: '', symbolValue: '', inputValue: '' })
    },
    deleterule (index) {
      this.addRulesModal.ruleResult.splice(index, 1)
    },
    clearRuleResult () {
      this.addRulesModal.ruleResult = []
    },
    async getRulesAttr () {
      this.addRulesModal.ruleResult = []
      const { status, data } = await getRuleAttrByServiceName(this.addRulesModal.serviceName)
      if (status === 'OK') {
        this.addRulesModal.ruleConfig.attr = data.data
      }
    },
    async configMatchValaue () {
      await this.manageEditRules()
      this.showAddRulesModal = true
    },
    async manageEditRules () {
      this.addRulesModal.ruleResult = []
      this.addRulesModal.serviceName = ''
      this.addRulesModal.ruleConfig.attr = []
      const { status, data } = await getService()
      if (status === 'OK') {
        this.addRulesModal.ruleConfig.serviceList = data.data
      }
      if (!this.modelConfig.addRow.args_scope) return
      let singleMatchValue = this.modelConfig.addRow.args_scope.split('}{')
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
    },
    tirmComma (op, val) {
      if (['like', 'ilike', 'eq', 'neq', 'regex', 'iregex'].includes(op)) {
        return val.substring(1, val.lastIndexOf("'")) || ''
      }
      return val || ''
    },
    // 规则配置函数-结束
    async initTableData () {
      const params = this.$itsCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    async add () {
      this.modelConfig.addRow.enabled = true
      this.modelConfig.isAdd = true
      await this.getAllDataModels()
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
      await this.getAllDataModels()
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      this.modelConfig.addRow.enabled = Number(this.modelConfig.addRow.enabled)
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: this.$t('delete_confirm') + rowData.name,
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
  components: {
    FilterRules
  }
}
</script>

<style scoped lang="scss"></style>
