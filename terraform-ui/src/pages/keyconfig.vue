<template>
  <div class=" ">
    <TerraformPageTable :pageConfig="pageConfig"></TerraformPageTable>
    <TfModalComponent :modelConfig="modelConfig">
      <template #outer-config>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_provider_property') }}:</label>
          <Input
            v-model="modelConfig.addRow.value_config"
            class="json-edit"
            type="textarea"
            :rows="5"
            style="width:70%"
          />
          <Icon
            @click="editJson(modelConfig.addRow.value_config, 'value_config')"
            type="ios-create-outline"
            size="18"
            class="json-edit"
          />
          <label class="required-tip">*</label>
        </div>
      </template>
    </TfModalComponent>
    <Modal :z-index="2000" v-model="showEdit" :title="$t('tf_json_edit')" @on-ok="confirmJsonData">
      <Tree ref="jsonTree" :jsonData="jsonData"></Tree>
    </Modal>
  </div>
</template>

<script>
import { getTableData, addTableRow, editTableRow, deleteTableRow } from '@/api/server'
import Tree from '@/pages/components/tree'
let tableEle = [
  {
    title: 'tf_provider',
    value: 'provider', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_resource',
    value: 'resource', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_property', // 不必
    value: 'property', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_provider_property',
    value: 'value_config',
    render: item => {
      return JSON.stringify(item.value_config)
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
      showEdit: false,
      jsonData: {},
      editKey: '',
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
            option: 'providerOption',
            disabled: true,
            type: 'select'
          },
          {
            label: 'tf_property',
            value: 'property',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          { name: 'outer-config', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          resource: '',
          provider: '',
          property: '',
          value_config: '{}'
        },
        v_select_configs: {
          providerOption: []
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
    editJson (value, key) {
      this.editKey = key
      value = value || '{}'
      this.$refs.jsonTree.initJSON(JSON.parse(value))
      this.jsonData = value
      this.showEdit = true
    },
    confirmJsonData () {
      const jsonJ = this.$refs.jsonTree.jsonJ
      this.modelConfig.addRow[this.editKey] = JSON.stringify(jsonJ)
      this.showEdit = false
    },
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
      if (params.value_config) {
        params.value_config = JSON.parse(params.value_config)
      } else {
        params.value_config = {}
      }
      return params
    },
    async addPost () {
      const params = this.beautyParams(JSON.parse(JSON.stringify(this.modelConfig.addRow)))
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
      this.modelConfig.addRow.value_config = JSON.stringify(this.modelConfig.addRow.value_config)
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
  components: {
    Tree
  }
}
</script>

<style scoped lang="scss">
.json-edit {
  position: absolution;
  vertical-align: top;
  cursor: pointer;
  color: #2d8cf0;
}
</style>
