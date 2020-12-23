import { req as request, baseURL } from './base'
import { pluginErrorMessage } from './base-plugin'
let req = request
if (window.request) {
  req = {
    post: (url, ...params) => pluginErrorMessage(window.request.post(baseURL + url, ...params)),
    get: (url, ...params) => pluginErrorMessage(window.request.get(baseURL + url, ...params)),
    delete: (url, ...params) => pluginErrorMessage(window.request.delete(baseURL + url, ...params)),
    put: (url, ...params) => pluginErrorMessage(window.request.put(baseURL + url, ...params)),
    patch: (url, ...params) => pluginErrorMessage(window.request.patch(baseURL + url, ...params))
  }
}

export const getTableData = url => req.get(url)
export const addTableRow = (url, data) => req.post(`${url}`, data)
export const editTableRow = (url, id, data) => req.patch(`${url}/${id}`, data)
export const deleteTableRow = (url, id) => req.delete(`${url}/${id}`)

export const boxDetect = (id, data) => req.post(`/itsdangerous/ui/v1/boxes/${id}/run`, data)

export const getRuleAttrById = id => req.get(`/itsdangerous/ui/v1/matchparams/${id}/args`)
export const getService = () => req.get(`/itsdangerous/v1/platform/services?__fields=serviceName`)
export const getRuleAttrByServiceName = serviceName =>
  req.get(`/itsdangerous/v1/platform/service-attributes?serviceName=${serviceName}`)

// Wecube Api
export const getAllDataModels = () => req.get(`/platform/v1/models`)
export const getTargetOptions = (pkgName, entityName) =>
  req.get(`/platform/v1/packages/${pkgName}/entities/${entityName}/retrieve`)
export const getEntityRefsByPkgNameAndEntityName = (pkgName, entityName) =>
  req.get(`/platform/v1/models/package/${pkgName}/entity/${entityName}`)
