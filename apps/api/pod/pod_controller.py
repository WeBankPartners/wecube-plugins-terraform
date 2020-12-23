# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import time

from apps.api.rc.base import RCApi
from apps.common.kubernetes_auth_info import validate_cluster_auth
from apps.common.kubernetes_auth_info import validate_cluster_info
from core import local_exceptions as exception_common
from core import validation
from core.controller import BaseController
from lib.uuid_util import get_uuid
from .base import PodApi


class PodBaseController(BaseController):
    def not_null_keys(self):
        return ["kubernetes_url"]

    def before_handler(self, request, data, **kwargs):
        validate_cluster_auth(data)
        validation.not_allowed_null(data=data,
                                    keys=self.not_null_keys()
                                    )

        validation.validate_string("kubernetes_url", data["kubernetes_url"])
        validation.validate_string("kubernetes_token", data.get("kubernetes_token"))
        validation.validate_string("kubernetes_ca", data.get("kubernetes_ca"))
        validation.validate_string("apiversion", data.get("apiversion"))
        validation.validate_string("namespace", data.get("namespace"))
        validate_cluster_info(data["kubernetes_url"])


class PodListController(PodBaseController):
    name = "Pod"
    resource_describe = "Pod"
    allow_methods = ('POST',)
    resource = PodApi()

    def response_templete(self, data):
        return []

    def main_response(self, request, data, **kwargs):
        result = self.resource.list(kubernetes_url=data["kubernetes_url"],
                                    kubernetes_token=data.get("kubernetes_token"),
                                    kubernetes_ca=data.get("kubernetes_ca"),
                                    apiversion=data.get("apiversion"),
                                    namespace=data.get("namespace")
                                    )
        return result


class PodDetailController(PodBaseController):
    name = "Pod.id"
    resource_describe = "Pod"
    allow_methods = ("POST",)
    resource = PodApi()

    def not_null_keys(self):
        return ["kubernetes_url", "name"]

    def response_templete(self, data):
        return {"pod_restart_policy": "", "pod_uid": "",
                "pod_created_time": "", "pod_ip": "",
                "pod_start_time": "", "host_memory": "",
                "host_ip": "", "pod_annotations": "",
                "pod_labels": "", "host_cpu": "", "pod_node_name": "",
                "host_name": "", "pod_api_version": "",
                "pod_namespace": "", "host_uuid": "",
                "containers": "", "pod_name": data["name"],
                "id": data.get("id")}

    def main_response(self, request, data, **kwargs):
        kubernetes_url = data["kubernetes_url"]
        kubernetes_token = data.get("kubernetes_token")
        kubernetes_ca = data.get("kubernetes_ca")

        name = data["name"]
        result = self.resource.detail(name=name,
                                      kubernetes_url=kubernetes_url,
                                      kubernetes_token=kubernetes_token,
                                      kubernetes_ca=kubernetes_ca,
                                      apiversion=data.get("apiversion"),
                                      namespace=data.get("namespace", "default")
                                      )
        if result:
            result["id"] = data.get("id")
        return result


