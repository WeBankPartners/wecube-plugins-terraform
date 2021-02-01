<template>
  <div class=" ">
    <TerraformPageTable :pageConfig="pageConfig"></TerraformPageTable>
    <TfModalComponent :modelConfig="modelConfig"></TfModalComponent>
  </div>
</template>

<script>
import { getTableData, addTableRow, editTableRow, deleteTableRow } from '@/api/server'
let tableEle = [
  {
    title: 'tf_id',
    value: 'id', //
    display: true
  },
  {
    title: 'tf_provider',
    value: 'provider', //
    display: true
  },
  {
    title: 'tf_resource',
    value: 'resource', //
    display: true
  },
  {
    title: 'tf_property', // 不必
    value: 'property', //
    display: true
  },
  {
    title: 'tf_provider_property',
    value: 'value_config',
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
        CRUD: '/terraform/v1/configer/keyconfig',
        researchConfig: {
          input_conditions: [
            {
              value: 'provider',
              type: 'input',
              placeholder: 'tf_provider',
              style: ''
            },
            {
              value: 'property',
              type: 'input',
              placeholder: 'tf_property',
              style: ''
            },
            {
              value: 'resource',
              type: 'input',
              placeholder: 'tf_resource',
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
          filters: {}
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
        modalTitle: 'tf_keyconfig',
        isAdd: true,
        config: [
          {
            label: 'tf_resource',
            value: 'resource',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            label: 'tf_provider',
            value: 'provider',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            label: 'tf_property',
            value: 'property',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            label: 'tf_provider_property',
            value: 'value_config',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true',
            disabled: false,
            type: 'textarea'
          }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          resource: '',
          provider: '',
          property: '',
          value_config: ''
        }
      },
      modelTip: {
        key: 'resource',
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
      const params = this.$tfCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    add () {
      this.modelConfig.isAdd = true
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async addPost () {
      this.modelConfig.addRow.value_config = JSON.parse(this.modelConfig.addRow.value_config)
      const { status, message } = await addTableRow(this.pageConfig.CRUD, this.modelConfig.addRow)
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
      this.modelConfig.addRow = this.$tfCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      this.modelConfig.addRow.value_config = JSON.stringify(this.modelConfig.addRow.value_config)
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      let editData = JSON.parse(JSON.stringify(this.modelConfig.addRow))
      editData.value_config = JSON.parse(editData.value_config)
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, editData)
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: this.$t('delete_confirm') + rowData[this.modelTip.key],
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
