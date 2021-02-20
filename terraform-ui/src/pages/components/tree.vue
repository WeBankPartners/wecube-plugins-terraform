<template>
  <div>
    <Tree :data="data5" :render="renderContent" class="demo-tree-render"></Tree>
  </div>
</template>
<script>
export default {
  data () {
    return {
      data5: [
        {
          title: 'parent 1',
          expand: true,
          render: (h, { root, node, data }) => {
            return (
              <span style="display: inline-block;width: 100%">
                <span>{data.title}</span>
                <span style="display: inline-block;float: right;margin-right: 32px">
                  <Button
                    onClick={() => this.append(data)}
                    type="primary"
                    style="width:64px"
                    size="small"
                    icon="ios-add"
                  ></Button>
                </span>
              </span>
            )
          },
          children: []
        }
      ],
      childrenT: []
    }
  },
  mounted () {
    this.initJSON()
  },
  methods: {
    renderContent (h, { root, node, data }) {
      let formateNodeData = (v, tag) => {
        const res = target({ children: this.data5[0].children }, data.nodeKey)
        console.log(res)
        res[tag] = v
        console.log(this.data5[0])
      }

      let target = (js, nodeKey) => {
        let tmp = null
        let levelOne = js.children.find(item => item.nodeKey === data.nodeKey)
        let levelTow = js.children.findIndex(item => item.nodeKey > data.nodeKey)
        tmp = levelOne || js.children[levelTow - 1] || js.children.slice(-1)[0]
        if (tmp.nodeKey === nodeKey) {
          return tmp
        } else {
          return target(tmp, nodeKey)
        }
      }

      if (data.children.length !== 0) {
        return (
          <span style="display: 'inline-block';width: '100%'">
            <span style="padding: 0 4px">
              Key:<Input value={data.title} style="width:100px" onInput={v => formateNodeData(v, 'key')}></Input>
            </span>
            <span style="display: inline-block;float: right;margin-right: 32px">
              <Button onClick={() => this.append(data)} type="default" size="small" icon="ios-add"></Button>
              <Button
                onClick={() => this.remove(root, node, data)}
                type="default"
                size="small"
                icon="ios-remove"
              ></Button>
            </span>
          </span>
        )
      } else {
        return (
          <span style="display: 'inline-block';width: '100%'">
            <span style="padding: 0 4px">
              Key:<Input value={data.title} style="width:100px" onInput={v => formateNodeData(v, 'key')}></Input>
            </span>
            <span style="padding: 0 4px">
              Value:<Input value={data.value} style="width:100px" onInput={v => formateNodeData(v, 'value')}></Input>
            </span>
            <span style="display: inline-block;float: right;margin-right: 32px">
              <Button onClick={() => this.append(data)} type="default" size="small" icon="ios-add"></Button>
              <Button
                onClick={() => this.remove(root, node, data)}
                type="default"
                size="small"
                icon="ios-remove"
              ></Button>
            </span>
          </span>
        )
      }
    },
    append (data) {
      const children = data.children || []
      children.push({
        title: 'appended node',
        key: 'appended node',
        expand: true,
        children: [],
        value: ''
      })
      this.$set(data, 'children', children)
    },
    remove (root, node, data) {
      const parentKey = root.find(el => el === node).parent
      const parent = root.find(el => el.nodeKey === parentKey).node
      const index = parent.children.indexOf(data)
      parent.children.splice(index, 1)
    },
    initJSON () {
      const jsonJ = {
        instance_id: {
          convert: 'instance_id',
          allow_null: 0,
          type: 'string'
        },
        eip_id: {
          convert: 'eip_id',
          allow_null: 0,
          type: 'string'
        },
        name: '-',
        private_ip: {
          convert: 'private_ip',
          allow_null: 1,
          type: 'string'
        }
      }
      const data = this.formatTreeData(jsonJ)
      this.data5[0].children = data
    },
    isJson (obj) {
      return (
        typeof obj === 'object' &&
        Object.prototype.toString.call(obj).toLowerCase() === '[object object]' &&
        !obj.length
      )
    },
    formatTreeData (tmp) {
      const keys = Object.keys(tmp)
      let childrenTmp = []
      keys.forEach(key => {
        let params = {
          title: key,
          expand: true,
          key: key,
          value: tmp[key]
        }
        if (this.isJson(tmp[key])) {
          params.children = this.formatTreeData(tmp[key])
        } else {
          params.children = []
        }
        childrenTmp.push(params)
      })
      return childrenTmp
    }
  }
}
</script>
<style>
.demo-tree-render .ivu-tree-title {
  width: 100%;
}
</style>
