#!/usr/bin/python
# -*- coding: UTF-8 -*-

# import MySQLdb
import pymysql.cursors
import sys

class DB:
    TABLE_NAME = 'client_logs'
    
    INITED = False
    
    def __init__(self, host, port, user, passwd, db):
        self.db = db
        try:
            self.connection = pymysql.connect(charset='UTF8', host = host, port = port, user = user, passwd = passwd, db = db)
        except Exception as e:
            print(e)
    
    def insert_log(self, time, ip, session_key, user_agent, lv = None, user_id = None, data = None):
        sql = 'insert into ' + DB.TABLE_NAME + '''
            (time, ip, session_key, user_agent, lv, user_id, data)
            values
            (%s, %s, %s, %s, %s, %s, %s)
            '''
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (time, ip, session_key, user_agent, lv, user_id, data))
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def insert_many_log(self, param):
        sql = 'insert into ' + DB.TABLE_NAME + '''
            (time, ip, session_key, user_agent, lv, user_id, data)
            values
            (%s, %s, %s, %s, %s, %s, %s)
            '''
        count = len(param)
        
        cursor = self.connection.cursor()
        cursor.executemany(sql, param)
        self.connection.commit()
        print('存储了{}条记录'.format(count))
        return True
        
        try:
            pass
        except Exception as e:
            print(e)
            return False