<template>
  <div class=" ">
    <DangerousPageTable :pageConfig="pageConfig"></DangerousPageTable>
    <ModalComponent :modelConfig="modelConfig">
      <template #plugin-params>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('hr_service_name') }}:</label>
          <Select v-model="modelConfig.addRow.service" @on-change="changeService" filterable style="width: 338px">
            <Option
              v-for="service in modelConfig.v_select_configs.serviceNameOptions"
              :value="service.serviceName"
              :key="service.serviceName"
              >{{ service.serviceName }}</Option
            >
          </Select>
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('content_type') }}:</label>
          <Select v-model="modelConfig.addRow.content_type" filterable style="width: 338px">
            <Option
              v-for="item in modelConfig.v_select_configs.contentTypeOptions"
              :value="item.value"
              :key="item.value"
              >{{ item.label }}</Option
            >
          </Select>
          <label class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('content_field') }}:</label>
          <Select v-model="modelConfig.addRow.content_field" clearable filterable style="width: 338px">
            <Option v-for="item in modelConfig.v_select_configs.serviceAttr" :value="item.name" :key="item.name">{{
              item.name
            }}</Option>
          </Select>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('endpoint_field') }}:</label>
          <Select v-model="modelConfig.addRow.endpoint_field" clearable filterable style="width: 338px">
            <Option v-for="item in modelConfig.v_select_configs.serviceAttr" :value="item.name" :key="item.name">{{
              item.name
            }}</Option>
          </Select>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('endpoint_include') }}:</label>
          <Select v-model="modelConfig.endpoint_include_seleted" filterable multiple style="width: 338px">
            <Option v-for="item in modelConfig.v_select_configs.serviceAttr" :value="item.name" :key="item.name">{{
              item.name
            }}</Option>
          </Select>
        </div>
      </template>
    </ModalComponent>
  </div>
</template>

<script>
import {
  getTableData,
  addTableRow,
  editTableRow,
  deleteTableRow,
  getService,
  getRuleAttrByServiceName
} from '@/api/server'
let tableEle = [
  {
    title: 'service',
    value: 'service', // 插件
    display: true
  },
  {
    title: 'content_type', // 不必
    value: 'content_type', // 脚本类型
    display: true
  },
  {
    title: 'content_field',
    value: 'content_field', // 脚本字段
    display: true
  },
  {
    title: 'endpoint_field', // 脚本地址
    value: 'endpoint_field',
    display: true
  },
  {
    title: 'endpoint_include', // 脚本地址
    value: 'endpoint_include',
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
        CRUD: '/itsdangerous/ui/v1/service-scripts',
        researchConfig: {
          input_conditions: [
            {
              value: 'service__icontains',
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
        modalTitle: 'hr_plugin_params',
        isAdd: true,
        config: [{ name: 'plugin-params', type: 'slot' }],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          service: null,
          content_type: 'shell',
          content_field: null,
          endpoint_field: null,
          endpoint_include: ''
        },
        endpoint_include_seleted: [],
        v_select_configs: {
          serviceNameOptions: [],
          serviceAttr: [],
          contentTypeOptions: [
            { label: 'shell', value: 'shell' },
            { label: 'sql', value: 'sql' }
          ]
        }
      },
      modelTip: {
        key: 'service',
        value: null
      },
      id: ''
    }
  },
  mounted () {
    this.initTableData()
  },
  methods: {
    async changeService (val) {
      const { status, data } = await getRuleAttrByServiceName(val)
      if (status === 'OK') {
        this.modelConfig.v_select_configs.serviceAttr = data.data
      }
    },
    async getService () {
      this.modelConfig.endpoint_include_seleted = []
      const { status, data } = await getService()
      if (status === 'OK') {
        this.modelConfig.v_select_configs.serviceNameOptions = data.data
      }
    },
    async initTableData () {
      const params = this.$itsCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    async add () {
      this.modelConfig.isAdd = true
      await this.getService()
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async addPost () {
      this.modelConfig.addRow.endpoint_include = this.modelConfig.endpoint_include_seleted.join('|')
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
      await this.getService()
      this.modelConfig.addRow.service = rowData.service
      await this.changeService(rowData.service)
      this.modelConfig.addRow = this.$itsCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      if (rowData.endpoint_include) {
        this.modelConfig.endpoint_include_seleted = rowData.endpoint_include.split('|')
      }
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      this.modelConfig.addRow.endpoint_include = this.modelConfig.endpoint_include_seleted.join('|')
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: this.$t('delete_confirm') + rowData.service,
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
