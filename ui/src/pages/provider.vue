<template>
  <div class=" ">
    <Form inline>
      <FormItem>
        <Button @click="addProvider" style="margin-left: 24px" type="primary">{{ $t('t_add') }}</Button>
      </FormItem>
    </Form>
    <Table border :columns="tableColumns" :data="tableData"></Table>
    <Modal
      v-model="newProvider.isShow"
      :title="newProvider.isAdd ? $t('t_add') : $t('t_edit') + $t('t_provider')"
      :mask-closable="false"
      @on-ok="confirmProvider"
      @on-cancel="confirmProvider.isShow = false"
    >
      <Form inline :label-width="80">
        <FormItem :label="$t('t_name')">
          <Input type="text" v-model="newProvider.form.name" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_namespace')">
          <Input type="text" v-model="newProvider.form.nameSpace" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_version')">
          <Input type="text" v-model="newProvider.form.version" :rows="4" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_region_attr_name')">
          <Input type="text" v-model="newProvider.form.regionAttrName" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_secretId_attr_name')">
          <Input type="text" v-model="newProvider.form.secretIdAttrName" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_secretKey_attr_name')">
          <Input type="text" v-model="newProvider.form.secretKeyAttrName" style="width:400px"></Input>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import { getProviders, addProvider, deleteProvider, instanceDataDownload, editProvider } from '@/api/server'
export default {
  name: '',
  data () {
    return {
      name: '',
      newProvider: {
        isShow: false,
        isAdd: true,
        form: {
          createTime: '',
          createUser: '',
          id: '',
          name: '',
          nameSpace: '',
          regionAttrName: '',
          secretIdAttrName: '',
          secretKeyAttrName: '',
          updateTime: '',
          updateUser: '',
          version: ''
        }
      },
      emptyForm: {
        createTime: '',
        createUser: '',
        id: '',
        name: '',
        nameSpace: '',
        regionAttrName: '',
        secretIdAttrName: '',
        secretKeyAttrName: '',
        updateTime: '',
        updateUser: '',
        version: ''
      },
      tableColumns: [
        {
          title: this.$t('t_name'),
          key: 'name'
        },
        {
          title: this.$t('t_namespace'),
          key: 'nameSpace'
        },
        {
          title: this.$t('t_version'),
          key: 'version'
        },
        {
          title: this.$t('t_region_attr_name'),
          key: 'regionAttrName'
        },
        {
          title: this.$t('t_secretId_attr_name'),
          key: 'secretIdAttrName'
        },
        {
          title: this.$t('t_secretKey_attr_name'),
          key: 'secretKeyAttrName'
        },
        {
          title: this.$t('t_action'),
          key: 'action',
          width: 230,
          align: 'center',
          render: (h, params) => {
            let action = [
              h(
                'Button',
                {
                  props: {
                    type: 'primary',
                    size: 'small'
                  },
                  style: {
                    marginRight: '5px'
                  },
                  on: {
                    click: () => {
                      this.editProvider(params.row)
                    }
                  }
                },
                this.$t('t_edit')
              ),
              h(
                'Button',
                {
                  props: {
                    type: 'error',
                    size: 'small'
                  },
                  style: {
                    marginRight: '5px'
                  },
                  on: {
                    click: () => {
                      this.deleteProvider(params.row)
                    }
                  }
                },
                this.$t('t_delete')
              )
            ]
            if (params.row.initialized === 'N') {
              action.push([
                h(
                  'Upload',
                  {
                    props: {
                      type: 'select',
                      size: 'small',
                      action: `/terraform/api/v1/providers/upload?id=${params.row.id}`,
                      'on-success': this.handleSuccess,
                      'on-error': this.handleError
                    },
                    style: {
                      display: 'inline-block'
                    },
                    on: {}
                  },
                  [
                    h(
                      'Button',
                      {
                        props: {
                          type: 'success',
                          size: 'small'
                        },
                        style: {},
                        on: {}
                      },
                      this.$t('t_local_upload')
                    )
                  ]
                ),
                h(
                  'Button',
                  {
                    props: Object.assign(
                      {},
                      {
                        type: 'warning',
                        size: 'small'
                      }
                    ),
                    style: {
                      // 'margin-left': '8px'
                    },
                    on: {
                      click: () => {
                        this.downloadInstance(params.row)
                      }
                    }
                  },
                  this.$t('t_online_download')
                )
              ])
            }
            return h(
              'div',
              {
                style: {
                  textAlign: 'left'
                }
              },
              action
            )
          }
        }
      ],
      tableData: []
    }
  },
  mounted () {
    this.getTableData()
  },
  methods: {
    handleUpload (file) {
      if (!file.name.endsWith('.gz')) {
        this.$Notice.warning({
          title: 'Warning',
          desc: 'Must be a json file'
        })
        return false
      }
      return true
    },
    handleError (val) {
      this.$Notice.error({
        title: 'Error',
        desc: 'Import Faild'
      })
    },
    handleSuccess (val) {
      this.$Notice.success({
        title: 'Successful',
        desc: 'Successful'
      })
      this.getTableData()
    },
    async downloadInstance (item) {
      this.$Notice.success({
        title: 'Info',
        desc: 'Need 10s ……'
      })
      const { statusCode } = await instanceDataDownload(item.id)
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getTableData()
      }
    },
    editProvider (item) {
      this.newProvider.form = {
        ...item
      }
      this.newProvider.isAdd = false
      this.newProvider.isShow = true
    },
    deleteProvider (item) {
      this.$Modal.confirm({
        title: this.$t('t_confirm_delete'),
        'z-index': 1000000,
        loading: true,
        onOk: async () => {
          let res = await deleteProvider(item.id)
          this.$Modal.remove()
          if (res.statusCode === 'OK') {
            this.$Notice.success({
              title: 'Successful',
              desc: 'Successful'
            })
            this.getTableData()
          }
        },
        onCancel: () => {}
      })
    },
    addProvider () {
      this.newProvider.isAdd = true
      this.newProvider.form = JSON.parse(JSON.stringify(this.emptyForm))
      this.newProvider.isShow = true
    },
    async confirmProvider () {
      const method = this.newProvider.isAdd ? addProvider : editProvider
      const { statusCode } = await method([this.newProvider.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getTableData()
        this.confirmProvider.isShow = false
      }
    },
    async getTableData () {
      const { statusCode, data } = await getProviders()
      if (statusCode === 'OK') {
        this.tableData = data
      }
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
