# _*_ coding:utf-8 _*_
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import configparser
from wecube_plugins_terraform.settings import BASE_DIR


class ConfigReader(object):
    def __init__(self, configPath=None):
        self.__configPath__ = configPath or os.path.join(BASE_DIR, "conf/application.conf")
        self.__defaultConfig__ = configparser.ConfigParser(allow_no_value=True)

        self.__default__ = None

        if self.__check_file(self.__configPath__):
            self.__default__ = True
            self.__defaultConfig__.read(self.__configPath__, encoding="UTF-8")
        else:
            raise ValueError("配置文件 %s 不存在" % os.path.basename(self.__configPath__))

    def __check_file(self, path):
        return os.path.exists(path)

    def get(self, section, option, default=None):
        '''
        获取配置文件参数
        :param section:
        :param option:
        :param default: 默认值，当未设置配置参数时， 返回默认值
        :return:
        '''
        _data = None
        if self.__default__:
            try:
                _data = self.__defaultConfig__.get(section=section, option=option)
            except (configparser.NoOptionError, configparser.NoOptionError) as e:
                pass

        if not _data and default is not None:
            _data = default

        if _data is None:
            raise ValueError("[section]: %s [option]: %s  未配置" % (section, option))
        return _data

    def getInt(self, section, option, default=None):
        _data = self.get(section, option, default)
        return int(_data) if _data else 0

    def getFloat(self, section, option, default=None):
        _data = self.get(section, option, default)
        return float(_data) if _data else 0.00

    def getBool(self, section, option, default=False):
        _data = self.get(section, option, default)
        if _data == 'true' or _data == 'True' or _data is True:
            return True
        elif _data == 'false' or _data == 'False' or _data is False:
            return False
        else:
            raise ValueError("[section]: %s [option]: %s  配置错误  -  %s" % (section, option, _data))

    def getList(self, section, option, default=None, splitwith=None):
        _data = self.get(section, option, default)
        if _data and isinstance(_data, str):
            splitwith = splitwith or ","
            _data = _data.split(splitwith)

        return _data


Config = ConfigReader()


if __name__ == '__main__':
    conf = ConfigReader()
    print(conf.get("DEFAULT", "test1", "ok"))
