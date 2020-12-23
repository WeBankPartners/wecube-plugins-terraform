# coding : utf-8

import os
from lib.ConfigReader import Config

# ---------------------default setting --------------------
DEBUG = Config.getBool("DEFAULT", "debug", default=False)
PORT = Config.getInt("DEFAULT", "serverport", default=8999)

# ---------------------log setting --------------------
LOG_NAME = Config.get("LOG", "name", default="service.log")
LOG_LEVEL = Config.get("LOG", "level", default="INFO")
LOG_MAX_SIZE = Config.getInt("LOG", "max_size", default="200") * 1024 * 1024
LOG_BACKUP = Config.getInt("LOG", "backup_count", default=3)
LOG_MSG_MAX_LEN = Config.getInt("LOG", "msg_max_len", default=2048)

# ---------------------mysql setting --------------------
if DEBUG:
    MYSQL_SERVER = Config.get("DATABASE", "server")
    MYSQL_USERNAME = Config.get("DATABASE", "username")
    MYSQL_PASSWORD = Config.get("DATABASE", "password")
    MYSQL_DATABASE = Config.get("DATABASE", "database")
else:
    MYSQL_SERVER = os.environ.get("MYSQL_SERVER")
    MYSQL_USERNAME = os.environ.get("MYSQL_USERNAME")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")

USER_HOME = os.environ.get("USER_HOME", "/root")
JWT_KEY = os.environ.get("JWT_SIGNING_KEY", "secret")

