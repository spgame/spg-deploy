#!/usr/bin/python
# -*- coding: UTF-8 -*-

# import MySQLdb
import pymysql.cursors
import sys
import datetime

class DB_Offline:
    
    HOST = PORT = USER = PASSWD = DB_NAME = None
    
    def __init__(self):
        try:
            self.connection = pymysql.connect(charset='UTF8', host = DB_Offline.HOST, port = DB_Offline.PORT, \
                user = DB_Offline.USER, passwd = DB_Offline.PASSWD, db = DB_Offline.DB_NAME)
        except Exception as e:
            print(e)
            
    def query_qa_detail_record(self, user_id, today):
        #昨天,前天,大前天
        day1 = today + datetime.timedelta(days = -1)
        day2 = today + datetime.timedelta(days = -2)
        day3 = today + datetime.timedelta(days = -3)
        
        sql = 'select en_text,cn_text,wac,wcc from qa_detail_record_' + day1.strftime('%Y_%m_%d') + ' where role_id=' + str(user_id) \
            + ' union all' \
            + ' select en_text,cn_text,wac,wcc from qa_detail_record_' + day2.strftime('%Y_%m_%d') + ' where role_id=' + str(user_id) \
            + ' union all' \
            + ' select en_text,cn_text,wac,wcc from qa_detail_record_' + day3.strftime('%Y_%m_%d') + ' where role_id=' + str(user_id)

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            
            dict = {}
            for record in result:
                en_text = record[0];
                # 整合数据
                if (dict.get(en_text) is None):
                    dict[en_text] = {'en_text':record[0], 'cn_text':record[1], 'wac':record[2], 'wcc':record[3]}
                else:
                    dict[en_text]['wac'] += record[2]
                    dict[en_text]['wcc'] += record[3]
    
            # i = 0;
            # for record in dict:
            #     print('{}:{} -> {}'.format(i, record, dict[record]))
            #     i += 1
            
            return dict
        except Exception as e:
            print('从数据库读取单词记录出错：{}'.format(e))
            return None