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
    title: 'ID',
    value: 'id', //
    display: true
  },
  {
    title: 'tf_name',
    value: 'name', //
    display: true
  },
  {
    title: 'tf_secret_id',
    value: 'secret_id', //
    display: true
  },
  {
    title: 'tf_secret_key',
    value: 'secret_key', //
    display: true
  },
  {
    title: 'tf_provider_property',
    value: 'provider_property', //
    display: true
  },
  {
    title: 'tf_extend_info',
    value: 'extend_info', //
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
        CRUD: '/terraform/v1/configer/provider',
        researchConfig: {
          input_conditions: [
            {
              value: 'name',
              type: 'input',
              placeholder: 'tf_name',
              style: ''
            },
            {
              value: 'region',
              type: 'input',
              placeholder: 'tf_region',
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
            name: '',
            region: ''
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
        modalTitle: 'tf_provider',
        isAdd: true,
        config: [
          {
            label: 'tf_name',
            value: 'name',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: true,
            type: 'text'
          },
          {
            label: 'tf_secret_key',
            value: 'secret_key',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            label: 'tf_secret_id',
            value: 'secret_id',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            label: 'tf_extend_info',
            value: 'extend_info',
            placeholder: 'JSON',
            disabled: false,
            type: 'textarea'
          },
          {
            label: 'tf_provider_property',
            value: 'provider_property',
            placeholder: 'JSON',
            disabled: false,
            type: 'textarea'
          }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: '',
          secret_key: '',
          secret_id: '',
          extend_info: '',
          provider_property: ''
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
      this.modelConfig.addRow.extend_info = JSON.parse(this.modelConfig.addRow.extend_info)
      this.modelConfig.addRow.provider_property = JSON.parse(this.modelConfig.addRow.provider_property)
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
      this.modelConfig.addRow.extend_info = JSON.stringify(this.modelConfig.addRow.extend_info)
      this.modelConfig.addRow.provider_property = JSON.stringify(this.modelConfig.addRow.provider_property)
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      let editData = JSON.parse(JSON.stringify(this.modelConfig.addRow))
      delete editData.name
      editData.extend_info = JSON.parse(editData.extend_info)
      editData.provider_property = JSON.parse(editData.provider_property)
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, editData)
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
