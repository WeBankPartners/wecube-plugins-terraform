<template>
  <div class=" ">
    <!-- 搜索区 -->
    <div>
      <Row>
        <Col span="5">
          <span>{{ $t('t_plugin') }}</span>
          <Select v-model="model1" style="width:200px">
            <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
          </Select>
        </Col>
        <Col span="5">
          <span>{{ $t('t_plugin') }}</span>
          <Select v-model="model1" style="width:200px">
            <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
          </Select>
        </Col>
        <Col span="5">
          <span>{{ $t('t_plugin') }}</span>
          <Select v-model="model1" style="width:200px">
            <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
          </Select>
        </Col>
        <Col span="5">
          <Button type="primary">{{ $t('t_search') }}</Button>
        </Col>
      </Row>
    </div>
    <!-- 配置区 -->
    <div style="margin-top: 36px; max-height: 840px; overflow: auto; text-align: center;">
      <header>
        <div style="font-size: 0">
          <div class="table-title title-width-level2">
            source
          </div>
          <div class="table-title title-width-level1">
            名称
          </div>
          <div class="table-title title-width-level1">
            数据类型
          </div>
          <div class="table-title title-width-level1">
            多个支持
          </div>
          <div class="table-title title-width-level1">
            允许为空
          </div>
          <div class="table-title title-width-level3" style="vertical-align: top;">
            <div style="line-height:40px">
              转换配置
            </div>
            <div style="font-size: 0;margin-top: -2px;">
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                转换类型
              </div>
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                关联Param
              </div>
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                关联值
              </div>
              <div
                class="table-title title-width-level1"
                style="line-height: 40px;
    vertical-align: bottom;"
              >
                关联Attr
              </div>
            </div>
          </div>
          <div class="table-title title-width-level1">
            Parameter
          </div>
          <div class="table-title title-width-level1">
            默认值
          </div>
          <div class="table-title title-width-level1">
            操作
          </div>
        </div>
      </header>
      <div style="font-size: 0;margin-top:-1px;margin-left:-4px">
        <div class="style-widthout-height" style="font-size: 0;margin-left:-1px">
          <div class="style-widthout-height" style="width:120px;line-height:158px;border:none">
            source1
          </div>
          <div class="style-widthout-height" style="width:120px;vertical-align: top;border:none">
            <div class="style-widthout-height" style="font-size: 0;margin-left:-1px;border:none">
              <div class="style-widthout-height" style="width:120px;line-height:79px;border:none">
                xxx
              </div>
              <div class="style-widthout-height" style="width:120px;line-height:79px;border:none">
                arg
              </div>
            </div>
          </div>
        </div>
        <div style="display:inline-block;vertical-align: top;margin-top:1px;margin-letf:-1px;">
          <div>
            <div style="margin-top: -1px;" v-for="item in [1, 2]" :key="item">
              <template>
                <div class="table-col title-width-level1">
                  <Input size="small" />
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Checkbox v-model="single">Checkbox</Checkbox>
                </div>
                <div class="table-col title-width-level1">
                  <Checkbox v-model="single">Checkbox</Checkbox>
                </div>

                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Input size="small" />
                </div>
                <div class="table-col title-width-level1">
                  <Button type="primary" ghost size="small">{{ $t('t_save') }}</Button>
                  <Button type="error" ghost size="small">{{ $t('t_delete') }}</Button>
                </div>
              </template>
            </div>
          </div>
          <div>
            <div style="margin-top: -1px;" v-for="item in [1, 2]" :key="item">
              <template>
                <div class="table-col title-width-level1">
                  <Input size="small" />
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Checkbox v-model="single">Checkbox</Checkbox>
                </div>
                <div class="table-col title-width-level1">
                  <Checkbox v-model="single">Checkbox</Checkbox>
                </div>

                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Select v-model="model1" size="small">
                    <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                  </Select>
                </div>
                <div class="table-col title-width-level1">
                  <Input size="small" />
                </div>
                <div class="table-col title-width-level1">
                  <Button type="primary" ghost size="small">{{ $t('t_save') }}</Button>
                  <Button type="error" ghost size="small">{{ $t('t_delete') }}</Button>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: '',
  data () {
    return {
      single: '',
      cityList: [
        {
          value: 'New York',
          label: 'New York'
        }
      ],
      model1: ''
    }
  },
  mounted () {},
  methods: {}
}
</script>

<style scoped lang="scss">
.table-title {
  display: inline-block;
  border: 1px solid #e9e9e9;
  font-size: 12px;
  margin-left: -1px;
  height: 80px;
  line-height: 80px;
  // width: 250px;
  // padding: 8px 4px;
  font-weight: bold;
  color: #515a6e;
  font-size: 14px;
}
.table-col {
  display: inline-block;
  border: 1px solid #e9e9e9;
  font-size: 12px;
  margin-left: -1px;
  height: 40px;
  // width: 250px;
  padding: 8px 4px;
  font-weight: bold;
  color: #515a6e;
  font-size: 14px;
}
.style-widthout-height {
  display: inline-block;
  border: 1px solid #e9e9e9;
  font-size: 12px;
  margin-left: -1px;
  // padding: 8px 4px;
  font-weight: bold;
  color: #515a6e;
  font-size: 14px;
}

.title-width-level1 {
  width: 120px;
}
.title-width-level2 {
  width: 240px;
}
.title-width-level3 {
  width: 480px;
}
</style>