class PodSearchController(BaseController):
    name = "Pod.id"
    resource_describe = "Pod"
    allow_methods = ("POST",)
    resource = RCApi()

    def not_null_keys(self):
        return ["kubernetes_url", "name"]

    def response_templete(self, data):
        return {"pod_restart_policy": "", "pod_uid": "",
                "pod_created_time": "", "pod_ip": "",
                "pod_start_time": "", "host_memory": "",
                "host_ip": "", "pod_annotations": "",
                "pod_labels": "", "host_cpu": "", "pod_node_name": "",
                "host_name": "", "pod_api_version": "",
                "pod_namespace": "", "host_uuid": "",
                "containers": "", "pod_name": data["name"]}

    def main_response(self, request, data, **kwargs):
        kubernetes_url = data["kubernetes_url"]
        kubernetes_token = data.get("kubernetes_token")
        kubernetes_ca = data.get("kubernetes_ca")

        name = data["name"]
        result = self.resource.search_rc_pods(selector={"app": data["name"]},
                                              kubernetes_url=kubernetes_url,
                                              kubernetes_token=kubernetes_token,
                                              kubernetes_ca=kubernetes_ca,
                                              apiversion=data.get("apiversion"),
                                              namespace=data.get("namespace", "default"))

        return result

    def _format_data(self, data):
        validate_cluster_auth(data)
        validation.not_allowed_null(data=data,
                                    keys=["kubernetes_url", "name"]
                                    )

        kubernetes_url = data["kubernetes_url"]
        kubernetes_token = data.get("kubernetes_token")
        kubernetes_ca = data.get("kubernetes_ca")

        validation.validate_string("kubernetes_url", kubernetes_url)
        validation.validate_string("kubernetes_token", kubernetes_token)
        validation.validate_string("kubernetes_ca", kubernetes_ca)
        validate_cluster_info(kubernetes_url)

        name = data["name"]

        return {"kubernetes_url": kubernetes_url,
                "name": name,
                "kubernetes_token": kubernetes_token,
                "kubernetes_ca": kubernetes_ca,
                "namespace": data.get("namespace", "default"),
                "apiversion": data.get("apiversion"),
                "id": data.get("id"),
                "callbackParameter": data.get("callbackParameter")
                }

    def create(self, request, data, **kwargs):
        search_datas = []
        for info in data:
            search_datas.append(self._format_data(info))

        success_pod = []
        failed_pod = []
        for search_data in search_datas:
            pods = self.resource.search_rc_pods(selector={"app": search_data["name"]},
                                                kubernetes_url=search_data["kubernetes_url"],
                                                kubernetes_token=search_data["kubernetes_token"],
                                                kubernetes_ca=search_data["kubernetes_ca"],
                                                apiversion=search_data.get("apiversion"),
                                                namespace=search_data.get("namespace", "default"))
            if not pods:
                _data = {"errorCode": 1, "errorMessage": "创建失败",
                         "pod_restart_policy": "", "pod_uid": "",
                         "pod_created_time": "", "pod_ip": "",
                         "pod_start_time": "", "host_memory": "", "host_ip": "",
                         "pod_annotations": "", "pod_labels": "",
                         "host_cpu": "", "pod_node_name": "", "host_name": "",
                         "pod_api_version": "", "pod_namespace": "",
                         "host_uuid": "", "containers": "",
                         "pod_name": search_data["name"]}

                _data["id"] = search_data["id"]
                _data["callbackParameter"] = search_data["callbackParameter"]
                failed_pod.append(_data)
            else:
                _pod = pods[0]
                _pod["id"] = search_data["id"]
                _pod["callbackParameter"] = search_data["callbackParameter"]
                success_pod += [_pod]

        failed_name = []
        return_data = success_pod + failed_pod
        for failed in failed_pod:
            failed_name.append(failed["pod_name"])

        failed_name = ",".join(failed_name)
        if failed_pod:
            raise exception_common.ResourceNotSearchError(param="name",
                                                          msg="未查找到pod %s" % failed_name,
                                                          return_data=return_data)

        return len(return_data), return_data


