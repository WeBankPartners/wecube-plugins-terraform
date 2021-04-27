# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import traceback
from shutil import copyfile
from lib.logs import logger
from lib.command import command
from lib.json_helper import format_json_dumps
from lib.date_time import get_datetime_point_str
from wecube_plugins_terraform.settings import TERRAFORM_BASE_PATH
from apps.background.lib.commander.terraform import TerraformDriver


class TerraformResource(object):
    terraformDriver = TerraformDriver()

    def __init__(self):
        self.resource_name = None
        self.resource_workspace = None

    def get_workpath(self, rid, provider, region, **kwargs):
        return os.path.join(TERRAFORM_BASE_PATH, provider, region, self.resource_workspace, rid)

    def create_workpath(self, rid, provider, region, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param kwargs:
        :return:
        '''

        # _path = os.path.join(TERRAFORM_BASE_PATH, provider, region, self.resource_workspace, rid)
        _path = self.get_workpath(rid, provider, region, **kwargs)
        if not os.path.exists(_path):
            os.makedirs(_path)

        return _path

    def init_workspace(self, _path, provider):
        return self.terraformDriver.init_resource_dir(dir_path=_path, provider=provider)

    def write_provider_define(self, path, define_json):
        '''

        :param rid:
        :param path:
        :param define_json:
        :return:
        '''

        file = os.path.join(path, "provider.tf.json")
        if os.path.exists(file):
            backupfile = file + "_" + get_datetime_point_str()
            copyfile(file, backupfile)

        with open(file, 'wb+') as f:
            json.dump(define_json, f, ensure_ascii=False, indent=4)

        logger.info(format_json_dumps(define_json))

    def write_define(self, rid, path, define_json):
        '''

        :param rid:
        :param path:
        :param define_json:
        :return:
        '''

        backupfile = ""
        file = os.path.join(path, "%s.tf.json" % rid)
        if os.path.exists(file):
            backupfile = file + "_" + get_datetime_point_str()
            copyfile(file, backupfile)

        with open(os.path.join(path, "%s.tf.json" % rid), 'wb+') as f:
            json.dump(define_json, f, ensure_ascii=False, indent=4)

        logger.info(format_json_dumps(define_json))
        return backupfile

    def rewrite_state(self, path, state_file):
        '''

        :param rid:
        :param path:
        :param define_json:
        :return:
        '''

        _statefile = os.path.join(path, "terraform.tfstate")
        if os.path.exists(_statefile):
            return

        with open(_statefile, 'wb+') as f:
            json.dump(state_file, f, ensure_ascii=False, indent=4)

        logger.info("rewrite state file")
        logger.info(format_json_dumps(state_file))

    def rollback_workspace(self, path):
        if os.path.exists(path):
            backuppath = path + "_" + get_datetime_point_str()
            logger.info("try rollback workspace %s to %s" % (path, backuppath))
            command(cmd="mv %s %s" % (path, backuppath))

    def run(self, path, skip_backup=None):
        '''

        :param path:
        :return:
        '''

        _statefile = os.path.join(path, "terraform.tfstate")
        if os.path.exists(_statefile):
            backupfile = _statefile + "_" + get_datetime_point_str()
            copyfile(_statefile, backupfile)

        try:
            self.terraformDriver.plan(path)
        except:
            logger.info(traceback.format_exc())
            logger.info("terraform plan run failed, continue ... ")

        self.terraformDriver.apply(path, auto_approve="")
        return self.terraformDriver.resource_result(path)

    def is_need_imort(self, path):
        '''

        :param path:
        :return:
        '''
        _statefile = os.path.join(path, "terraform.tfstate")
        if os.path.exists(_statefile):
            return False

        return True

    def run_import(self, from_source, dest_source, path, state=None):
        '''
        # 非资产类型资源没有id, 使用两个字段  资产id  + 标识id 进行导入
        :param from_source:
        :param dest_source:
        :param path:
        :param state:
        :return:
        '''

        self.terraformDriver.import_state(from_source, dest_source, path, state)
        return self.terraformDriver.resource_result(path)

    def refresh(self, path):
        '''

        :param path:
        :return:
        '''

        _statefile = os.path.join(path, "terraform.tfstate")
        if os.path.exists(_statefile):
            backupfile = _statefile + "_" + get_datetime_point_str()
            copyfile(_statefile, backupfile)
        self.terraformDriver.refresh(path)
        return self.terraformDriver.resource_result(path)

    def destroy_ensure_file(self, rid, path):
        '''

        :param rid:
        :param path:
        :return:
        '''

        file = os.path.join(path, "%s.tf.json" % rid)
        if os.path.exists(file):
            return True

        return False

    def ensure_provider_file(self, path):
        '''

        :param rid:
        :param path:
        :return:
        '''
        file = os.path.join(path, "provider.tf.json")
        if os.path.exists(file):
            return True

        return False

    def run_destroy(self, path):
        '''

        :param path:
        :return:
        '''

        try:
            self.terraformDriver.plan(path)
        except:
            logger.info(traceback.format_exc())
            logger.info("terraform plan run failed, continue ... ")

        return TerraformDriver().destroy(dir_path=path, auto_approve="")
