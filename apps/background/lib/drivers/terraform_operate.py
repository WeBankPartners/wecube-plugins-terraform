# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
from shutil import copyfile
from lib.logs import logger
from lib.json_helper import format_json_dumps
from lib.date_time import get_datetime_point_str
from wecube_plugins_terraform.settings import TERRAFORM_BASE_PATH
from apps.background.lib.commander.terraform import TerraformDriver


class TerraformResource(object):
    terraformDriver = TerraformDriver()

    def __init__(self):
        self.resource_name = None
        self.resource_workspace = None

    def create_workpath(self, rid, provider, region, **kwargs):
        '''

        :param rid:
        :param provider:
        :param region:
        :param kwargs:
        :return:
        '''

        _path = os.path.join(TERRAFORM_BASE_PATH, provider, region, self.resource_workspace, rid)
        if not os.path.exists(_path):
            os.makedirs(_path)
            self.terraformDriver.init_resource_dir(dir_path=_path, provider=provider)

        return _path

    def write_define(self, rid, path, define_json):
        '''

        :param rid:
        :param path:
        :param define_json:
        :return:
        '''

        file = os.path.join(path, "%s.tf.json" % rid)
        if os.path.exists(file):
            backupfile = file + "_" + get_datetime_point_str()
            copyfile(file, backupfile)

        with open(os.path.join(path, "%s.tf.json" % rid), 'wb+') as f:
            json.dump(define_json, f, ensure_ascii=False, indent=4)

        logger.info(format_json_dumps(define_json))

    def run(self, path):
        '''

        :param path:
        :return:
        '''

        _statefile = os.path.join(path, "terraform.tfstate")
        if os.path.exists(_statefile):
            backupfile = _statefile + "_" + get_datetime_point_str()
            copyfile(_statefile, backupfile)
        self.terraformDriver.apply(path, auto_approve="")
        return self.terraformDriver.resource_result(path)

    def destory_ensure_file(self, rid, path):
        '''

        :param rid:
        :param path:
        :return:
        '''

        file = os.path.join(path, "%s.tf.json" % rid)
        if os.path.exists(file):
            return True

        return False

    def run_destory(self, path):
        '''

        :param path:
        :return:
        '''

        return TerraformDriver().destroy(dir_path=path, auto_approve="")
