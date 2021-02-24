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
          title: 'JSON',
          expand: true,
          key: 'JSON',
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
      childrenT: [],
      finalJson: {},
      jsonJ: {
        originJSON: {
          // region: 'region111',
          // secret_key: 'secret_key11',
          // secret_id: 'access_key11'
        }
      }
      // jsonJ: {
      // instance_id: {
      //   convert: 'sdf',
      //   allow_null: 0,
      //   type: 'string'
      // },
      // eip_id: {
      //   convert: 'eip_id',
      //   allow_null: 0,
      //   type: 'string'
      // },
      // name: '-',
      // private_ip: {
      //   convert: 'private_ip',
      //   allow_null: 1,
      //   type: 'string'
      // }
      // }
    }
  },
  mounted () {
    this.initJSON(this.jsonJ)
  },
  methods: {
    renderContent (h, { root, node, data }) {
      let formateNodeData = (v, tag) => {
        const res = target({ children: this.data5[0].children }, data.nodeKey)
        console.log('res:', res)
        data.path = data.path.replace('undefined.', '')
        let attrs = data.path.split('.')
        console.log('path:', data.path)
        let xx = attrs.slice(0, attrs.length - 1)
        console.log(xx, this.jsonJ)
        const ss = this.renderValue(this.jsonJ, xx)
        console.log('操作对象', ss, res.key, v)
        console.log('旧，新：', res.key, v)
        if (tag === 'key') {
          if (xx[0] === 'parent') {
            console.log(1)
            this.jsonJ[v] = this.jsonJ[res.key]
            delete this.jsonJ[res.key]
          } else {
            console.log(2)
            ss[v] = ss[res.key]
            delete ss[res.key]
          }
        } else {
          if (xx[0] === 'parent') {
            console.log(11)
            this.jsonJ[res.key] = v
          } else {
            console.log(22)
            ss[res.key] = v
          }
        }

        if (tag === 'key') {
          if (xx[0] === 'parent') {
            xx.push(v)
            data.path = xx.join('.')
          } else {
            xx.push(v)
            data.path = xx.join('.')
          }
          res[tag] = res['title'] = v
        } else {
          res[tag] = v
        }
        console.log(data.path)
        console.log(this.data5[0].children)
        console.log(this.jsonJ)
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
    renderValue (item, attrs) {
      let item_tmp = item
      let n = 0
      for (n in attrs) {
        if (attrs[n] in item_tmp) {
          item_tmp = item_tmp[attrs[n]]
        } else {
          return {}
        }
      }
      return item_tmp
    },
    // 添加节点，赋初始值
    append (data) {
      const tag = 'key_' + Math.floor(Math.random() * 4000 + 1000)
      const children = data.children || []
      children.push({
        title: tag,
        key: tag,
        expand: true,
        children: [],
        value: '',
        path: data.path + '.' + tag
      })
      data.value = {
        [tag]: ''
      }
      this.$set(data, 'children', children)
      console.log(data)
      if (data.path) {
        let attrs = data.path.split('.')
        let xx = attrs.slice(0, attrs.length - 1)
        let ss = this.renderValue(this.jsonJ, xx)
        console.log(ss)
        ss[data.key] = {
          [tag]: ''
        }
        // console.log(ss)
        // this.jsonJ[tag] = ''
        // debugger
      } else {
        this.jsonJ[tag] = ''
      }
      console.log(this.jsonJ)
    },
    remove (root, node, data) {
      const parentKey = root.find(el => el === node).parent
      const parent = root.find(el => el.nodeKey === parentKey).node
      const index = parent.children.indexOf(data)
      parent.children.splice(index, 1)

      data.path = data.path.replace('undefined.', '')
      let attrs = data.path.split('.')
      let xx = attrs.slice(0, attrs.length - 1)
      console.log(xx)
      let ss = this.renderValue(this.jsonJ, xx)
      if (xx[0] === 'parent') {
        delete this.jsonJ[data.key]
      } else {
        // 父节点包含多节点删除节点，其他父节点置空
        if (Object.keys(ss).length === 1) {
          let xx2 = attrs.slice(0, attrs.length - 2)
          let ss2 = this.renderValue(this.jsonJ, xx2)
          const key = xx.slice(-1)[0]
          ss2[key] = {}
        } else {
          delete ss[data.key]
        }
      }
      console.log(ss)
      console.log(this.jsonJ)
    },
    initJSON (val) {
      // this.$nextTick(() => {
      // this.jsonJ = val
      const data = this.formatTreeData(this.jsonJ, 'parent')
      this.data5[0].children = data
      // })
    },
    isJson (obj) {
      return (
        typeof obj === 'object' &&
        Object.prototype.toString.call(obj).toLowerCase() === '[object object]' &&
        !obj.length
      )
    },
    formatTreeData (tmp, path) {
      const keys = Object.keys(tmp)
      let childrenTmp = []
      keys.forEach(key => {
        let params = {
          title: key,
          expand: true,
          key: key,
          value: tmp[key],
          path: path + '.' + key
        }
        if (this.isJson(tmp[key])) {
          params.children = this.formatTreeData(tmp[key], key)
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
