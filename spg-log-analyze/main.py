#!/usr/bin/python3
#coding=utf-8

import requests
import json
import pymysql.cursors
import datetime
import xlsxwriter
from slacker import Slacker
from ipip import IP

#指定数据库连接参数
DB_HOST = 'rds3wipl97sqdxu4v7wze.mysql.rds.aliyuncs.com'
DB_PORT = 3306
DB_USER = 'logger'
DB_PASSWD = 'mazongnb'
DB_NAME = 'flash_log'
TABLE_NAME = 'client_logs'
table_name_today = None
yesterday = datetime.datetime.now() + datetime.timedelta(days = -1)
table_name_today = TABLE_NAME + '_' + yesterday.strftime('%Y_%m_%d')

#指定slack参数
SLACK_TOCKEN = 'xoxb-19280290032-XfwE4Bfmx0N8vGpq4LqtDCmP'
SLACK_CHANNEL = '#spg'

#读数据库获取一些记录
def get_logs():
    connection = pymysql.connect(charset='UTF8', host = DB_HOST, port = DB_PORT, user = DB_USER, passwd = DB_PASSWD, db = DB_NAME)
    cursor = connection.cursor()
    sql = 'select * from ' + table_name_today + ' limit 0,9999999'
    cursor.execute(sql)
    return cursor.fetchall()

IP.load("17monipdb.dat")


print('从数据库{}读取log……'.format(table_name_today))

logs = get_logs()
print('共有{}条。'.format(len(logs)))

print('统计重复的log……')
#将相同session的记录聚合起来的数据结构
session_map = {}
#将error级别的summary聚合，统计出现次数
summary_map = {}
#逐条处理数据
for log in logs:
    ip = log[2]
    session_key = log[3]
    level = log[5]
    user_id = log[6]
    summary = log[7]
    detail = log[8]
    
    logs_per_session = session_map.get(session_key)
    if logs_per_session is None:
        session_map[session_key] = logs_per_session = {}
        logs_per_session['ip'] = ip
        logs_per_session['city'] = IP.find(ip)
        # print('ip {} -> {}'.format(ip,logs_per_session['city']))
        logs_per_session['user_id'] = user_id
        logs_per_session['summary_map'] = {}
    
    detail_info = logs_per_session['summary_map'].get(summary)
    if detail_info is None:
        logs_per_session['summary_map'][summary] = detail_info = {}
        detail_info['count'] = 0
        detail_info['detail'] = detail
        detail_info['level'] = level
    detail_info['count'] += 1
    
    summary_info = summary_map.get(summary)
    if summary_info is None:
        summary_map[summary] = summary_info = {}
        summary_info['count'] = 0
        summary_info['level'] = level
    summary_info['count'] += 1
    



print('写入数据报告……')

workbook = xlsxwriter.Workbook('data.xlsx')
bold = workbook.add_format({'bold': 1})

print('写入log去重表……')
sheet = workbook.add_worksheet('log去重表')
sheet.write_row('A1', ['user_id / session_key', '事件等级', '摘要', 'ip', '发生次数', '地域'], bold)
row = 0
for (session_key, logs_per_session) in session_map.items():
    for (summary, detail_info) in logs_per_session['summary_map'].items():
        # print('写入{} {} {}'.format(session_key, summary, detail_info))
        row += 1
        id_or_session = str(logs_per_session['user_id'])
        
        if '0' == id_or_session:
            id_or_session = session_key
        
        sheet.write_row(row, 0, [id_or_session, detail_info['level'], summary, logs_per_session['ip'], detail_info['count'], logs_per_session['city']])

print('写入了{}条记录。'.format(row))

print('写入摘要排序表……')
sheet = workbook.add_worksheet('摘要排序表')
sheet.write_row('A1', ['事件等级', '摘要', '发生次数'], bold)
summary_info_list = sorted(summary_map.items(), key = lambda x: x[1]['count'], reverse = True)
row = 0
for (summary, summary_info) in summary_info_list:
    row += 1
    sheet.write_row(row, 0, [summary_info['level'], summary, summary_info['count']])

print('写入了{}条记录。'.format(row))


workbook.close()

print('上传到slack')

slack = Slacker(SLACK_TOCKEN)
slack.files.upload('data.xlsx', title = '{}客户端日志分析报告'.format(yesterday.strftime('%Y_%m_%d')), \
                    initial_comment = '总计{}条log记录'.format(len(logs)), \
                    filename = 'client_logs_analyze_{}.xlsx'.format(yesterday.strftime('%Y_%m_%d')), channels = SLACK_CHANNEL)

