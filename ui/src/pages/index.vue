<template>
  <div id="cmdb">
    <div class="header">
      <Header />
    </div>
    <div class="content-container">
      <transition name="fade" mode="out-in">
        <router-view class="pages"></router-view>
      </transition>
    </div>
  </div>
</template>

<script>
import Header from './components/header'
export default {
  components: {
    Header
  },
  data () {
    return {
      isShowBreadcrum: true,
      allMenusAry: [],
      parentBreadcrumb: '',
      childBreadcrumb: '',
      isSetting: this.$route.path.startsWith('/setting')
    }
  },
  methods: {},
  mounted () {}
}
</script>

<style lang="scss" scoped>
#cmdb {
  height: 100%;
}
.header {
  width: 100%;
  background-color: #515a6e;
  display: block;
}
.content-container {
  height: calc(100% - 50px);
  padding: 5px 30px;
}

.ivu-breadcrumb {
  color: #515a6e;
}
</style>
