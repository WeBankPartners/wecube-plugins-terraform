# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
from shutil import copyfile
from lib.date_time import get_datetime_point_str
from wecube_plugins_terraform.settings import TERRAFORM_BASE_PATH
from apps.background.lib.commander.terraform import TerraformDriver


class TerraformResource(object):
    terraformDriver = TerraformDriver()

    def __init__(self):
        self.resource_name = None
        self.resource_workspace = None

    def create_workpath(self, rid, provider, region, **kwargs):
        _path = os.path.join(TERRAFORM_BASE_PATH, provider, region, self.resource_workspace, rid)
        if not os.path.exists(_path):
            os.makedirs(_path)
            self.terraformDriver.init_resource_dir(dir_path=_path, provider=provider)

        return _path

    def write_define(self, rid, path, define_json):
        file = os.path.join(path, "%s.tf.json" % rid)
        if os.path.exists(file):
            backupfile = file + "_" + get_datetime_point_str()
            copyfile(file, backupfile)

        with open(os.path.join(path, "%s.tf.json" % rid), 'wb+') as f:
            json.dump(define_json, f, ensure_ascii=False, indent=4)

    def run(self, path):
        self.terraformDriver.apply(path, auto_approve="")
        return self.terraformDriver.resource_result(path)
