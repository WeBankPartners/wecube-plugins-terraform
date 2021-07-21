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
export const deleteTemplate = id => req.delete(`/templates?ids=${id}`)
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
export const deletePlugin = id => req.delete(`/plugins?ids=${id}`)
export const editPlugin = data => req.put(`/plugins`, data)
export const addParameter = data => req.post(`/parameters`, data)
export const editParameter = data => req.put(`/parameters`, data)
export const deleteParameter = id => req.delete(`/parameters?ids=${id}`)

export const getSourceByfilter = (interfaceId, providerId) =>
  req.get(`/sources?interfaceId=${interfaceId}&providerId=${providerId}`)
export const addSource = data => req.post(`/sources`, data)
export const editSource = data => req.put(`/sources`, data)
export const deleteSource = id => req.delete(`/sources?ids=${id}`)
export const getSourceByProvider = providerId => req.get(`/sources?providerId=${providerId}`)
export const getArgBySource = sourceId => req.get(`/tf_arguments?sourceId=${sourceId}`)
export const updateArgs = data => req.post(`/tf_arguments`, data)
export const deleteArg = id => req.delete(`/tf_arguments?ids=${id}`)
export const getAttrBySource = sourceId => req.get(`/tfstate_attributes?sourceId=${sourceId}`)
export const updateAttrs = data => req.post(`/tfstate_attributes`, data)
export const deleteAttrs = id => req.delete(`/tfstate_attributes?ids=${id}`)

export const getProviders = name => req.get(`/providers`)
export const addProvider = data => req.post(`/providers`, data)
export const editProvider = data => req.put(`/providers`, data)
export const deleteProvider = id => req.delete(`/providers?ids=${id}`)
export const getProviderInfo = name => req.get(`/provider_infos?name=${name}`)
export const addProviderInfo = data => req.post(`/provider_infos`, data)
export const editProviderInfo = data => req.put(`/provider_infos`, data)
export const deleteProviderInfo = id => req.delete(`/provider_infos?ids=${id}`)
