# coding: utf-8

import traceback

from lib.json_helper import format_json_dumps
from lib.logs import logger
from lib.mysql_client import Database


class _BaseManager(object):
    obj = None

    def create(self, data):
        '''

        :param data:
        :return:
        '''

        try:
            logger.info("try create data: %s" % (format_json_dumps(data)))
            obj = self.obj(data)
            Database().create(obj)
            return 1, obj.id
        except Exception, e:
            logger.info("%s create data error, insert: %s" % (str(self.obj), format_json_dumps(data)))
            logger.info(traceback.format_exc())
            raise e

    def list(self, filters=None, filter_string=None,
             params=None, pageAt=0, pageSize=20000, orderby=None):
        '''

        :param filters:
        :param filter_string:
        :param params:
        :param pageAt:
        :param pageSize:
        :param orderby:
        :return:
        '''
        pageAt = pageAt or 0
        pageSize = pageSize or 20000
        filters = filters or {}
        try:
            num, result = Database().query(self.obj,
                                           filters=filters,
                                           filter_string=filter_string,
                                           params=params,
                                           pageAt=pageAt,
                                           pageSize=pageSize,
                                           orderby=orderby)
            _tmp = []
            for data in result:
                _tmp.append(data.to_dict())
            return num, _tmp
        except:
            logger.info("%s list data error" % (str(self.obj)))
            logger.info(traceback.format_exc())
            return 0, []

    def get(self, filters=None, filter_string=None, params=None):
        try:
            filters = filters or {}
            result = Database().get(self.obj, filters=filters, filter_string=filter_string, params=params)
            return result.to_dict()
        except:
            logger.info("%s get data error" % (str(self.obj)))
            logger.info(traceback.format_exc())
            return {}

    def update(self, filters, data):
        try:
            ora_data = self.get(filters=filters)
            if not ora_data:
                return 0, {}

            Database().update(self.obj, filters=filters, update_data=data)
            ora_data.update(data)
            return 1, ora_data
        except Exception, e:
            logger.info("%s update data error, filter: %s, data: %s" % (str(self.obj),
                                                                        str(filters),
                                                                        format_json_dumps(data)))
            logger.info(traceback.format_exc())
            raise e

    def delete(self, filters):
        try:
            ora_data = self.get(filters=filters)
            if not ora_data:
                return 0

            Database().delete(self.obj, filters=filters)
            return 1
        except Exception, e:
            logger.info("%s delete data error" % (str(self.obj)))
            logger.info(traceback.format_exc())
            raise e

    def excute(self, sql, bind=None):
        '''

        :param sql:
        :return:
        '''

        return Database().excute(sql, bind)
