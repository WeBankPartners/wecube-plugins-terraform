# _ coding:utf-8 _*_

from django.conf.urls import include, url
import disk_controller
import disk_attach_controller

urlpatterns = [
    url(r'^disk$', disk_controller.DiskController()),
    url(r'^disk/(?P<rid>[\w-]+)$', disk_controller.DiskIdController()),
    url(r'^backend/disk/create$', disk_controller.DiskAddController()),
    url(r'^backend/disk/delete$', disk_controller.DiskDeleteController()),

    url(r'^disk_attach$', disk_attach_controller.DiskAttachController()),
    url(r'^disk_attach/(?P<rid>[\w-]+)$', disk_attach_controller.DiskAttachIdController()),
    url(r'^backend/disk/attach$', disk_attach_controller.DiskAttachAddController()),
    url(r'^backend/disk/detach$', disk_attach_controller.DiskDetachController()),


]