class PodCreateController(PodBaseController):
    name = "pod"
    resource_describe = "pod"
    allow_methods = ("POST")
    resource = RCApi()

    def not_null_keys(self):
        return ["kubernetes_url", "name", "image", "containername", "containerports"]

    def before_handler(self, request, data, **kwargs):
        validate_cluster_auth(data)
        validation.not_allowed_null(data=data,
                                    keys=self.not_null_keys()
                                    )

        kubernetes_url = data["kubernetes_url"]
        kubernetes_token = data.get("kubernetes_token")
        kubernetes_ca = data.get("kubernetes_ca")

        validation.validate_string("kubernetes_url", kubernetes_url)
        validation.validate_string("kubernetes_token", kubernetes_token)
        validation.validate_string("kubernetes_ca", kubernetes_ca)
        validate_cluster_info(kubernetes_url)

        name = data["name"]
        image = data["image"]

        containerlabels = data.get("containerlabels", {})
        if containerlabels:
            containerlabels = validation.validate_dict("containerlabels", containerlabels)
        else:
            containerlabels = {"app": name}

        selector = data.get("selector", {})
        if selector:
            selector = validation.validate_dict("selector", selector)
        else:
            selector = {"app": name}

        labels = data.get("labels", {})
        if labels:
            labels = validation.validate_dict("labels", labels)
        else:
            labels = {"app": name}

        env = self._format_env(data.get("env"))
        # validation.validate_string("env", data.get("env"))

        containerports = data.get("containerports")
        if containerports:
            containerports = validation.validate_port(containerports)

        request_cpu = data.get("request_cpu")
        if request_cpu:
            request_cpu = validation.validate_number("request_cpu",
                                                     value=request_cpu,
                                                     min=0.01, max=32)

        request_memory = data.get("request_memory")
        if request_memory:
            request_memory = validation.validate_number("request_memory",
                                                        value=request_memory,
                                                        min=128, max=64 * 1024)

        limit_cpu = data.get("limit_cpu")
        if limit_cpu:
            limit_cpu = validation.validate_number("limit_cpu",
                                                   value=limit_cpu,
                                                   min=0.01, max=32)

        limit_memory = data.get("limit_memory")
        if limit_memory:
            limit_memory = validation.validate_number("limit_memory",
                                                      value=limit_memory,
                                                      min=128, max=64 * 1024)

        containername = data.get("containername")
        if containername:
            containername = validation.validate_string("containername", containername)

        imagePullSecrets = data.get("imagePullSecrets")
        if imagePullSecrets:
            imagePullSecrets = validation.validate_string("imagePullSecrets", imagePullSecrets)

        docker_register_server = data.get("docker_register_server")
        if docker_register_server:
            docker_register_server = validation.validate_string("docker_register_server",
                                                                docker_register_server)
        else:
            docker_register_server = image.split("/")[0]

        docker_password = data.get("docker_password")
        if docker_password:
            docker_password = validation.validate_string("docker_password", docker_password)

        docker_username = data.get("docker_username")
        if docker_username:
            docker_username = validation.validate_string("docker_username", docker_username)

        replicas = data.get("replicas", 1)
        apiversion = data.get("apiversion", "v1")

        return {"kubernetes_url": kubernetes_url,
                "name": name,
                "id": data.get("id"),
                "image": image,
                "containerports": containerports,
                "kubernetes_token": kubernetes_token,
                "kubernetes_ca": kubernetes_ca,
                "apiversion": apiversion,
                "replicas": replicas,
                "labels": labels,
                "selector": selector,
                "containername": containername,
                "containerlabels": containerlabels,
                "env": env,
                "request_cpu": request_cpu,
                "request_memory": request_memory,
                "limit_cpu": limit_cpu,
                "limit_memory": limit_memory,
                "namespace": data.get("namespace", "default"),
                'docker_password': docker_password,
                'docker_username': docker_username,
                'docker_register_server': docker_register_server,
                'imagePullSecrets': imagePullSecrets
                }

    def _format_env(self, envstring):
        env = {}
        envstring = validation.validate_string("env", envstring)
        envstring = envstring.replace("\u0001", "")
        env_keys = envstring.split("=")[0]
        env_keys_list = env_keys.split(",")
        env_values = envstring.split("=")[1]
        env_values_list = env_values.split(",")
        for i in xrange(len(env_keys_list)):
            env[env_keys_list[i]] = env_values_list[i]

        return env

    def _format_data(self, deployment):
        validate_cluster_auth(deployment)
        validation.not_allowed_null(data=deployment,
                                    keys=["kubernetes_url", "name", "image",
                                          "containername", "containerports"]
                                    )

        kubernetes_url = deployment["kubernetes_url"]
        kubernetes_token = deployment.get("kubernetes_token")
        kubernetes_ca = deployment.get("kubernetes_ca")

        validation.validate_string("kubernetes_url", kubernetes_url)
        validation.validate_string("kubernetes_token", kubernetes_token)
        validation.validate_string("kubernetes_ca", kubernetes_ca)
        validate_cluster_info(kubernetes_url)

        name = deployment["name"]
        image = deployment["image"]

        containerlabels = deployment.get("containerlabels", {})
        if containerlabels:
            containerlabels = validation.validate_dict("containerlabels", containerlabels)
        else:
            containerlabels = {"app": name}

        selector = deployment.get("selector", {})
        if selector:
            selector = validation.validate_dict("selector", selector)
        else:
            selector = {"app": name}

        labels = deployment.get("labels", {})
        if labels:
            labels = validation.validate_dict("labels", labels)
        else:
            labels = {"app": name}

        env = self._format_env(deployment.get("env"))

        containerports = deployment.get("containerports")
        if containerports:
            containerports = validation.validate_port(containerports)

        request_cpu = deployment.get("request_cpu")
        if request_cpu:
            request_cpu = validation.validate_number("request_cpu",
                                                     value=request_cpu,
                                                     min=0.01, max=32)

        request_memory = deployment.get("request_memory")
        if request_memory:
            request_memory = validation.validate_number("request_memory",
                                                        value=request_memory,
                                                        min=128, max=64 * 1024)

        limit_cpu = deployment.get("limit_cpu")
        if limit_cpu:
            limit_cpu = validation.validate_number("limit_cpu",
                                                   value=limit_cpu,
                                                   min=0.01, max=32)

        limit_memory = deployment.get("limit_memory")
        if limit_memory:
            limit_memory = validation.validate_number("limit_memory",
                                                      value=limit_memory,
                                                      min=128, max=64 * 1024)

        containername = deployment.get("containername")
        if containername:
            containername = validation.validate_string("containername", containername)

        imagePullSecrets = deployment.get("imagePullSecrets")
        if imagePullSecrets:
            imagePullSecrets = validation.validate_string("imagePullSecrets", imagePullSecrets)

        docker_register_server = deployment.get("docker_register_server")
        if docker_register_server:
            docker_register_server = validation.validate_string("docker_register_server",
                                                                docker_register_server)
        else:
            docker_register_server = image.split("/")[0]

        docker_password = deployment.get("docker_password")
        if docker_password:
            docker_password = validation.validate_string("docker_password", docker_password)

        docker_username = deployment.get("docker_username")
        if docker_username:
            docker_username = validation.validate_string("docker_username", docker_username)

        replicas = deployment.get("replicas", 1)
        apiversion = deployment.get("apiversion", "v1")

        deploymentname = deployment.get("deployment")

        callbackParameter = deployment.get("callbackParameter")

        return {"kubernetes_url": kubernetes_url,
                "name": name,
                "id": deployment.get("id"),
                "image": image,
                "containerports": containerports,
                "kubernetes_token": kubernetes_token,
                "kubernetes_ca": kubernetes_ca,
                "apiversion": apiversion,
                "replicas": replicas,
                "labels": labels,
                "selector": selector,
                "containername": containername,
                "containerlabels": containerlabels,
                "env": env,
                "request_cpu": request_cpu,
                "request_memory": request_memory,
                "limit_cpu": limit_cpu,
                "limit_memory": limit_memory,
                "namespace": deployment.get("namespace", "default"),
                'docker_password': docker_password,
                'docker_username': docker_username,
                'docker_register_server': docker_register_server,
                'imagePullSecrets': imagePullSecrets,
                "callbackParameter": callbackParameter
                }

    def _fetch_deployment(self, deployments):
        info = {}
        for deployment in deployments:
            name = deployment.get("name")
            if name in info.keys():
                info[name].append(deployment)
            else:
                info[name] = [deployment]

        result = []
        for deploymentname, deploy in info.items():
            if len(deploy) > 1:
                raise exception_common.ResourceUniqueException("name", deploymentname)

            uuid = deploy[0].get("id", None) or get_uuid()
            _info = {"id": uuid,
                     "name": deploymentname,
                     "kubernetes_url": deploy[0]["kubernetes_url"],
                     "kubernetes_token": deploy[0]["kubernetes_token"],
                     "kubernetes_ca": deploy[0]["kubernetes_ca"],
                     "apiversion": deploy[0]["apiversion"],
                     "selector": deploy[0]["selector"],
                     "labels": deploy[0]["labels"],
                     "namespace": deploy[0]["namespace"],
                     "replicas": deploy[0]["replicas"],
                     'docker_password': deploy[0]["docker_password"],
                     'docker_username': deploy[0]["docker_username"],
                     'docker_register_server': deploy[0]["docker_register_server"],
                     'imagePullSecrets': deploy[0]["imagePullSecrets"]
                     }

            containers = []

            for container_info in deploy:
                build_info = {}
                build_info["image"] = container_info["image"]
                build_info["name"] = container_info["containername"]

                env = container_info["env"]
                env_info = [{"name": "envcreator", "value": "wecube_plugins_kubernetes"}]
                if env:
                    for key, value in env.items():
                        env_info.append({"name": key, "value": value})

                build_info["env"] = env_info
                build_info["ports"] = [{"containerPort": container_info["containerports"]}]
                build_info["resources"] = {"requests": {"cpu": container_info.get("request_cpu", 0.01),
                                                        "memory": str(
                                                            container_info.get("request_memory", "256")) + "Mi"},
                                           "limits": {"cpu": container_info.get("limit_cpu", 1),
                                                      "memory": str(container_info.get("limit_memory", "256")) + "Mi"}}

                containers.append(build_info)

            _info["containers"] = containers
            _info["callbackParameter"] = deploy[0]["callbackParameter"]
            result.append(_info)

        return result

    def create(self, request, data, **kwargs):
        '''
        :param request:
        :param data:
        :return:
        '''

        metadata_lists = []
        success_deploy = []
        failed_deploy = []
        for deployment in data:
            metadata_lists.append(self._format_data(deployment))

        create_datas = self._fetch_deployment(metadata_lists)

        for create_data in create_datas:
            try:
                _res = self.resource.create_pod_containers(uuid=create_data["id"],
                                                           kubernetes_url=create_data.get("kubernetes_url"),
                                                           name=create_data.get("name"),
                                                           containers=create_data.get("containers"),
                                                           image_tags=create_data.get("image_tags", {}),
                                                           kubernetes_token=create_data.get("kubernetes_token"),
                                                           kubernetes_ca=create_data.get("kubernetes_ca"),
                                                           apiversion=create_data.get("apiversion"),
                                                           labels=create_data.get("labels"),
                                                           replicas=create_data.get("replicas"),
                                                           selector=create_data.get("selector"),
                                                           namespace=create_data.get("namespace", "default"),
                                                           imagePullSecrets=create_data.get("imagePullSecrets"),
                                                           docker_password=create_data.get("docker_password"),
                                                           docker_username=create_data.get("docker_username"),
                                                           docker_register_server=create_data.get(
                                                               "docker_register_server")
                                                           )

                if _res and _res.get("status") != 409:
                    success_deploy.append(create_data)
                else:
                    create_data["status"] = 409
                    failed_deploy.append(create_data)
            except Exception, e:
                failed_deploy.append(create_data)

        result = []
        if success_deploy:
            time.sleep(1.5)

        for deployment_info in success_deploy:
            pods = self.resource.search_rc_pods(selector=deployment_info["selector"],
                                                kubernetes_url=deployment_info.get("kubernetes_url"),
                                                kubernetes_token=create_data.get("kubernetes_token"),
                                                kubernetes_ca=create_data.get("kubernetes_ca"),
                                                apiversion=create_data.get("apiversion"),
                                                namespace=create_data.get("namespace", "default"))
            _pod = pods[0]
            _pod["id"] = deployment_info["id"]
            _pod["callbackParameter"] = deployment_info["callbackParameter"]

            result = result + [_pod]

        failed_name = []
        for failed in failed_deploy:
            failed_name.append(failed["name"])
            _failed_data_ = {"errorCode": 1, "errorMessage": "创建失败",
                             "pod_restart_policy": "", "pod_uid": "",
                             "pod_created_time": "", "pod_ip": "",
                             "pod_start_time": "", "host_memory": "",
                             "host_ip": "", "pod_annotations": "",
                             "pod_labels": "", "host_cpu": "", "pod_node_name": "",
                             "host_name": "", "pod_api_version": "",
                             "pod_namespace": "", "host_uuid": "",
                             "containers": "", "pod_name": failed["name"]}
            _pod["id"] = failed["id"]
            _pod["callbackParameter"] = failed["callbackParameter"]

            if failed.get("status", 0) == 409:
                _failed_data_["errorMessage"] = "%s 已经存在， 请使用其他名称" % failed["name"]

            result = result + [_failed_data_]

        failed_name = ",".join(failed_name)

        if failed_deploy:
            raise exception_common.ResourceNotCompleteError(param="",
                                                            msg="pod %s 部署失败" % failed_name,
                                                            return_data=result)

        return len(result), result


class PodDeleteController(PodBaseController):
    name = "Pod.id"
    resource_describe = "Pod"
    allow_methods = ("POST",)
    resource = PodApi()

    def not_null_keys(self):
        return ["kubernetes_url", "name"]

    def response_templete(self, data):
        return {"id": data.get("id"), "name": data["name"]}

    def main_response(self, request, data, **kwargs):
        result = self.resource.delete(name=data["name"],
                                      kubernetes_url=data["kubernetes_url"],
                                      kubernetes_token=data.get("kubernetes_token"),
                                      kubernetes_ca=data.get("kubernetes_ca"),
                                      apiversion=data.get("apiversion"),
                                      namespace=data.get("namespace", "default")
                                      )

        return {"id": data.get("id"), "name": data["name"]}
