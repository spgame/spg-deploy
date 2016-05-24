#!/usr/bin/python
# -*- coding: UTF-8 -*-

DEBUG = False

#指定数据库连接参数
DB_HOST = 'rdsw47401c9a58i39kd9public.mysql.rds.aliyuncs.com'
DB_PORT = 3306
DB_USER = 'loya_analyze'
DB_PASSWD = 'mazongnb'
DB_NAME = 'loya_online'

A17API_APP_KEY = 'A17ZYSPG'
A17API_SECRET_KEY = 'Fca4vpuD1bjR'
A17API_SERVER_URL = 'http://www.17zuoye.com/v1'

PAY_LINK = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx3c30705f9f1d82d1&redirect_uri=http%3a%2f%2fwechat.17zuoye.com%2fparent_auth.vpage&response_type=code&scope=snsapi_base&state=nt_product_spg#wechat_redirect'