export default function sortedArgument (items) {
  let level = 0
  items.forEach(el => {
    el.__level = level
    el.__completed = false
  })
  items.forEach(el => {
    if (el.__completed) {
      return
    }
    if (!el.objectName) {
      level += 1
      el.__level += level
      el.__completed = true
      if (el.type === 'object') {
        level = rSortedArgument(
          items.filter(el2 => el2.objectName === el.id),
          items,
          level
        )
      }
    }
  })
  items.sort((a, b) => a.__level - b.__level)
  return items
}
function rSortedArgument (items, allItems, level) {
  items.forEach(el => {
    level += 1
    el.__level += level
    el.__completed = true
    if (el.type === 'object') {
      level = this.rSortedArgument(
        allItems.filter(el2 => el2.objectName === el.id),
        allItems,
        level
      )
    }
  })
  return level
}
