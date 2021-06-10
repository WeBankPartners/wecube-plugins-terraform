<template>
  <div class=" ">
    <!-- 云厂商 -->
    <div class="marginbottom params-each">
      <label class="col-md-2 label-name">{{ $t('tf_provider') }}:</label>
      <Select v-model="provider" @on-change="changeProvider" filterable style="width: 338px">
        <Option v-for="providerItem in providerOptions" :value="providerItem.name" :key="providerItem.id">{{
          providerItem.name
        }}</Option>
      </Select>
      <label class="required-tip">*</label>
    </div>
    <!-- 资源类型 -->
    <div class="marginbottom params-each">
      <label class="col-md-2 label-name">{{ $t('tf_resource_type') }}:</label>
      <Select v-model="resourceType" @on-change="changeResourceType" filterable style="width: 338px">
        <Option
          v-for="resourceTypeItem in resourceTypeOptions"
          :value="resourceTypeItem.name"
          :key="resourceTypeItem.id"
          >{{ resourceTypeItem.name }}</Option
        >
      </Select>
      <label class="required-tip">*</label>
    </div>
    <!-- 属性 -->
    <div class="marginbottom params-each">
      <label class="col-md-2 label-name">{{ $t('tf_property') }}:</label>
      <Select v-model="resourceProperty" @on-change="changeResourceProperty" filterable style="width: 338px">
        <Option
          v-for="resourcePropertyItem in resourcePropertyOptions"
          :value="resourcePropertyItem.name"
          :key="resourcePropertyItem.id"
          >{{ resourcePropertyItem.name }}</Option
        >
      </Select>
      <label class="required-tip">*</label>
    </div>
    <!-- 名称 -->
    <div class="marginbottom params-each">
      <label class="col-md-2 label-name">{{ $t('tf_parameter_conversion') }}:</label>
      <Select v-model="name" @on-change="changeName" filterable style="width: 338px">
        <Option v-for="nameItem in nameOptions" :value="nameItem.name" :key="nameItem.id">{{ nameItem.name }}</Option>
      </Select>
      <label class="required-tip">*</label>
    </div>
  </div>
</template>

<script>
import { getTableData } from '@/api/server'
export default {
  name: '',
  data () {
    return {
      provider: '',
      providerOptions: [],
      resourceType: '',
      resourceTypeOptions: [],
      resourceProperty: '',
      resourcePropertyOptions: [],
      name: '',
      nameOptions: []
    }
  },
  mounted () {
    this.getProvider()
  },
  methods: {
    // clear () {
    //   this.provider = ''
    //   this.providerOptions = []
    //   this.resourceType = ''
    //   this.resourceTypeOptions = []
    //   this.resourceProperty = ''
    //   this.resourcePropertyOptions = []
    //   this.name = ''
    //   this.nameOptions = []
    // },
    // injectionData (val) {
    //   this.clear()
    //   this.provider = val.provider
    //   this.resourceType = val.resource
    //   this.resourceProperty = val.property
    //   this.getProvider()
    //   this.getResourceType()
    //   this.getResourceProperty()
    // },
    async getProvider () {
      this.providerOptions = []
      const { status, data } = await getTableData('/terraform/v1/configer/provider')
      if (status === 'OK') {
        this.providerOptions = data.data
      }
    },
    changeProvider () {
      this.clearResourceType()
      this.getResourceType()
      this.clearResourceProperty()
      this.clearName()
      this.sendValue()
    },
    async getResourceType () {
      this.resourceTypeOptions = []
      const { status, data } = await getTableData('/terraform/v1/configer/resourceList?provider=' + this.provider)
      if (status === 'OK') {
        this.resourceTypeOptions = data.resource
      }
    },
    changeResourceType () {
      this.clearResourceProperty()
      this.getResourceProperty()
      this.clearName()
      this.sendValue()
    },
    clearResourceType () {
      this.resourceType = ''
      this.resourceTypeOptions = []
    },
    changeResourceProperty (val) {
      this.clearName()
      this.getName()
      this.sendValue()
    },
    async getResourceProperty () {
      this.resourcePropertyOptions = []
      const { status, data } = await getTableData(
        '/terraform/v1/configer/resourceAttr?provider=' + this.provider + '&resource_type=' + this.resourceType
      )
      if (status === 'OK') {
        this.resourcePropertyOptions = data.resource
      }
    },
    clearResourceProperty () {
      this.resourceProperty = ''
      this.resourcePropertyOptions = []
    },
    changeName (val) {
      this.sendValue()
    },
    async getName () {
      this.nameOptions = []
      const { status, data } = await getTableData(
        '/terraform/v1/configer/configList?provider=' +
          this.provider +
          '&resource_type=' +
          this.resourceType +
          '&property=' +
          this.resourceProperty
      )
      if (status === 'OK') {
        this.nameOptions = data.resource
      }
    },
    clearName () {
      this.name = ''
      this.nameOptions = []
    },
    sendValue () {
      const find = this.nameOptions.find(item => this.name === item.id)
      const params = {
        provider: this.provider || '',
        name: (find && find.name) || '',
        origin_name: (find && find.origin_name) || ''
      }
      this.$emit('callbackValue', params)
    }
  },
  components: {}
}
</script>

<style scoped lang="less">
.marginbottom {
  margin-top: 12px;
}
.label-name {
  text-align: right;
  padding: 0;
}
</style>
