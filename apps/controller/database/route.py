# _ coding:utf-8 _*_

from django.conf.urls import include, url
from mysql_controller import instance as mysql_instance
from mysql_controller import database as mysql_database
from mysql_controller import account as mysql_account
from mysql_controller import privilege as mysql_privilege
from mysql_controller import backup as mysql_backup

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

]
