# _ coding:utf-8 _*_

from django.conf.urls import include, url
from mysql_controller import instance as mysql_instance
from mysql_controller import database as mysql_database
from mysql_controller import account as mysql_account
from mysql_controller import privilege as mysql_privilege
from mysql_controller import backup as mysql_backup
from kv_controller import kvstore_controller
from kv_controller import kvstore_backup_controller
from kv_controller import redis_controller
from kv_controller import memcached_conrtoller

urlpatterns = [
    url(r'^mysql$', mysql_instance.MysqlController()),
    url(r'^mysql/(?P<rid>[\w-]+)$', mysql_instance.MysqlIdController()),
    url(r'^backend/mysql/create$', mysql_instance.MysqlAddController()),
    url(r'^backend/mysql/delete$', mysql_instance.MysqlDeleteController()),

    url(r'^mysql_database$', mysql_database.MysqlDatabaseController()),
    url(r'^mysql_database/(?P<rid>[\w-]+)$', mysql_database.MysqlDatabaseIdController()),
    url(r'^backend/mysql_database/create$', mysql_database.MysqlDatabaseAddController()),
    url(r'^backend/mysql_database/delete$', mysql_database.MysqlDatabaseDeleteController()),

    url(r'^mysql_account$', mysql_account.MysqlAccountController()),
    url(r'^mysql_account/(?P<rid>[\w-]+)$', mysql_account.MysqlAccountIdController()),
    url(r'^backend/mysql_account/create$', mysql_account.MysqlAccountAddController()),
    url(r'^backend/mysql_account/delete$', mysql_account.MysqlAccountDeleteController()),

    url(r'^mysql_privilege$', mysql_privilege.MysqlPrivilegeController()),
    url(r'^mysql_privilege/(?P<rid>[\w-]+)$', mysql_privilege.MysqlPrivilegeIdController()),
    url(r'^backend/mysql_privilege/create$', mysql_privilege.MysqlPrivilegeAddController()),
    url(r'^backend/mysql_privilege/delete$', mysql_privilege.MysqlPrivilegeDeleteController()),

    url(r'^mysql_backup$', mysql_backup.MysqlBackupController()),
    url(r'^mysql_backup/(?P<rid>[\w-]+)$', mysql_backup.MysqlBackupIdController()),
    url(r'^backend/mysql_backup/create$', mysql_backup.MysqlBackupAddController()),
    url(r'^backend/mysql_backup/delete$', mysql_backup.MysqlBackupDeleteController()),

    url(r'^redis$', redis_controller.RedisController()),
    url(r'^redis/(?P<rid>[\w-]+)$', redis_controller.RedisIdController()),
    url(r'^backend/redis/create$', redis_controller.RedisAddController()),
    url(r'^backend/redis/delete$', redis_controller.RedisDeleteController()),

    url(r'^redis_backup$', redis_controller.RedisBackupController()),
    url(r'^redis_backup/(?P<rid>[\w-]+)$', redis_controller.RedisBackupIdController()),
    url(r'^backend/redis_backup/create$', redis_controller.RedisBackupAddController()),
    url(r'^backend/redis_backup/delete$', redis_controller.RedisBackupDeleteController()),

    url(r'^memcached$', memcached_conrtoller.MemcachedController()),
    url(r'^memcached/(?P<rid>[\w-]+)$', memcached_conrtoller.MemcachedIdController()),
    url(r'^backend/memcached/create$', memcached_conrtoller.MemcachedAddController()),
    url(r'^backend/memcached/delete$', memcached_conrtoller.MemcachedDeleteController()),

    url(r'^memcached_backup$', memcached_conrtoller.MemBackupController()),
    url(r'^memcached_backup/(?P<rid>[\w-]+)$', memcached_conrtoller.MemBackupIdController()),
    url(r'^backend/memcached_backup/create$', memcached_conrtoller.MemBackupAddController()),
    url(r'^backend/memcached_backup/delete$', memcached_conrtoller.MemBackupDeleteController()),

    url(r'^kvstore$', kvstore_controller.KvStoreController()),
    url(r'^kvstore/(?P<rid>[\w-]+)$', kvstore_controller.KvStoreIdController()),
    url(r'^backend/kvstore/create$', kvstore_controller.KvStoreAddController()),
    url(r'^backend/kvstore/delete$', kvstore_controller.KvStoreDeleteController()),

    url(r'^kvstore_backup$', kvstore_backup_controller.KvBackupController()),
    url(r'^kvstore_backup/(?P<rid>[\w-]+)$', kvstore_backup_controller.KvBackupIdController()),
    url(r'^backend/kvstore_backup/create$', kvstore_backup_controller.KvBackupAddController()),
    url(r'^backend/kvstore_backup/delete$', kvstore_backup_controller.KvBackupDeleteController()),
]
