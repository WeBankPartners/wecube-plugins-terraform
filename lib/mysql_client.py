# coding:utf-8

import traceback
from lib.logs import logger
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from wecube_plugins_terraform.settings import MYSQL_SERVER
from wecube_plugins_terraform.settings import MYSQL_USERNAME
from wecube_plugins_terraform.settings import MYSQL_PASSWORD
from wecube_plugins_terraform.settings import MYSQL_DATABASE

Base = declarative_base()

_Session = sessionmaker(bind=create_engine("mysql+pymysql://%(user)s:%(password)s@%(service)s/%(database)s"
                                           % ({"user": MYSQL_USERNAME,
                                               "password": MYSQL_PASSWORD,
                                               "service": MYSQL_SERVER,
                                               "database": MYSQL_DATABASE}),
                                           # echo=True,
                                           pool_size=20,
                                           pool_recycle=60 * 9
                                           ),
                        autocommit=True
                        )

session = _Session()


class Database(object):
    def create(self, obj):
        '''

        :param obj:
        :return:
        '''

        try:
            session.begin()
            session.add(obj)
            session.commit()
        except Exception, e:
            logger.info(traceback.format_exc())
            session.rollback()
            raise e

    def query(self, obj, filters=None, filter_string=None, params=None,
              pageAt=0, pageSize=20000, orderby=None, **kwargs):
        '''

        :param obj:
        :param filters:
        :param filter_string: 需要与params一起使用
        :param pageAt:
        :param pageSize:
        :param orderby:
        :param kwargs:
        :return:
        '''

        filters = filters or {}

        _query_sql = session.query(obj).filter_by(**filters)

        if filter_string:
            _query_sql = _query_sql.filter(text(filter_string)).params(**params)

        count = _query_sql.count()

        if pageAt:
            _query_sql = _query_sql.offset(pageAt * pageSize)

        if orderby:
            if orderby[1] == "desc":
                _query_sql = _query_sql.order_by(desc(orderby[0]))
            else:
                _query_sql = _query_sql.order_by(orderby[0])

        return count, _query_sql.limit(pageSize).all()

    def get(self, obj, filters, filter_string=None, params=None):
        '''

        :param obj:
        :param fileters:
        :return:
        '''
        filters = filters or {}
        _query_sql = session.query(obj).filter_by(**filters)
        if filter_string:
            _query_sql = _query_sql.filter(filter_string).params(**params)

        return _query_sql.first()

    def delete(self, obj, filters):
        '''

        :param obj:
        :param filters:
        :return:
        '''
        if not filters:
            raise ValueError("delete filter not permit null")

        session.begin()
        try:
            session.query(obj).filter_by(**filters).delete()
            session.commit()
        except Exception, e:
            logger.info(traceback.format_exc())
            session.rollback()
            raise e

    def update(self, obj, filters, update_data):
        '''

        :param obj:
        :param filters:
        :param update_data:
        :return:
        '''
        if not filters:
            raise ValueError("update filter not permit null")

        try:
            session.begin()
            session.query(obj).filter_by(**filters).update(update_data)
            session.commit()
        except Exception, e:
            logger.info(traceback.format_exc())
            session.rollback()
            raise e

    def excute(self, sql, bind=None):
        '''

        :param sql:
        :return:
        '''

        ret = session.execute(sql, bind=bind)
        return ret.fetchall()
