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

export const getPluginList = () => req.get('/terraform/api/v1/plugins')
export const getProviderList = () => req.get('/terraform/api/v1/providers')
export const createTemplate = data => req.post('/terraform/api/v1/templates', data)
export const getTemplate = data => req.get('/terraform/api/v1/templates')
export const deleteTemplate = id => req.delete(`/terraform/api/v1/templates?ids=${id}`)
export const getTemplateByPlugin = pluginId => req.get(`/terraform/api/v1/templates/${pluginId}`)
export const getTemplateValue = templateValue => req.get(`/terraform/api/v1/provider_template_values/${templateValue}`)
export const createTemplateValue = data => req.post(`/terraform/api/v1/template_values`, data)
export const deleteTemplateValue = id => req.delete(`/terraform/api/v1/template_values?ids=${id}`)
export const createProviderTemplateValues = data => req.post(`/terraform/api/v1/provider_template_values`, data)

export const getInterfaceByPlugin = pluginId => req.get(`/terraform/api/v1/interfaces?plugin=${pluginId}`)
export const addInterface = data => req.post(`/terraform/api/v1/interfaces`, data)
export const deleteInterface = id => req.delete(`/terraform/api/v1/interfaces?ids=${id}`)
export const editInterface = data => req.put(`/terraform/api/v1/interfaces`, data)
export const getParamaByInterface = interfaceId => req.get(`/terraform/api/v1/parameters?interface=${interfaceId}`)

export const addPlugin = data => req.post(`/terraform/api/v1/plugins`, data)
export const deletePlugin = id => req.delete(`/terraform/api/v1/plugins?ids=${id}`)
export const editPlugin = data => req.put(`/terraform/api/v1/plugins`, data)
export const addParameter = data => req.post(`/terraform/api/v1/parameters`, data)
export const editParameter = data => req.put(`/terraform/api/v1/parameters`, data)
export const deleteParameter = id => req.delete(`/terraform/api/v1/parameters?ids=${id}`)

export const getSourceByfilter = (interfaceId, providerId) =>
  req.get(`/terraform/api/v1/sources?interfaceId=${interfaceId}&providerId=${providerId}`)
export const addSource = data => req.post(`/terraform/api/v1/sources`, data)
export const editSource = data => req.put(`/terraform/api/v1/sources`, data)
export const deleteSource = id => req.delete(`/terraform/api/v1/sources?ids=${id}`)
export const getSourceByProvider = providerId => req.get(`/terraform/api/v1/sources?providerId=${providerId}`)
export const getArgBySource = sourceId => req.get(`/terraform/api/v1/tf_arguments?sourceId=${sourceId}`)
export const updateArgs = data => req.post(`/terraform/api/v1/tf_arguments`, data)
export const deleteArg = id => req.delete(`/terraform/api/v1/tf_arguments?ids=${id}`)
export const getAttrBySource = sourceId => req.get(`/terraform/api/v1/tfstate_attributes?sourceId=${sourceId}`)
export const updateAttrs = data => req.post(`/terraform/api/v1/tfstate_attributes`, data)
export const deleteAttrs = id => req.delete(`/terraform/api/v1/tfstate_attributes?ids=${id}`)

export const getProviders = name => req.get(`/terraform/api/v1/providers`)
export const addProvider = data => req.post(`/terraform/api/v1/providers`, data)
export const editProvider = data => req.put(`/terraform/api/v1/providers`, data)
export const deleteProvider = id => req.delete(`/terraform/api/v1/providers?ids=${id}`)
export const getProviderInfo = name => req.get(`/terraform/api/v1/provider_infos?name=${name}`)
export const addProviderInfo = data => req.post(`/terraform/api/v1/provider_infos`, data)
export const editProviderInfo = data => req.put(`/terraform/api/v1/provider_infos`, data)
export const deleteProviderInfo = id => req.delete(`/terraform/api/v1/provider_infos?ids=${id}`)

export const getDebugInfo = () => req.get(`/terraform/api/v1/resource_data_debugs`)

export const debuggerRequest = (plugin, action, data) =>
  req.post(`/terraform/api/v1/terraform_debug/${plugin}/${action}`, data)

export const terraformExport = (provider, plugin) =>
  req.get(`/terraform/api/v1/provider_plugin_config/export?provider=${provider}&plugin=${plugin}`)

export const getInstanceData = () => req.get(`/terraform/api/v1/resource_datas`)

export const instanceDataDownload = data => req.post(`/terraform/api/v1/providers/download?id=${data}`)
