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
      activeTab: '/dangerousIndex/policy',
      tabs: [
        { label: 'hr_box', path: '/dangerousIndex/boxes' },
        { label: 'hr_policies', path: '/dangerousIndex/policy' },
        { label: 'hr_rule', path: '/dangerousIndex/rule' },
        { label: 'hr_match_params', path: '/dangerousIndex/match-params' },
        { label: 'hr_subject', path: '/dangerousIndex/subjects' },
        { label: 'hr_target', path: '/dangerousIndex/targets' },
        { label: 'hr_plugin_params', path: '/dangerousIndex/plugin-params' }
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
