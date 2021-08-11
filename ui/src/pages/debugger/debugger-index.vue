<template>
  <div class="monitor-config-index">
    <section>
      <Tabs :value="activeTab" @on-click="changeTab">
        <template v-for="(tabItem, tabIndex) in tabs">
          <TabPane :label="$t(tabItem.label)" :name="tabItem.path" :key="tabIndex"> </TabPane>
        </template>
      </Tabs>
      <router-view></router-view>
    </section>
  </div>
</template>

<script>
export default {
  name: '',
  data () {
    return {
      activeTab: '/debuggerIndex/debuggerData',
      tabs: [
        { label: 't_debugger_data', path: '/debuggerIndex/debuggerData' },
        { label: 't_debugger_request', path: '/debuggerIndex/debuggerRequest' }
      ]
    }
  },
  mounted () {
    this.activeTab = this.$route.path
  },
  methods: {
    changeTab (path) {
      this.activeTab = path
      if (this.$route.path === path) return
      this.$router.push({ path: path })
    }
  },
  components: {}
}
</script>

<style lang="scss" scoped>
.home-page {
  align-items: center;
  background-color: #fff;
  display: flex;
  font-size: 75px;
  font-weight: 600;
  height: 100%;
  justify-content: center;
}
</style>
