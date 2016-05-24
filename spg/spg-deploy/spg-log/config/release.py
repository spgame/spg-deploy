#!/usr/bin/python
# -*- coding: UTF-8 -*-

DEBUG = False

#指定数据库连接参数
DB_HOST = 'rds3wipl97sqdxu4v7wze.mysql.rds.aliyuncs.com'
DB_PORT = 3306
DB_USER = 'logger'
DB_PASSWD = 'mazongnb'
DB_NAME = 'flash_log'

#指定数据库写入CD
WRITE_CD = 60

#指定数据库写入失败重试CD
RETURY_CD = 18
#指定数据库写入失败重试次数
RETURY_TIMES = 10
