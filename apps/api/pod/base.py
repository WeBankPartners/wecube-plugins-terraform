# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.node.base import NodeApi
from apps.background.lib.drivers.KubernetesDrivers import PodManager


class PodApi(object):
    def list(self, kubernetes_url, kubernetes_token=None,
             kubernetes_ca=None, apiversion=None,
             namespace=None, label_selector=None, **kwargs):
        '''

        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param label_selector: "app=redis"
        :param kwargs:
        :return:
        '''

        return PodManager.list(url=kubernetes_url, token=kubernetes_token,
                               cafile=kubernetes_ca, version=apiversion,
                               namespace=namespace,
                               label_selector=label_selector,
                               **kwargs)

    def __pod_info__(self, name, kubernetes_url,
                     kubernetes_token=None, kubernetes_ca=None,
                     apiversion=None, namespace="default", **kwargs):
        '''

        :param name:
        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        return PodManager.query(name,
                                url=kubernetes_url,
                                token=kubernetes_token,
                                cafile=kubernetes_ca,
                                version=apiversion,
                                namespace=namespace)

    def detail(self, name, kubernetes_url,
               kubernetes_token=None, kubernetes_ca=None,
               apiversion=None, namespace="default", **kwargs):

        '''
        not exception
        :param name:
        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        pod_info = self.__pod_info__(name=name,
                                     kubernetes_url=kubernetes_url,
                                     kubernetes_token=kubernetes_token,
                                     kubernetes_ca=kubernetes_ca,
                                     apiversion=apiversion,
                                     namespace=namespace)
        if pod_info:
            result = self.__format_pod_info__(pod_info,
                                              kubernetes_url,
                                              kubernetes_token=kubernetes_token,
                                              kubernetes_ca=kubernetes_ca,
                                              apiversion=apiversion,
                                              namespace=namespace
                                              )
            return result
        else:
            return pod_info

    def describe(self, name, kubernetes_url,
                 kubernetes_token=None, kubernetes_ca=None,
                 apiversion=None, namespace="default", **kwargs):
        '''

        :param name:
        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        pod_info = self.__pod_info__(name=name,
                                     kubernetes_url=kubernetes_url,
                                     kubernetes_token=kubernetes_token,
                                     kubernetes_ca=kubernetes_ca,
                                     apiversion=apiversion,
                                     namespace=namespace)
        if pod_info:
            node_name = pod_info["spec"]["node_name"]
            node = NodeApi().node_info(node_name, kubernetes_url,
                                       kubernetes_token=kubernetes_token,
                                       kubernetes_ca=kubernetes_ca,
                                       apiversion=apiversion,
                                       namespace=namespace)

            node["ipaddress"] = pod_info["status"]["host_ip"]
            pod_info["node"] = node

        return pod_info

    def __container_info__(self, containers):
        '''

        :param containers:
        :return:
        '''

        result = []
        for container in containers:
            _info_ = {"container_image": container["image"],
                      "container_env": container["env"],
                      "container_ports": container["ports"],
                      "container_name": container["name"],
                      "container_volume_mounts": container["volume_mounts"],
                      "container_volume_devices": container["volume_devices"],
                      "container_command": container["command"]
                      }
            result.append(_info_)

        return result

    def __format_pod_info__(self, pod_info, kubernetes_url,
                            kubernetes_token=None, kubernetes_ca=None,
                            apiversion=None, namespace="default"):

        '''

        :param pod_info:
        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :return:
        '''
        node_name = pod_info["spec"]["node_name"]
        node = NodeApi().node_info(node_name, kubernetes_url,
                                   kubernetes_token=kubernetes_token,
                                   kubernetes_ca=kubernetes_ca,
                                   apiversion=apiversion,
                                   namespace=namespace)

        templete = {}
        templete["pod_api_version"] = pod_info["api_version"]

        templete["host_cpu"] = node.get("cpu")
        templete["host_memory"] = node.get("memory")
        templete["host_name"] = node.get("hostname")
        templete["host_ip"] = pod_info["status"]["host_ip"]
        templete["host_uuid"] = node.get("uuid")
        templete["host_cmdb_id"] = node.get("host_cmdb_id")

        templete["pod_ip"] = pod_info["status"]["pod_ip"]
        templete["pod_start_time"] = pod_info["status"]["start_time"]
        templete["pod_name"] = pod_info["metadata"]["name"]
        templete["pod_namespace"] = pod_info["metadata"]["namespace"]
        templete["pod_labels"] = pod_info["metadata"]["labels"]
        templete["pod_created_time"] = pod_info["metadata"]["creation_timestamp"]
        templete["pod_uid"] = pod_info["metadata"]["uid"]
        templete["pod_node_name"] = node_name
        templete["pod_restart_policy"] = pod_info["spec"]["restart_policy"]
        templete["pod_annotations"] = pod_info["metadata"]["annotations"]
        templete["status"] = 0
        _containers = pod_info["spec"]["containers"]
        container_list = self.__container_info__(containers=_containers)

        templete["containers"] = container_list
        return templete

    def rc_pod_detail(self, kubernetes_url,
                      label_selector=None,
                      kubernetes_token=None,
                      kubernetes_ca=None,
                      apiversion=None,
                      namespace=None, **kwargs):
        '''

        :param kubernetes_url:
        :param label_selector:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        pod_lists = PodManager.list(url=kubernetes_url, token=kubernetes_token,
                                    cafile=kubernetes_ca, version=apiversion,
                                    namespace=namespace,
                                    label_selector=label_selector,
                                    **kwargs)

        rc_pod_lists = []
        for pod_info in pod_lists:
            rc_pod = self.__format_pod_info__(pod_info,
                                              kubernetes_url,
                                              kubernetes_token=kubernetes_token,
                                              kubernetes_ca=kubernetes_ca,
                                              apiversion=apiversion,
                                              namespace=namespace
                                              )
            rc_pod_lists.append(rc_pod)

        return rc_pod_lists

    def delete(self, name, kubernetes_url, kubernetes_token=None,
               kubernetes_ca=None, apiversion=None, namespace="default", **kwargs):
        '''

        :param name:
        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        return PodManager.delete(name, url=kubernetes_url,
                                 token=kubernetes_token,
                                 cafile=kubernetes_ca,
                                 version=apiversion,
                                 namespace=namespace)
