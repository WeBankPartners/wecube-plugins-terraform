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
    title: 'tf_name',
    value: 'name', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_display_name',
    value: 'display_name', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_provider',
    value: 'provider', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_region',
    value: 'region ', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_secret_info',
    value: 'secret_info',
    display: true
  },
  {
    title: 'tf_extend_info',
    value: 'extend_info',
    render: item => {
      return JSON.stringify(item.extend_info)
    },
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
        CRUD: '/terraform/v1/configer/secret',
        researchConfig: {
          input_conditions: [
            {
              value: 'provider',
              type: 'input',
              placeholder: 'tf_provider',
              style: ''
            },
            {
              value: 'name',
              type: 'input',
              placeholder: 'tf_name',
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
        modalTitle: 'tf_secret',
        isAdd: true,
        config: [
          {
            label: 'tf_name',
            value: 'name',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            label: 'tf_display_name',
            value: 'display_name',
            placeholder: '',
            v_validate: '',
            disabled: false,
            type: 'text'
          },
          {
            label: 'tf_provider',
            value: 'provider',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true',
            option: 'providerOption',
            disabled: true,
            type: 'select'
          },
          {
            label: 'tf_region',
            value: 'region',
            placeholder: '',
            disabled: false,
            type: 'text'
          },
          {
            label: 'tf_secret_info',
            value: 'secret_info',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true',
            disabled: false,
            type: 'textarea'
          },
          {
            label: 'tf_extend_info',
            value: 'extend_info',
            placeholder: '',
            disabled: false,
            type: 'textarea'
          }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: '',
          display_name: '',
          provider: '',
          region: '',
          secret_info: '',
          extend_info: ''
        },
        v_select_configs: {
          providerOption: []
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
    async getProvider () {
      const { status, data } = await getTableData('/terraform/v1/configer/provider')
      if (status === 'OK') {
        this.modelConfig.v_select_configs.providerOption = data.data.map(item => {
          return {
            value: item.name,
            label: item.name
          }
        })
        this.$root.JQ('#add_edit_Modal').modal('show')
      }
    },
    async add () {
      await this.getProvider()
      this.modelConfig.isAdd = true
    },
    beautyParams (params) {
      if (params.extend_info) {
        params.extend_info = JSON.parse(params.extend_info)
      } else {
        params.extend_info = {}
      }
      return params
    },
    async addPost () {
      const params = this.beautyParams(this.modelConfig.addRow)
      const { status, message } = await addTableRow(this.pageConfig.CRUD, params)
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    async editF (rowData) {
      this.id = rowData.id
      await this.getProvider()
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.modelConfig.addRow = this.$tfCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      this.modelConfig.addRow.extend_info = JSON.stringify(this.modelConfig.addRow.extend_info)
    },
    async editPost () {
      let editData = JSON.parse(JSON.stringify(this.modelConfig.addRow))
      const params = this.beautyParams(editData)
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, params)
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
