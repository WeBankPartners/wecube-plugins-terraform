<template>
  <div class=" ">
    <Button @click="addProvider" style="margin-bottom: 10px" type="primary">{{ $t('t_add') }}</Button>
    <Table border size="small" :columns="tableColumns" :data="tableData"></Table>
    <Modal
      v-model="newProvider.isShow"
      :title="(newProvider.isAdd ? $t('t_add') : $t('t_edit')) + $t('t_provider')"
      :mask-closable="false"
      :width="700"
    >
      <Form inline :label-width="120">
        <FormItem required :label="$t('t_name')">
          <Input type="text" v-model="newProvider.form.name" style="width: 520px"></Input>
        </FormItem>
        <FormItem required :label="$t('t_namespace')">
          <Input type="text" v-model="newProvider.form.nameSpace" style="width: 520px"></Input>
        </FormItem>
        <FormItem required :label="$t('t_version')">
          <Input type="text" v-model="newProvider.form.version" :rows="4" style="width: 520px"></Input>
        </FormItem>
        <FormItem :label="$t('t_is_microsoft_cloud')">
          <i-switch v-model="isMicrosoftCloud" style="width: 52px">
            <span slot="open">{{ $t('t_yes') }}</span>
            <span slot="close">{{ $t('t_no') }}</span>
          </i-switch>
        </FormItem>
        <FormItem required v-if="!isMicrosoftCloud" :label="$t('t_region_attr_name')">
          <Input type="text" v-model="newProvider.form.regionAttrName" style="width: 520px"></Input>
        </FormItem>
        <FormItem required :label="$t('t_secretId_attr_name')">
          <Input type="text" v-model="newProvider.form.secretIdAttrName" style="width: 520px"></Input>
        </FormItem>
        <FormItem required :label="$t('t_secretKey_attr_name')">
          <Input type="text" v-model="newProvider.form.secretKeyAttrName" style="width: 520px"></Input>
        </FormItem>
        <FormItem required v-if="isMicrosoftCloud" :label="$t('t_tenant_id_key')">
          <Input type="text" v-model="newProvider.form.tenantIdAttrName" style="width: 520px"></Input>
        </FormItem>
        <FormItem required v-if="isMicrosoftCloud" :label="$t('t_subscription_id_key')">
          <Input type="text" v-model="newProvider.form.subscriptionIdAttrName" style="width: 520px"></Input>
        </FormItem>
      </Form>
      <div slot="footer">
        <Button @click="newProvider.isShow = false">{{ $t('t_cancle') }}</Button>
        <Button type="primary" @click="confirmProvider">{{ $t('t_save') }}</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import { getProviders, addProvider, deleteProvider, instanceDataDownload, editProvider } from '@/api/server'
import { getCookie } from '../pages/util/cookie'
export default {
  name: '',
  data () {
    return {
      name: '',
      isMicrosoftCloud: false,
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
          tenantIdAttrName: '',
          subscriptionIdAttrName: '',
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
        tenantIdAttrName: '',
        subscriptionIdAttrName: '',
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
          title: this.$t('t_tenant_id_key'),
          key: 'tenantIdAttrName'
        },
        {
          title: this.$t('t_subscription_id_key'),
          key: 'subscriptionIdAttrName'
        },
        {
          title: this.$t('t_initialized'),
          key: 'initialized'
        },
        {
          title: this.$t('t_action'),
          key: 'action',
          width: 231,
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
                      title: 'xxfsdfaslkfjsaldkjflk',
                      action: `/terraform/api/v1/providers/upload?id=${params.row.id}`,
                      headers: { Authorization: 'Bearer ' + getCookie('accessToken') },
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
                      'Tooltip',
                      {
                        props: { placement: 'top', content: this.$t('t_local_upload_tip'), 'max-width': 115 }
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
                    )
                  ]
                ),
                h(
                  'Tooltip',
                  {
                    props: { placement: 'top', content: this.$t('t_online_download_tip'), 'max-width': 115 }
                  },
                  [
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
                          'margin-left': '8px'
                        },
                        on: {
                          click: () => {
                            this.downloadInstance(params.row)
                          }
                        }
                      },
                      this.$t('t_online_download')
                    )
                  ]
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
      if (this.newProvider.form.subscriptionIdAttrName) {
        this.isMicrosoftCloud = true
      } else {
        this.isMicrosoftCloud = false
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
      this.isMicrosoftCloud = false
      this.newProvider.isShow = true
    },
    validRequired () {
      if (
        !this.newProvider.form.name ||
        !this.newProvider.form.nameSpace ||
        !this.newProvider.form.version ||
        !this.newProvider.form.secretIdAttrName ||
        !this.newProvider.form.secretKeyAttrName ||
        (this.isMicrosoftCloud &&
          (!this.newProvider.form.tenantIdAttrName || !this.newProvider.form.subscriptionIdAttrName)) ||
        (!this.isMicrosoftCloud && !this.newProvider.form.regionAttrName)
      ) {
        this.$Message.error(this.$t('t_validate_required'))
        return false
      } else {
        return true
      }
    },
    async confirmProvider () {
      if (!this.validRequired()) {
        return false
      }
      const method = this.newProvider.isAdd ? addProvider : editProvider
      const { statusCode } = await method([this.newProvider.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getTableData()
        this.newProvider.isShow = false
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
