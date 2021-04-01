<template>
  <div class=" ">
    <TerraformPageTable :pageConfig="pageConfig"></TerraformPageTable>
    <TfModalComponent :modelConfig="modelConfig">
      <template #outer-config>
        <Divider size="small" orientation="left" style="font-size:12px;color:#cccaca"
          >Resource {{ $t('tf_config') }}</Divider
        >
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('tf_name') }}:</label>
          <input
            v-model="modelConfig.addRow.resource_name"
            type="text"
            class="col-md-7 form-control model-input c-dark"
          />
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_property_conversion') }}:</label>
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
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_output_conversion') }}:</label>
          <Input
            v-model="modelConfig.addRow.resource_output"
            class="json-edit"
            type="textarea"
            :rows="3"
            style="width:70%"
          />
          <Icon
            @click="editJson(modelConfig.addRow.resource_output, 'resource_output')"
            type="ios-create-outline"
            size="18"
            class="json-edit"
          />
          <label class="required-tip">*</label>
        </div>
        <Divider size="small" orientation="left" style="font-size:12px;color:#cccaca"
          >Data Source {{$t('tf_config')</Divider
        >
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('tf_name') }}:</label>
          <input
            v-model="modelConfig.addRow.data_source_name"
            type="text"
            class="col-md-7 form-control model-input c-dark"
          />
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('tf_output_property') }}:</label>
          <input
            v-model="modelConfig.addRow.data_source_argument"
            type="text"
            class="col-md-7 form-control model-input c-dark"
          />
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_parameter_conversion') }}:</label>
          <Input v-model="modelConfig.addRow.data_source" type="textarea" :rows="3" style="width:70%" />
          <Icon
            @click="editJson(modelConfig.addRow.data_source, 'data_source')"
            type="ios-create-outline"
            size="18"
            class="json-edit"
          />
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_output_conversion') }}:</label>
          <Input
            v-model="modelConfig.addRow.data_source_output"
            class="json-edit"
            type="textarea"
            :rows="3"
            style="width:70%"
          />
          <Icon
            @click="editJson(modelConfig.addRow.data_source_output, 'data_source_output')"
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
import { isJSONStr } from '@/assets/js/utils'
let tableEle = [
  {
    title: 'tf_provider', // 不必
    value: 'provider', //
    style: { width: '200px' },
    display: true
  },
  {
    title: 'tf_resource_type',
    value: 'resource_type', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_resource_name',
    value: 'resource_name',
    // style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_resource_property_conversion',
    value: 'resource_property',
    // style: { width: '150px' },
    render: item => {
      return JSON.stringify(item.resource_property)
    },
    display: true
  },
  {
    title: 'tf_resource_output_conversion',
    value: 'resource_output',
    // style: { width: '150px' },
    render: item => {
      return JSON.stringify(item.resource_output)
    },
    display: true
  },

  {
    title: 'tf_data_source_name',
    value: 'data_source_name', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_data_source_output_parameter',
    value: 'data_source_argument', //
    style: { width: '200px' },
    display: true
  },
  {
    title: 'tf_data_source_parameter_conversion',
    value: 'data_source',
    style: { width: '200px' },
    render: item => {
      return JSON.stringify(item.data_source)
    },
    display: true
  },
  {
    title: 'tf_data_source_output_conversion',
    value: 'data_source_output',
    style: { width: '200px' },
    render: item => {
      return JSON.stringify(item.data_source_output)
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
              value: 'resource_type',
              type: 'input',
              placeholder: 'tf_resource_type',
              style: ''
            },
            {
              value: 'resource_name',
              type: 'input',
              placeholder: 'tf_resource_name',
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
        modalStyle: 'min-width:800px',
        config: [
          {
            label: 'tf_resource_type',
            value: 'resource_type',
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
          { name: 'outer-config', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          resource_name: '',
          provider: '',
          resource_type: '',
          resource_property: '{}',
          resource_output: '{}',
          data_source_name: '',
          data_source_argument: '',
          data_source: '{}',
          data_source_output: '{}'
        },
        v_select_configs: {
          providerOption: []
        },
        slotConfig: []
      },
      modelTip: {
        key: 'resource_type',
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
      this.modelConfig.addRow.resource_property = '{}'
      this.modelConfig.addRow.resource_output = '{}'
      this.modelConfig.addRow.data_source = '{}'
      this.modelConfig.addRow.data_source_output = '{}'
      await this.getProvider()
      this.modelConfig.isAdd = true
    },
    beautyParams (params, transformFields) {
      for (let p of transformFields) {
        if (isJSONStr(params[p])) {
          params[p] = JSON.parse(params[p])
        } else {
          this.$Notice.error({
            title: 'Error',
            desc: this.$t('tf_' + p) + this.$t('tf_json_require'),
            duration: 10
          })
          return false
        }
      }
      return params
    },
    async addPost () {
      const params = this.beautyParams(JSON.parse(JSON.stringify(this.modelConfig.addRow)), [
        'resource_property',
        'resource_output'
      ])
      if (!params) return
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
      this.modelConfig.addRow.resource_property = JSON.stringify(this.modelConfig.addRow.resource_property)
      this.modelConfig.addRow.resource_output = JSON.stringify(this.modelConfig.addRow.resource_output)
      this.modelConfig.addRow.data_source = JSON.stringify(this.modelConfig.addRow.data_source)
      this.modelConfig.addRow.data_source_output = JSON.stringify(this.modelConfig.addRow.data_source_output)
    },
    async editPost () {
      let editData = JSON.parse(JSON.stringify(this.modelConfig.addRow))
      delete editData.name
      const params = this.beautyParams(editData, ['resource_property', 'resource_output'])
      if (!params) return
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
