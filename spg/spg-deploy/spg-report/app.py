#!/usr/bin/python
# -*- coding: UTF-8 -*-

from db import DB
from db_offline import DB_Offline
from a17api import A17API
from flask import Flask, redirect, request, g, url_for, render_template, send_file
import time
import _thread
import sys
import datetime
import redis
import demjson

from IPy import IP

#定义APP
app = Flask(__name__)
app.config.from_envvar('APP_CONFIG_FILE')

@app.template_filter('percent')
def precent(value):
    return str(value * 100)[:4]
    
@app.template_filter('ms2s')
def ms2s(value):
    return str(value / 1000)[:4]
    
@app.template_filter('icon')
def get_icon(TQA, CR, TPQ):
    value = (60 / 500) * TQA * .4 + \
        CR * 100 * .4 + \
        (100 / 15) * (15 - TPQ / 1000) * 0.2
    if value < 60: #不及格
        return 'icon-6'
    elif value < 70:
        return 'icon-5'
    elif value < 80:
        return 'icon-2'
    elif value < 90:
        return 'icon-4'
    else:
        return 'icon-3'
    
@app.template_filter('rank')
def rank(RANK, TQA):
    if TQA < 100:
        return '-'
    return '第{}名'.format(RANK)

#生成学习成绩html页面
@app.route('/')
def show():
    #计算来源IP
    remote_addr = request.remote_addr
    for route_ip in reversed(request.access_route + [request.remote_addr]):
        if 'PRIVATE' != IP(route_ip).iptype():
            remote_addr = route_ip
            break
    
    session_key = request.args.get('session_key')
    app.logger.debug('Session Key: {}'.format(session_key))
    
    if session_key is None:
        return render_template('error.html', reason='没有提供session_key')

    #问一起作业要玩家user_id
    a17_api = A17API(app.config['A17API_APP_KEY'], app.config['A17API_SECRET_KEY'], session_key)
    a17_result = a17_api.user_get()
    app.logger.debug('Ask from API: {}'.format(a17_result))
    
    user_id = user_grade = real_name = None
    if a17_result is not None:
        user_id = a17_result['user_id']
        real_name = a17_result['real_name']
        user_grade = a17_result['clazz_level']
    else:
        return render_template('error.html', reason='查找用户失败')
        
    print('用户{}从IP{}访问'.format(user_id, remote_addr))
        
    #获取目标日期
    today = datetime.date.today()
    from_day = today + datetime.timedelta(days = - today.weekday() - 7)
    to_day = today + datetime.timedelta(days = - today.weekday())
    
    #读数据库
    db = DB()
    data = db.query(user_id, from_day.strftime('%Y%m%d'))
    
    if data is None:
        # return render_template('error.html', reason='获取报告失败')
        return render_template('nodata.html', name = real_name, pay_link = app.config['PAY_LINK'])
    print('数据库返回：{}'.format(data))
    
    return render_template('index.html', data = data, name = real_name, \
        grade = user_grade, from_day = from_day.strftime('%Y/%m/%d'), \
        to_day = to_day.strftime('%Y/%m/%d'),\
        pay_link = app.config['PAY_LINK'])

#获取学生学习成绩json格式数据
@app.route('/qadetail')
def qadetail():
    #计算来源IP
    remote_addr = request.remote_addr
    for route_ip in reversed(request.access_route + [request.remote_addr]):
        if 'PRIVATE' != IP(route_ip).iptype():
            remote_addr = route_ip
            break
    
    session_key = request.args.get('session_key')
    limit =  request.args.get('limit')
    
    if session_key is None:
        return '{}'
        
    #问一起作业要玩家user_id
    a17_api = A17API(app.config['A17API_APP_KEY'], app.config['A17API_SECRET_KEY'], session_key)
    a17_result = a17_api.user_get()
    
    user_id = real_name = None
    if a17_result is not None:
        user_id = a17_result['user_id']
        real_name = a17_result['real_name']
    else:
        return '{}'
        
    print('qadetail::用户{}从IP{}访问'.format(user_id, remote_addr))
        
    #获取目标日期
    today = datetime.date.today()
    now = datetime.datetime.now()
    secs = now.hour*3600 + now.minute*60 + now.second
    expire_secs = 24*3600 - secs
    
    print ('过期需要秒{}'.format(now.hour))
    # 取词汇学习数据
    redis_instance = redis.StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=0, password=app.config['REDIS_PWD'])
    
    # 尝试从redis中获取数据
    qa_detail = redis_instance.get(user_id)
    
    # 如果redis内没有查找到数据,从数据库内查找
    if (qa_detail is None):
        db_off = DB_Offline()
        qa_detail = db_off.query_qa_detail_record(user_id, today)
        # 从数据库查询出结果后,转换为json字符串存储至redis
        redis_instance.set(user_id, demjson.encode(qa_detail))
        # redis_instance.expire(user_id, expire_secs)
        redis_instance.expire(user_id, 600)
        print ('使用数据库查询得到数据')
    else:
        qa_detail = redis_instance.get(user_id)
        qa_detail = demjson.decode(qa_detail)
        print ('命中缓存')
        
    if limit is None:
        limit = 200
    limit = min(int(limit), len(qa_detail.keys()))
    
    i = 0
    result = []
    for key in qa_detail:
        if (i < limit):
            result.append(qa_detail[key])
        else:
            break
        i += 1
        
    return demjson.encode(result)
    
#启动APP
if __name__ == '__main__':
    
    DB.HOST = app.config['DB_HOST']
    DB.PORT = app.config['DB_PORT']
    DB.USER = app.config['DB_USER']
    DB.PASSWD = app.config['DB_PASSWD']
    DB.DB_NAME = app.config['DB_NAME']
    
    DB_Offline.HOST = app.config['DB_OFFLINE_HOST']
    DB_Offline.PORT = app.config['DB_OFFLINE_PORT']
    DB_Offline.USER = app.config['DB_OFFLINE_USER']
    DB_Offline.PASSWD = app.config['DB_OFFLINE_PASSWD']
    DB_Offline.DB_NAME = app.config['DB_OFFLINE_NAME']

    A17API.SERVER_URL = app.config['A17API_SERVER_URL']
    app.run(host='0.0.0.0', port=8080)