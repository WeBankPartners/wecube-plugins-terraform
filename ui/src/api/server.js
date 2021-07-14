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

export const getPluginList = () => req.get('/plugins')
export const getProviderList = () => req.get('/providers')
export const createTemplate = data => req.post('/templates', data)
export const getTemplate = data => req.get('/templates')
export const getTemplateByPlugin = pluginId => req.get(`/templates/${pluginId}`)
export const getTemplateValue = templateValue => req.get(`/provider_template_values/${templateValue}`)
export const createTemplateValue = data => req.post(`/template_values`, data)
export const deleteTemplateValue = id => req.delete(`/template_values?ids=${id}`)
export const createProviderTemplateValues = data => req.post(`/provider_template_values`, data)

export const getInterfaceByPlugin = pluginId => req.get(`/interfaces?plugin=${pluginId}`)
export const addInterface = data => req.post(`/interfaces`, data)
export const deleteInterface = id => req.delete(`/interfaces?ids=${id}`)
export const editInterface = data => req.put(`/interfaces`, data)
export const getParamaByInterface = interfaceId => req.get(`/parameters?interface=${interfaceId}`)

export const addPlugin = data => req.post(`/plugins`, data)
export const editPlugin = data => req.put(`/plugins`, data)
export const addParameter = data => req.post(`/parameters`, data)
export const editParameter = data => req.put(`/parameters`, data)
export const deleteParameter = id => req.delete(`/parameters?ids=${id}`)
