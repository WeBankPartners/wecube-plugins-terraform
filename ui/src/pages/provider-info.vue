<template>
  <div class="terraform-provider-info">
    <Form inline>
      <FormItem prop="user">
        <Input type="text" v-model="name" style="width: 300px" :placeholder="$t('t_name')"> </Input>
      </FormItem>
      <FormItem>
        <Button type="primary" @click="getTableData" style="margin-left: 24px">{{ $t('t_search') }}</Button>
        <Button @click="addProviderInfo" type="success" style="margin-left: 24px">{{ $t('t_add') }}</Button>
      </FormItem>
    </Form>
    <Table border size="small" :columns="tableColumns" :data="tableData"></Table>
    <Modal
      v-model="newProviderInfo.isShow"
      :title="(newProviderInfo.isAdd ? $t('t_add') : $t('t_edit')) + $t('t_provider_info')"
      :mask-closable="false"
      :width="700"
    >
      <Form inline :label-width="120">
        <FormItem required :label="$t('t_name')">
          <Input type="text" v-model="newProviderInfo.form.name" style="width: 520px"></Input>
        </FormItem>
        <FormItem required :label="$t('t_provider')">
          <Select
            v-model="newProviderInfo.form.provider"
            ref="selectProvider"
            @on-change="handleSelectProvider"
            style="width: 520px"
          >
            <Option v-for="provider in newProviderInfo.providerOptions" :value="provider.id" :key="provider.id"
              >{{ provider.name }}
            </Option>
          </Select>
        </FormItem>
        <FormItem required :label="$t('t_secret_id')">
          <Input type="textarea" v-model="newProviderInfo.form.secretId" :rows="4" style="width: 520px"></Input>
        </FormItem>
        <FormItem required :label="$t('t_secret_key')">
          <Input type="textarea" v-model="newProviderInfo.form.secretKey" :rows="4" style="width: 520px"></Input>
        </FormItem>
        <FormItem required v-if="newProviderInfo.providerItem.tenantIdAttrName" :label="$t('t_tenant_id')">
          <Input type="text" v-model="newProviderInfo.form.tenantId" style="width: 520px"></Input>
        </FormItem>
        <FormItem required v-if="newProviderInfo.providerItem.subscriptionIdAttrName" :label="$t('t_subscription_id')">
          <Input type="text" v-model="newProviderInfo.form.subscriptionId" style="width: 520px"></Input>
        </FormItem>
      </Form>
      <div slot="footer">
        <Button @click="newProviderInfo.isShow = false">{{ $t('t_cancle') }}</Button>
        <Button type="primary" @click="confirmProviderInfo">{{ $t('t_save') }}</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import { getProviderInfo, getProviders, addProviderInfo, editProviderInfo, deleteProviderInfo } from '@/api/server'
export default {
  name: '',
  data () {
    return {
      name: '',
      newProviderInfo: {
        isShow: false,
        isAdd: true,
        providerOptions: [],
        providerItem: {},
        form: {
          createTime: '',
          createUser: '',
          id: '',
          name: '',
          provider: '',
          secretId: '',
          secretKey: '',
          tenantId: '',
          subscriptionId: '',
          updateTime: '',
          updateUser: ''
        }
      },
      emptyForm: {
        createTime: '',
        createUser: '',
        id: '',
        name: '',
        provider: '',
        secretId: '',
        secretKey: '',
        tenantId: '',
        subscriptionId: '',
        updateTime: '',
        updateUser: ''
      },
      tableColumns: [
        {
          title: this.$t('t_name'),
          key: 'name'
        },
        {
          title: this.$t('t_provider'),
          key: 'providerTitle'
        },
        {
          title: this.$t('t_secret_key'),
          key: 'secretKey'
        },
        {
          title: this.$t('t_secret_id'),
          key: 'secretId'
        },
        {
          title: this.$t('t_tenant_id'),
          key: 'tenantId'
        },
        {
          title: this.$t('t_subscription_id'),
          key: 'subscriptionId'
        },
        {
          title: this.$t('t_action'),
          key: 'action',
          width: 150,
          align: 'center',
          render: (h, params) => {
            return h('div', [
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
                      this.edit(params.row)
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
                  on: {
                    click: () => {
                      this.remove(params.row)
                    }
                  }
                },
                this.$t('t_delete')
              )
            ])
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
    edit (item) {
      this.newProviderInfo.form = {
        ...item
      }
      this.newProviderInfo.isAdd = false
      this.getProvider()
      this.newProviderInfo.isShow = true
    },
    remove (item) {
      this.$Modal.confirm({
        title: this.$t('t_confirm_delete'),
        'z-index': 1000000,
        loading: true,
        onOk: async () => {
          let res = await deleteProviderInfo(item.id)
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
    addProviderInfo () {
      this.newProviderInfo.isAdd = true
      this.newProviderInfo.form = JSON.parse(JSON.stringify(this.emptyForm))
      this.getProvider()
      this.newProviderInfo.isShow = true
    },
    validRequired () {
      if (
        !this.newProviderInfo.form.name ||
        !this.newProviderInfo.form.provider ||
        !this.newProviderInfo.form.secretId ||
        !this.newProviderInfo.form.secretKey ||
        (this.newProviderInfo.providerItem.tenantIdAttrName && !this.newProviderInfo.form.tenantId) ||
        (this.newProviderInfo.providerItem.subscriptionIdAttrName && !this.newProviderInfo.form.subscriptionId)
      ) {
        this.$Message.error(this.$t('t_validate_required'))
        return false
      } else {
        return true
      }
    },
    async confirmProviderInfo () {
      if (!this.validRequired()) {
        return false
      }
      const method = this.newProviderInfo.isAdd ? addProviderInfo : editProviderInfo
      const { statusCode } = method([this.newProviderInfo.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getTableData()
        this.newProviderInfo.isShow = false
      }
    },
    async getProvider () {
      const { statusCode, data } = await getProviders()
      if (statusCode === 'OK') {
        this.newProviderInfo.providerOptions = data || []
        this.newProviderInfo.providerItem =
          this.newProviderInfo.providerOptions.find(item => item.id === this.newProviderInfo.form.provider) || {}
      }
    },
    async getTableData () {
      const { statusCode, data } = await getProviderInfo(this.name)
      if (statusCode === 'OK') {
        this.tableData = data
      }
    },
    handleSelectProvider (val) {
      this.newProviderInfo.providerItem = this.newProviderInfo.providerOptions.find(item => item.id === val) || {}
    }
  }
}
</script>

<style scoped lang="scss">
.terraform-provider-info {
  .ivu-form-inline .ivu-form-item {
    margin-bottom: 10px;
  }
}
</style>
