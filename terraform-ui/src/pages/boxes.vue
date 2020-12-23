<template>
  <div class=" ">
    <DangerousPageTable :pageConfig="pageConfig"></DangerousPageTable>
    <ModalComponent :modelConfig="modelConfig">
      <template #boxes>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('hr_policies') }}:</label>
          <Select v-model="modelConfig.addRow.policy_id" style="width: 338px">
            <Option v-for="item in modelConfig.v_select_configs.policyOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('hr_subject') }}:</label>
          <Select v-model="modelConfig.addRow.subject_id" style="width: 338px">
            <Option v-for="item in modelConfig.v_select_configs.subjectOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
        </div>
      </template>
    </ModalComponent>
    <ModalComponent :modelConfig="detectConfig">
      <template #scriptType>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('hr_type') }}:</label>
          <Select v-model="detectConfig.addRow.type" style="width: 70%">
            <Option v-for="item in detectConfig.v_select_configs.typeOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
        </div>
      </template>
      <template #detectBtn>
        <div style="text-align: right">
          <button type="button" @click="exectDetect" style="margin: 8px 122px" class="btn btn-sm btn-confirm-f">
            {{ $t('detect') }}
          </button>
        </div>
        <DangerousPageTable :pageConfig="exectPageConfig"></DangerousPageTable>
      </template>
    </ModalComponent>
  </div>
</template>

<script>
import { getTableData, addTableRow, editTableRow, deleteTableRow, boxDetect } from '@/api/server'
let tableEle = [
  {
    title: 'hr_name',
    value: 'name', //
    display: true
  },
  {
    title: 'hr_description', // 不必
    value: 'description', //
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
    title: 'hr_policies',
    value: 'policy.name', //
    display: true
  },
  {
    title: 'hr_subject',
    value: 'subject.name', //
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
  { btn_name: 'detect', btn_func: 'detectF' },
  { btn_name: 'button.remove', btn_func: 'deleteConfirmModal' }
]
export default {
  name: '',
  data () {
    return {
      pageConfig: {
        CRUD: '/itsdangerous/ui/v1/boxes',
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
      exectPageConfig: {
        table: {
          tableData: [],
          tableEle: [
            {
              title: 'hr_level',
              value: 'level', //
              display: true,
              style: 'width: 80px;'
            },
            {
              title: 'lineno',
              value: 'lineno', //
              display: true,
              style: 'width: 80px;'
            },
            {
              title: 'message',
              value: 'message', //
              display: true,
              style: 'width:120px'
            },
            {
              title: 'script_name',
              value: 'script_name', //
              display: true
            },
            {
              title: 'content',
              value: 'content', //
              display: true
            }
          ],
          primaryKey: 'guid',
          btn: []
        }
      },
      modelConfig: {
        modalId: 'add_edit_Modal',
        modalTitle: 'hr_box',
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
          { name: 'boxes', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: null,
          enabled: true,
          description: null,
          policy_id: null,
          subject_id: null
        },
        v_select_configs: {
          policyOptions: [],
          subjectOptions: []
        }
      },
      detectConfig: {
        modalId: 'detect_Modal',
        modalTitle: 'detect',
        isAdd: true,
        noBtn: true,
        modalStyle: 'max-width:1000px',
        config: [
          { name: 'scriptType', type: 'slot' },
          {
            label: 'script',
            value: 'content',
            v_validate: 'required:true',
            placeholder: '',
            disabled: false,
            type: 'textarea'
          },
          { name: 'detectBtn', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: null,
          type: 'shell',
          content: null,
          entityInstances: []
        },
        v_select_configs: {
          typeOptions: [
            { label: 'shell', value: 'shell' },
            { label: 'sql', value: 'sql' }
          ]
        }
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
    async initTableData () {
      const params = this.$itsCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    detectF (rowData) {
      this.id = rowData.id
      this.detectConfig.addRow.type = 'shell'
      this.exectPageConfig.table.tableData = []
      this.detectConfig.addRow.name = rowData.name
      this.$root.JQ('#detect_Modal').modal('show')
    },
    async exectDetect () {
      this.exectPageConfig.table.tableData = []
      const params = {
        scripts: [
          {
            type: this.detectConfig.addRow.type,
            content: this.detectConfig.addRow.content,
            name: this.detectConfig.addRow.name
          }
        ],
        entityInstances: this.detectConfig.addRow.entityInstances
      }
      const { status, data } = await boxDetect(this.id, params)
      if (status === 'OK') {
        this.exectPageConfig.table.tableData = data
      }
    },
    async getConfigData () {
      const params = '/itsdangerous/ui/v1/policies'
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.modelConfig.v_select_configs.policyOptions = data.data.map(item => {
          return {
            label: item.name,
            value: item.id
          }
        })
      }
      const url = '/itsdangerous/ui/v1/subjects'
      const res = await getTableData(url)
      if (res.status === 'OK') {
        this.modelConfig.v_select_configs.subjectOptions = res.data.data.map(item => {
          return {
            label: item.name,
            value: item.id
          }
        })
      }
    },
    async add () {
      this.modelConfig.addRow.enabled = true
      await this.getConfigData()
      this.modelConfig.isAdd = true
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async addPost () {
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
      await this.getConfigData()
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
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
  components: {}
}
</script>

<style scoped lang="scss"></style>
