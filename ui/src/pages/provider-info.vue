<template>
  <div class=" ">
    <Form inline>
      <FormItem prop="user">
        <Input type="text" v-model="name" style="width:300px" :placeholder="$t('t_name')"> </Input>
      </FormItem>
      <FormItem>
        <Button type="primary" @click="getTableData" style="margin-left: 24px">{{ $t('t_search') }}</Button>
        <Button @click="addProviderInfo" style="margin-left: 24px">{{ $t('t_add') }}</Button>
      </FormItem>
    </Form>
    <Table border :columns="tableColumns" :data="tableData"></Table>
    <Modal
      v-model="newProviderInfo.isShow"
      :title="newProviderInfo.isAdd ? $t('t_add') : $t('t_edit') + $t('t_provider_info')"
      @on-ok="confirmProviderInfo"
      @on-cancel="confirmProviderInfo.isShow = false"
    >
      <Form inline :label-width="80">
        <FormItem :label="$t('t_name')">
          <Input type="text" v-model="newProviderInfo.form.name" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_provider')">
          <Select v-model="newProviderInfo.form.provider" ref="selectProvider" style="width:400px">
            <Button type="success" style="width:100%" @click="addProvider" size="small">
              <Icon type="ios-add" size="24"></Icon>
            </Button>
            <Option v-for="provider in newProviderInfo.providerOptions" :value="provider.id" :key="provider.id"
              >{{ provider.name
              }}<span style="float:right">
                <Button
                  @click="editProvider(provider)"
                  icon="ios-create-outline"
                  style="color: #19be6b;"
                  size="small"
                ></Button>
              </span>
              <span style="float:right">
                <Button @click="deleteProvider(provider)" icon="ios-trash" type="error" size="small"></Button>
              </span>
            </Option>
          </Select>
        </FormItem>
        <FormItem :label="$t('t_secret_key')">
          <Input type="textarea" v-model="newProviderInfo.form.secretKey" :rows="4" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_secret_id')">
          <Input type="textarea" v-model="newProviderInfo.form.secretId" :rows="4" style="width:400px"></Input>
        </FormItem>
      </Form>
    </Modal>
    <Modal
      v-model="newProvider.isShow"
      :title="newProvider.isAdd ? $t('t_add') : $t('t_edit') + $t('t_provider')"
      @on-ok="confirmProvider"
      @on-cancel="confirmProvider.isShow = false"
    >
      <Form inline :label-width="80">
        <FormItem :label="$t('t_name')">
          <Input type="text" v-model="newProvider.form.name" style="width:400px"></Input>
        </FormItem>
        <FormItem :label="$t('t_version')">
          <Input type="textarea" v-model="newProvider.form.version" :rows="4" style="width:400px"></Input>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  getProviderInfo,
  getProviders,
  addProvider,
  editProvider,
  deleteProvider,
  addProviderInfo,
  editProviderInfo,
  deleteProviderInfo
} from '@/api/server'
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
          regionAttrName: '',
          secretIdAttrName: '',
          secretKeyAttrName: '',
          updateTime: '',
          updateUser: '',
          version: ''
        }
      },
      newProviderInfo: {
        isShow: false,
        isAdd: true,
        providerOptions: [],
        form: {
          createTime: '',
          createUser: '',
          id: '',
          name: '',
          provider: '',
          secretId: '',
          secretKey: '',
          updateTime: '',
          updateUser: ''
        }
      },
      tableColumns: [
        {
          title: this.$t('t_name'),
          key: 'name'
        },
        {
          title: this.$t('t_provider'),
          key: 'provider'
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
    addProvider () {
      this.$refs.selectProvider.visible = false
      this.newProvider.isAdd = true
      this.newProvider.isShow = true
    },
    editProvider (item) {
      this.$refs.selectProvider.visible = false
      this.newProvider.form = {
        ...item
      }
      this.newProvider.isAdd = false
      this.newProvider.isShow = true
    },
    async confirmProvider () {
      this.$refs.selectProvider.visible = false
      const method = this.newProvider.isAdd ? addProvider : editProvider
      const { statusCode } = await method([this.newProvider.form])
      if (statusCode === 'OK') {
        this.$Notice.success({
          title: 'Successful',
          desc: 'Successful'
        })
        this.getProvider()
        this.confirmProvider.isShow = false
      }
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
            this.getProvider()
          }
        },
        onCancel: () => {}
      })
    },
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
      this.getProvider()
      this.newProviderInfo.isShow = true
    },
    async confirmProviderInfo () {
      const method = this.newProviderInfo.isAdd ? addProviderInfo : editProviderInfo
      const { statusCode } = await method([this.newProviderInfo.form])
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
        this.newProviderInfo.providerOptions = data
      }
    },
    async getTableData () {
      const { statusCode, data } = await getProviderInfo(this.name)
      if (statusCode === 'OK') {
        this.tableData = data
      }
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
