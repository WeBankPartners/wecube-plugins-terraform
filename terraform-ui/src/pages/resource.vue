<template>
  <div class=" ">
    <TerraformPageTable :pageConfig="pageConfig"></TerraformPageTable>
    <TfModalComponent :modelConfig="modelConfig">
      <template #outer-config>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_provider_property') }}:</label>
          <Input v-model="modelConfig.addRow.resource_property" type="textarea" :rows="3" style="width:70%" />
          <Icon
            @click="editJson(modelConfig.addRow.resource_property, 'resource_property')"
            type="ios-create-outline"
            size="18"
            class="json-edit"
          />
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_output_property') }}:</label>
          <Input
            v-model="modelConfig.addRow.output_property"
            class="json-edit"
            type="textarea"
            :rows="3"
            style="width:70%"
          />
          <Icon
            @click="editJson(modelConfig.addRow.output_property, 'output_property')"
            type="ios-create-outline"
            size="18"
            class="json-edit"
          />
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_extend_info') }}:</label>
          <Input
            v-model="modelConfig.addRow.extend_info"
            class="json-edit"
            type="textarea"
            :rows="3"
            style="width:70%"
          />
          <Icon
            @click="editJson(modelConfig.addRow.extend_info, 'extend_info')"
            type="ios-create-outline"
            size="18"
            class="json-edit"
          />
        </div>
      </template>
    </TfModalComponent>
    <Modal :z-index="2000" v-model="showEdit" :title="$t('tf_json_edit')" @on-ok="confirmJsonData" width="700">
      <Tree ref="jsonTree" :jsonData="jsonData"></Tree>
    </Modal>
  </div>
</template>

<script>
import { getTableData, addTableRow, editTableRow, deleteTableRow } from '@/api/server'
import Tree from '@/pages/components/tree'
let tableEle = [
  {
    title: 'tf_provider', // 不必
    value: 'provider', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_resource',
    value: 'resource_name', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_property',
    value: 'property',
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_provider_property',
    value: 'resource_property', //
    render: item => {
      return JSON.stringify(item.resource_property)
    },
    display: true
  },
  {
    title: 'tf_output_property',
    value: 'output_property',
    render: item => {
      return JSON.stringify(item.output_property)
    },
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
      showEdit: false,
      jsonData: {},
      editKey: '',
      pageConfig: {
        CRUD: '/terraform/v1/configer/resource',
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
              value: 'resource_name',
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
          filters: {
            provider: '',
            property: '',
            resource_name: ''
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
        modalTitle: 'tf_resource',
        isAdd: true,
        config: [
          {
            label: 'tf_resource',
            value: 'resource_name',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: true,
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
          resource_name: '',
          provider: '',
          property: '',
          extend_info: '{}',
          resource_property: '{}',
          output_property: '{}'
        },
        v_select_configs: {
          providerOption: []
        }
      },
      modelTip: {
        key: 'resource_name',
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
      if (params.extend_info) {
        params.extend_info = JSON.parse(params.extend_info)
      } else {
        params.extend_info = {}
      }
      if (params.resource_property) {
        params.resource_property = JSON.parse(params.resource_property)
      } else {
        params.resource_property = {}
      }
      if (params.output_property) {
        params.output_property = JSON.parse(params.output_property)
      } else {
        params.output_property = {}
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
      this.modelConfig.addRow.extend_info = JSON.stringify(this.modelConfig.addRow.extend_info)
      this.modelConfig.addRow.resource_property = JSON.stringify(this.modelConfig.addRow.resource_property)
      this.modelConfig.addRow.output_property = JSON.stringify(this.modelConfig.addRow.output_property)
    },
    async editPost () {
      let editData = JSON.parse(JSON.stringify(this.modelConfig.addRow))
      delete editData.name
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
