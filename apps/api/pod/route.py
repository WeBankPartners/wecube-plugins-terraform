# _ coding:utf-8 _*_

from django.conf.urls import include, url
from .pod_controller import PodListController
from .pod_controller import PodIdController
from .pod_controller import PodDetailController
from .pod_controller import PodSearchController
from .pod_controller import PodCreateController
from .pod_controller import PodDeleteController

urlpatterns = [
    url(r'^list$', PodListController()),
    url(r'^describe$', PodIdController()),
    url(r'^detail$', PodDetailController()),
    url(r'^search$', PodSearchController()),
    url(r'^create$', PodCreateController()),
    url(r'^delete$', PodDeleteController()),
]
