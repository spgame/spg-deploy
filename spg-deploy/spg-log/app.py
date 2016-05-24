#!/usr/bin/python
# -*- coding: UTF-8 -*-

from db import DB
from log_collection import LogCollection
from flask import Flask, redirect, request, g, url_for, render_template, send_file
import time
import _thread
import sys
from IPy import IP
    
#定义APP
app = Flask(__name__)
app.config.from_envvar('APP_CONFIG_FILE')
logCollection = LogCollection()

def send_logs():
    global logCollection
    while True:
        time.sleep(app.config['WRITE_CD'])
        temp = logCollection
        
        if len(temp) > 0:
            print('批量存储Log')
            logCollection = LogCollection()
            temp.save()

@app.route('/crossdomain.xml')
def crossdomain():
    return send_file('static/crossdomain.xml')
    # return render_template('crossdomain.xml')
    # return redirect(url_for('static', filename='crossdomain.xml'), code=301)


#定义使用了APP修饰符的方法
@app.route('/', methods=['get', 'post'])
def log():
    user_agent = request.user_agent.string
    # route = request.access_route + [request.remote_addr]
    # trusted_proxies = {'127.0.0.1'}
    # remote_addr = next((addr for addr in reversed(route) 
    #     if addr not in trusted_proxies), request.remote_addr)
    remote_addr = request.remote_addr
    for route_ip in reversed(request.access_route + [request.remote_addr]):
        if 'PRIVATE' != IP(route_ip).iptype():
            remote_addr = route_ip
            break
    
    print ('请求参数', request.args, request.form)
    session_key = request.args.get('session_key') or request.form.get('session_key')
    user_id = request.args.get('user_id') or request.form.get('user_id') or 0
    lv = request.args.get('level') or request.form.get('level')
    #原有的data现在分为summary和detail：信息的可归类部分传入summary，其他传入detail。
    #如果用户不做区分，可将summary视为data。
    data = request.args.get('data') or request.form.get('data') or request.data
    summary = data or request.args.get('summary') or request.form.get('summary')
    detail = request.args.get('detail') or request.form.get('detail')
    
    app.logger.debug('IP: {0}\nUA: {1}\nsession_key: {2}\nlevel: {3}\nuser_id: {4}\nDATA: {5}'
        .format(remote_addr, user_agent, session_key, lv, user_id, summary, detail))
    
    # db = DB()
    # db.insert_log(time.strftime('%Y-%m-%d %H:%M:%S'), remote_addr, session_key, user_agent, user_id, data)
    
    
    logCollection.append_log(remote_addr, session_key, user_agent, lv, user_id, summary, detail)
    
    return 'OK'
    

#启动APP
if __name__ == '__main__':
    DB.HOST = app.config['DB_HOST']
    DB.PORT = app.config['DB_PORT']
    DB.USER = app.config['DB_USER']
    DB.PASSWD = app.config['DB_PASSWD']
    DB.DB_NAME = app.config['DB_NAME']
    LogCollection.RETURY_CD = app.config['RETURY_CD']
    LogCollection.RETURY_TIMES = app.config['RETURY_TIMES']
    
    count = 0
    while not DB().init_db():
        if count > LogCollection.RETURY_TIMES:
            print('写数据库错误超过失败次数。程序启动失败')
            sys.exit(1)
        print('写数据库时发生错误，{}秒后重试'.format(LogCollection.RETURY_CD))
        count += 1
        time.sleep(app.config['RETURY_CD'])
    
    #debug Mode 下主程序会被运行两次。关掉debug模式即正常。
    _thread.start_new_thread(send_logs, ())
    
    
    
    app.run(host='0.0.0.0', port=8080)
    