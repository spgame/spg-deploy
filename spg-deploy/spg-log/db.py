#!/usr/bin/python
# -*- coding: UTF-8 -*-

# import MySQLdb
import pymysql.cursors
import sys
import datetime

class DB:
    TABLE_NAME = 'client_logs'
    
    HOST = PORT = USER = PASSWD = DB_NAME = None
    
    # INITED = False
    
    table_name_today = None
    
    def __init__(self):
        #分日期打开数据表。夜里一点之前的数据计入前一天。
        global table_name_today
        table_name_today = DB.TABLE_NAME + '_' + (datetime.datetime.now() + datetime.timedelta(hours = -1)).strftime('%Y_%m_%d')
        
        try:
            self.connection = pymysql.connect(charset='UTF8', host = DB.HOST, port = DB.PORT, user = DB.USER, passwd = DB.PASSWD, db = DB.DB_NAME)
            # if not DB.INITED:
            #     self.init_db()
            #     DB.INITED = True
            self.init_db()
        except Exception as e:
            print(e)
            
            
    def init_db(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('select `TABLE_NAME` from `INFORMATION_SCHEMA`.`TABLES` \
                where `TABLE_SCHEMA`= %s and `TABLE_NAME`= %s ', (DB.DB_NAME, table_name_today))
            if 1 != len(cursor.fetchall()):
                print('创建数据表' +  table_name_today)
                #表名不能用execute参数，必须编码在SQL语句中
                cursor.execute('create table ' + table_name_today + '''(
                    `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
                    `time` datetime NOT NULL,
                    `ip` varchar(16) NOT NULL,
                    `session_key` varchar(32),
                    `user_agent` varchar(128) NOT NULL,
                    `lv` varchar(16),
                    `user_id` bigint NULL,
                    `summary` text NULL,
                    `detail` text NULL,
                    PRIMARY KEY (`id`)
                    )''')
            return True
        except Exception as e:
            print(e)
            return False
            
    
    def insert_log(self, time, ip, session_key, user_agent, lv = None, user_id = None, summary = None, detail = None):
        sql = 'insert into ' + table_name_today + '''
            (time, ip, session_key, user_agent, lv, user_id, summary, detail)
            values
            (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (time, ip, session_key, user_agent, lv, user_id, summary, detail))
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def insert_many_log(self, param):
        sql = 'insert into ' + table_name_today + '''
            (time, ip, session_key, user_agent, lv, user_id, summary, detail)
            values
            (%s, %s, %s, %s, %s, %s, %s, %s)
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