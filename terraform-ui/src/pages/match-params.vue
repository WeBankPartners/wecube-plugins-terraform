<template>
  <div class=" ">
    <DangerousPageTable :pageConfig="pageConfig"></DangerousPageTable>
    <Modal v-model="showAddRulesModal" :width="800" :z-index="1051" :title="$t('params')">
      <!-- @on-ok="generateExpression()" -->
      <Form label-position="right" label-colon>
        <FormItem v-if="modelConfig.addRow.type === 'regex'">
          <label class="col-md-2 label-name" style="text-align:right">{{ $t('params') }}:</label>
          <Input v-model="addRulesModal.regexParams" style="width:625px" placeholder="" />
        </FormItem>
        <template v-else>
          <FormItem>
            <label class="col-md-2 label-name" style="text-align:right">{{ $t('hr_name') }}:</label>
            <Input v-model="addRulesModal.name" style="width:625px" placeholder="" />
          </FormItem>
          <FormItem>
            <label class="col-md-2 label-name" style="text-align:right">{{ $t('strip_path') }}:</label>
            <i-switch v-model="addRulesModal.opt_strip_path" />
          </FormItem>
          <FormItem>
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
                  <Input v-model="item.name" style="width: 146px" :placeholder="$t('name')" />
                  <Input v-model="item.shortcut" style="width: 146px" placeholder="e.g:-f,-F,--force" />
                  <Select v-model="item.action" filterable style="width:140px">
                    <Option v-for="action in addRulesModal.ruleConfig.actionOption" :value="action" :key="action">{{
                      action
                    }}</Option>
                  </Select>
                  <i-switch size="large" v-model="item.convert_int" />
                  <Tooltip :content="$t('convert_int')">
                    <Icon type="md-help" />
                  </Tooltip>
                  <Select v-model="item.repeatable" filterable style="width:140px">
                    <Option
                      v-for="repeatable in addRulesModal.ruleConfig.repeatableOption"
                      :value="repeatable.value"
                      :key="repeatable.value"
                      >{{ repeatable.label }}</Option
                    >
                  </Select>
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
        </template>
      </Form>
      <div slot="footer">
        <Button @click="showAddRulesModal = false">{{ $t('button.cancel') }}</Button>
        <Button type="primary" @click="generateExpression">{{ $t('button.confirm') }}</Button>
      </div>
    </Modal>
    <ModalComponent :modelConfig="modelConfig">
      <template #match-params>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('hr_type') }}:</label>
          <Select v-model="modelConfig.addRow.type" @on-change="changeType" style="width: 338px">
            <Option v-for="item in modelConfig.v_select_configs.typeOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('params') }}:</label>
          <input v-model="modelConfig.addRow.params" disabled class="col-md-7 form-control model-input" />
          <Button
            @click="configMatchValaue"
            size="small"
            style="background-color: #57a3f3;border-color: #57a3f3;"
            type="primary"
            icon="ios-create-outline"
          ></Button>
        </div>
      </template>
    </ModalComponent>
  </div>
</template>

<script>
import { getTableData, addTableRow, editTableRow, deleteTableRow } from '@/api/server'
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
    title: 'params',
    value: 'params',
    display: true,
    render: item => {
      return JSON.stringify(item.params)
    }
  },
  {
    title: 'hr_type',
    value: 'type',
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
        CRUD: '/itsdangerous/ui/v1/matchparams',
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
        modalTitle: 'hr_match_params',
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
          { name: 'match-params', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: null,
          description: '',
          params: null,
          type: 'regex'
        },
        v_select_configs: {
          typeOptions: [
            { label: 'regex', value: 'regex' },
            { label: 'cli', value: 'cli' }
          ]
        }
      },
      showAddRulesModal: false,
      addRulesModal: {
        regexParams: '', // filter时配置
        name: '',
        opt_strip_path: true,
        ruleConfig: {
          actionOption: ['store', 'store_true', 'store_false', 'count', 'append'],
          repeatableOption: [
            { label: this.$t('repeatable_one'), value: 'null' },
            { label: this.$t('repeatable_two'), value: '?' },
            { label: this.$t('repeatable_three'), value: '+' },
            { label: this.$t('repeatable_four'), value: '*' }
          ]
        },
        ruleResult: [{ name: '', shortcut: '', action: 'store', convert_int: false, repeatable: 'null' }]
      },
      modelTip: {
        key: 'name',
        value: null
      },
      id: ''
    }
  },
  mounted () {
    this.initTableData()
  },
  methods: {
    changeType () {
      this.modelConfig.addRow.params = ''
    },
    async configMatchValaue () {
      await this.manageEditRules()
      this.showAddRulesModal = true
    },
    async manageEditRules () {
      this.addRulesModal.regexParams = ''
      this.addRulesModal.name = ''
      this.addRulesModal.ruleResult = []
      this.addRulesModal.opt_strip_path = true
      if (this.modelConfig.addRow.type === 'regex') {
        this.addRulesModal.regexParams = this.modelConfig.addRow.params
      } else {
        if (!this.modelConfig.addRow.params) return
        const rule = JSON.parse(this.modelConfig.addRow.params)
        rule.args.forEach(item => {
          if (item.repeatable === null) {
            item.repeatable = 'null'
          }
        })
        this.addRulesModal.name = rule.name
        this.addRulesModal.opt_strip_path = rule.opt_strip_path
        this.addRulesModal.ruleResult = rule.args
      }
    },
    generateExpression () {
      if (this.modelConfig.addRow.type === 'regex') {
        if (!this.addRulesModal.regexParams) {
          this.$Message.warning(this.$t('name_require'))
          this.showAddRulesModal = true
          return
        }
        this.modelConfig.addRow.params = this.addRulesModal.regexParams
        this.showAddRulesModal = false
      } else {
        const isEmpty = this.addRulesModal.ruleResult.some(item => item.name === '')
        if (!this.addRulesModal.name || isEmpty) {
          this.$Message.warning(this.$t('name_ex_require'))
          this.showAddRulesModal = true
          return
        }
        this.modelConfig.addRow.params = JSON.stringify({
          name: this.addRulesModal.name,
          opt_strip_path: this.addRulesModal.opt_strip_path,
          args: this.addRulesModal.ruleResult
        })
        this.showAddRulesModal = false
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
      this.addRulesModal.ruleResult.push({
        name: '',
        shortcut: '',
        action: 'store',
        convert_int: false,
        repeatable: 'null'
      })
    },
    deleterule (index) {
      this.addRulesModal.ruleResult.splice(index, 1)
    },
    async initTableData () {
      const params = this.$itsCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    add () {
      this.modelConfig.isAdd = true
      this.modelConfig.addRow.type = 'regex'
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async addPost () {
      this.beautifyData()
      const { status, message } = await addTableRow(this.pageConfig.CRUD, [this.modelConfig.addRow])
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    editF (rowData) {
      this.id = rowData.id
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.modelConfig.addRow = this.$itsCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      this.modelConfig.addRow.params = JSON.stringify(rowData.params)
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      this.beautifyData()
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    beautifyData () {
      this.modelConfig.addRow.params = JSON.parse(this.modelConfig.addRow.params)
      this.modelConfig.addRow.params.args.forEach(item => {
        if (item.repeatable === 'null') {
          item.repeatable = null
        }
      })
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
  components: {}
}
</script>

<style scoped lang="scss">
.ivu-form-item {
  margin-bottom: 0;
}
</style>
