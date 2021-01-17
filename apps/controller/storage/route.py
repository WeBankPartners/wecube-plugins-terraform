# _ coding:utf-8 _*_

from django.conf.urls import include, url
from disk_controller import DiskController
from disk_controller import DiskAddController
from disk_controller import DiskIdController
from disk_controller import DiskDeleteController

urlpatterns = [
    url(r'^disk$', DiskController()),
    url(r'^disk/(?P<rid>[\w-]+)$', DiskIdController()),
    url(r'^backend/disk/create$', DiskAddController()),
    url(r'^backend/disk/delete$', DiskDeleteController()),

]
