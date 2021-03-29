# _ coding:utf-8 _*_

from django.conf.urls import include, url
import disk_controller
import object_storage_controller
import disk_attach_controller

urlpatterns = [
    url(r'^disk$', disk_controller.DiskController()),
    url(r'^disk/(?P<rid>[\w-]+)$', disk_controller.DiskIdController()),
    url(r'^backend/disk/apply$', disk_controller.DiskAddController()),
    url(r'^backend/disk/destroy$', disk_controller.DiskDeleteController()),
    url(r'^backend/disk/source$', disk_controller.DiskSourceController()),

    url(r'^disk_attach$', disk_attach_controller.DiskAttachController()),
    url(r'^disk_attach/(?P<rid>[\w-]+)$', disk_attach_controller.DiskAttachIdController()),
    url(r'^backend/disk/attach$', disk_attach_controller.DiskAttachAddController()),
    url(r'^backend/disk/detach$', disk_attach_controller.DiskDetachController()),

    url(r'^object_storage$', object_storage_controller.ObjectStorageController()),
    url(r'^object_storage/(?P<rid>[\w-]+)$', object_storage_controller.ObjectStorageIdController()),
    url(r'^backend/object_storage/apply$', object_storage_controller.ObjectStorageAddController()),
    url(r'^backend/object_storage/destroy$', object_storage_controller.ObjectStorageDeleteController()),
    url(r'^backend/object_storage/source$', object_storage_controller.OSSSourceController()),

]
