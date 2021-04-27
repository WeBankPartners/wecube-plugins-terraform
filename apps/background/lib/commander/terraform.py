# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import json
import traceback
from lib.logs import logger
from lib.command import command
from wecube_plugins_terraform.settings import TERRAFORM_BASE_PATH
from wecube_plugins_terraform.settings import TERRFORM_BIN_PATH

if not os.path.exists(TERRAFORM_BASE_PATH):
    os.makedirs(TERRAFORM_BASE_PATH)


class TerrformExecError(Exception):
    pass


class TerraformDriver(object):
    def __init__(self, terraform_path=None, workdir=None):
        self.terraform = terraform_path or TERRFORM_BIN_PATH
        self.workdir = workdir

    def init_provider_path(self, provider):
        provider_path = os.path.join(TERRAFORM_BASE_PATH, provider)
        if not os.path.exists(provider_path):
            os.makedirs(provider_path)

        return provider_path

    def upgrade(self, dir_path=None, version_file=None):
        workdir = dir_path or self.workdir or ''
        if version_file:
            if not os.path.exists(os.path.join(workdir, "versions.tf")):
                command("cp %s %s" % (version_file, workdir))

        exec_cmd = "cd %s; terraform 0.13upgrade -yes ." % (workdir)
        code, out, err = command(self._format_cmd(exec_cmd), workdir=workdir)
        if code == 0:
            pass
        else:
            pass

    def init(self, dir_path=None,
             backend=None, backend_config=None,
             plugin_dir=None, reconfigure=None, upgrade=None):
        '''

        :param dir_path:
        :param backend: 'true' or 'flase'
        :param backend_config:
        :param plugin_dir:
        :param reconfigure: None or ''
        :param upgrade: 'true' or 'false'
        :return:
        '''

        workdir = dir_path or self.workdir or ''

        input_options = {}
        input_options["backend"] = backend
        input_options["backend_config"] = backend_config
        input_options["reconfigure"] = reconfigure
        input_options["upgrade"] = upgrade

        args = self._generate_args(input_options)
        if plugin_dir:
            args += " -plugin-dir %s" % plugin_dir

        exec_cmd = "init %s %s" % (args, workdir)

        code, out, err = command(self._format_cmd(exec_cmd), workdir=workdir)
        if code == 0:
            return True
        else:
            raise TerrformExecError("init error, msg: %s" % err)

    def init_resource_dir(self, dir_path, provider):
        provider_path = self.init_provider_path(provider)
        if not os.path.exists(os.path.join(dir_path, "versions.tf")):
            if os.path.exists(os.path.join(provider_path, "versions.tf")):
                command("cp %s %s" % (os.path.join(provider_path, "versions.tf"), dir_path))
            else:
                logger.info("versions.tf file not exists")

        return self.init(dir_path=dir_path)

    def _format_cmd(self, cmd, args=None):
        if not args:
            return "%s %s" % (self.terraform, cmd)
        else:
            return "%s %s %s" % (self.terraform, cmd, args)

    def _generate_args(self, input_options):
        args_list = []
        for k, v in input_options.items():
            if v is not None:
                if "_" in k:
                    k = k.replace("_", "-")
                if isinstance(v, bool):
                    v = "true" if v else "false"

                if v:
                    args_list.append("-%s=%s" % (k, v))
                else:
                    args_list.append("-%s" % (k))

        return " ".join(args_list)

    def _generate_var_args(self, var_args):
        var_args = var_args or {}
        args = ""
        for i, x in var_args.items():
            args += " -var %s=%s" % (i, x)
        return args

    def apply(self, dir_or_plan=None, auto_approve=None,
              backup=None, refresh=None,
              state=None, state_out=None,
              lock=None, var=None, var_file=None):
        '''

        :param dir_path:
        :param auto_approve: -auto-approve  None or ""
        :param backup: path
        :param refresh: 'true' or 'false'
        :param state: path
        :param state_out: path 保留以前的state文件
        :param lock: 'true' or 'false'
        :param var: dict
        :param var_file: path
        :return:
        '''

        workdir = dir_or_plan or self.workdir or ''

        input_options = {}
        input_options["lock"] = lock
        input_options["backup"] = backup
        input_options["refresh"] = refresh
        input_options["state"] = state
        input_options["state_out"] = state_out
        input_options["var_file"] = var_file
        input_options["auto_approve"] = auto_approve
        args = self._generate_args(input_options)
        args += self._generate_var_args(var)
        exec_cmd = "apply %s %s" % (args, workdir)

        code, out, err = command(self._format_cmd(exec_cmd), workdir=workdir)
        if code == 0:
            return True
        else:
            raise TerrformExecError("apply error, msg: %s" % err)

    def refresh(self, path=None):
        '''

        :param path:
        :return:
        '''

        workdir = path or self.workdir or ''

        exec_cmd = "refresh  %s" % (path)

        code, out, err = command(self._format_cmd(exec_cmd), workdir=workdir)
        if code == 0:
            return True
        else:
            raise TerrformExecError("refresh error, msg: %s" % err)

    def plan(self, dir_path=None, compact_warnings=None,
             destroy=None, detailed_exitcode=None,
             out=None, refresh=None, state=None,
             lock=None, var=None, var_file=None):
        '''

        :param dir_path:
        :param compact_warnings: None or ""
        :param destroy:  plan destroy None or ""
        :param detailed_exitcode: None or ""
        :param out: path
        :param refresh: 'true' or 'false'
        :param state: path
        :param state_out: path 保留以前的state文件
        :param lock: 'true' or 'false'
        :param var: dict
        :param var_file: path

        :return:
        '''

        workdir = dir_path or self.workdir or ''

        input_options = {}
        input_options["lock"] = lock
        input_options["out"] = out
        input_options["compact_warnings"] = compact_warnings
        input_options["destroy"] = destroy
        input_options["detailed_exitcode"] = detailed_exitcode
        input_options["refresh"] = refresh
        input_options["state"] = state
        input_options["var_file"] = var_file
        args = self._generate_args(input_options)
        args += self._generate_var_args(var)
        exec_cmd = "plan %s %s" % (args, workdir)

        code, out, err = command(self._format_cmd(exec_cmd), workdir=workdir)
        if code in [0, 1, 2]:
            # failed
            pass
        else:
            raise TerrformExecError("plan error, msg: %s" % err)

    def read_result(self, state_path=None):
        if not state_path:
            workdir = self.workdir or ""
            state_path = os.path.join(workdir, "terraform.tfstate")

        if not os.path.exists(state_path):
            raise TerrformExecError("can not read state")

        try:
            with open(state_path, "rb+") as f:
                return json.load(f)
        except Exception, e:
            logger.info(traceback.format_exc())
            raise TerrformExecError("can not generate state file. msg: %s-%s" % (e.__class__.__name__,
                                                                                 e.message))

    def resource_result(self, path):
        path = path or self.workdir or ""
        state_path = os.path.join(path, "terraform.tfstate")
        return self.read_result(state_path)

    def destroy(self, dir_path=None,
                auto_approve=None, force=None,
                backup=None, refresh=None,
                state=None, state_out=None,
                lock=None, var=None, var_file=None):
        '''


        :param dir_path:
        :param force:  同auto_approve
        :param auto_approve: -auto-approve  None or ""
        :param backup: path
        :param refresh: 'true' or 'false'
        :param state: path
        :param state_out: path 保留以前的state文件
        :param lock: 'true' or 'false'
        :param var: dict
        :param var_file: path
        :return:
        '''

        workdir = dir_path or self.workdir or ''
        if not os.path.exists(workdir):
            raise TerrformExecError("resource workpath not exists, not permit delete")

        input_options = {}
        input_options["lock"] = lock
        input_options["backup"] = backup
        input_options["refresh"] = refresh
        input_options["state"] = state
        input_options["state_out"] = state_out
        input_options["var_file"] = var_file
        input_options["auto_approve"] = auto_approve
        input_options["force"] = force
        args = self._generate_args(input_options)
        args += self._generate_var_args(var)
        exec_cmd = "destroy %s %s" % (args, workdir)

        code, out, err = command(self._format_cmd(exec_cmd), workdir=workdir)
        if code == 0:
            return True
        else:
            raise TerrformExecError("destroy error, msg: %s" % err)

    def import_state(self, from_source, dest_source, dir_or_plan=None, state=None):
        '''

        :param dir_path:
        :param state: path
        :return:
        '''

        workdir = dir_or_plan or self.workdir or ''

        if state:
            exec_cmd = "import -state=%s %s %s" % (state, dest_source, from_source)
        else:
            exec_cmd = "import %s %s" % (dest_source, from_source)

        x_command = "cd %s; %s" % (workdir, self._format_cmd(exec_cmd))
        code, out, err = command(x_command, workdir=workdir)
        if code == 0:
            return True
        else:
            raise TerrformExecError("import error, msg: %s" % err)
