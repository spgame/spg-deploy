#!/usr/bin/python
# -*- coding: UTF-8 -*-

# import MySQLdb
import pymysql.cursors
import sys
import datetime

class DB:
    TABLE_NAME = 'weekly_learn_rank'
    
    HOST = PORT = USER = PASSWD = DB_NAME = None
    
    def __init__(self):
        try:
            self.connection = pymysql.connect(charset='UTF8', host = DB.HOST, port = DB.PORT, user = DB.USER, passwd = DB.PASSWD, db = DB.DB_NAME)
        except Exception as e:
            print(e)
            
    
    def query(self, user_id, cycle_day):
        sql = 'select * from weekly_learn_rank where CYCLE = %s and ROLE_ID = %s'
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (cycle_day, user_id))
            result = cursor.fetchall()
            print('从数据库读出：{}'.format(result))
            if 1 != len(result):
                return None
            fields = map(lambda x:x[0], cursor.description)
            result = dict(zip(fields,result[0]))
            return result
        except Exception as e:
            print('访问数据库出错：{}'.format(e))
            return None