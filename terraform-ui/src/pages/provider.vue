<template>
  <div class=" ">
    <TerraformPageTable :pageConfig="pageConfig"></TerraformPageTable>
    <TfModalComponent :modelConfig="modelConfig">
      <template #outer-config>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name" style="vertical-align: top;">{{ $t('tf_provider_property') }}:</label>
          <Input v-model="modelConfig.addRow.provider_property" type="textarea" :rows="5" style="width:70%" />
          <Icon
            @click="editJson(modelConfig.addRow.provider_property, 'provider_property')"
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
            :rows="5"
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
    title: 'tf_name',
    value: 'name', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_secret_id',
    value: 'secret_id', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_secret_key',
    value: 'secret_key', //
    style: { width: '150px' },
    display: true
  },
  {
    title: 'tf_provider_property',
    value: 'provider_property', //
    render: item => {
      return JSON.stringify(item.provider_property)
    },
    display: true
  },
  {
    title: 'tf_extend_info',
    value: 'extend_info', //
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
          { name: 'outer-config', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: '',
          secret_key: '',
          secret_id: '',
          extend_info: '{}',
          provider_property: '{}'
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
    editJson (value = '{}', key) {
      this.editKey = key
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
    add () {
      this.modelConfig.isAdd = true
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    beautyParams (params) {
      if (params.extend_info) {
        params.extend_info = JSON.parse(params.extend_info)
      } else {
        params.extend_info = {}
      }
      if (params.provider_property) {
        params.provider_property = JSON.parse(params.provider_property)
      } else {
        params.provider_property = {}
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
