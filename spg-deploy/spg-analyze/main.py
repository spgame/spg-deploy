#!/usr/bin/python
# -*- coding: UTF-8 -*-
#!python3

import json
import sys
import pymysql.cursors
import datetime

#这个程序用于分析日志。

#用于重试数据库操作的装饰器
def retry(times = 3):
    def decorator(func):
        def retry_fucn(*args, **kwargs):
            fail = 0
            error = None
            while(True):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    if fail < times:
                        print('发生第{0}次错误，重试\n{1}'.format(fail, e))
                        fail += 1
                    else:
                        print('错误次数超过限制{0}，放弃\n{1}'.format(fail, e))
                        raise e
                        
        return retry_fucn
    return decorator
            

DB_ONLINE = 'rdsw47401c9a58i39kd9public.mysql.rds.aliyuncs.com'
DB_OFFLINE = 'rds5z0evv19cpy4r33r1public.mysql.rds.aliyuncs.com'
DB_USER = 'loya_analyze'
DB_PASSWD = 'mazongnb'

#获取已经拥有角色的用户
@retry()
def get_role_info():
    connection = pymysql.connect(charset='UTF8', host = DB_ONLINE, port = 3306, user = DB_USER, passwd = DB_PASSWD, db = 'loya_online')
    cursor = connection.cursor()
    cursor.execute('select role_id, level, create_time from role')
    return cursor.fetchall()
    
def get_day_time(offset):
    today = datetime.date.today()
    deltadays = datetime.timedelta(days = 1)
    return today + offset * deltadays
    
def get_day_str(offset):
    return get_day_time(offset).strftime('%Y_%m_%d')
    
#读取玩家行为
@retry()
def get_action(action, offset, group_by_role_id = False):
    connection = pymysql.connect(charset='UTF8', host = DB_OFFLINE, port = 3306, user = DB_USER, passwd = DB_PASSWD, db = 'loya_offline')
    cursor = connection.cursor()
    if group_by_role_id:
        print('获取日期于 {} 的行为[{}]，并按role_id去重'.format(get_day_str(offset), action))
    else:
        print('获取日期于 {} 的行为[{}]'.format(get_day_str(offset), action))
    table_name = 'role_offline_log_' + get_day_str(offset)
    
    cursor.execute('select `TABLE_NAME` from `INFORMATION_SCHEMA`.`TABLES` \
        where `TABLE_SCHEMA`= %s and `TABLE_NAME`= %s ', ('loya_offline', table_name))
    if 1 != len(cursor.fetchall()):
        return None
    
    sql = 'select role_id from ' + table_name + ' where action_type = "' + action + '"'
    if group_by_role_id:
        sql += 'group by role_id'
    cursor.execute(sql)
    return cursor.fetchall()
    
login_cache = {};
#读取指定天数的登陆行为，并存入缓存
def get_login_by_day(day):
    if day not in login_cache:
        temp = get_action('登录', day, True)
        day_time = get_day_time(day)
        if temp is not None:
            temp2 = {}
            for role_id in temp:
                role_id = role_id[0]
                if role_map[role_id]['create_time'] < day_time:
                    temp2[role_id] = True
            login_cache[day] = temp2
        else:
            login_cache[day] = None
    return login_cache[day]
        
#获取指定天数偏移（单日/范围）的登入行为
def get_login(days):
    if isinstance(days, int):
        days = (days, days + 1)
    result = None
    for i in range(days[0], days[1]):
        if result is None:
            result = get_login_by_day(i)
        else:
            if get_login_by_day(i) is not None:
                for role_id in get_login_by_day(i):
                    result[role_id] = True
    return result

# 获取流失率。reg_days:账号注册的时间范围 login_days:账号登陆的时间范围
def get_role_retention(reg_days, login_days):
    login_map = get_login(login_days)
    if isinstance(reg_days, int):
        reg_days = (reg_days, reg_days + 1)
    total = 0
    retention = 0
    for i in range(reg_days[0], reg_days[1]):
        temp = get_action('创建角色', i)
        if temp is not None:
            for role_id in temp:
                total += 1
                role_id = role_id[0]
                if role_id in login_map:
                    retention += 1
    return retention, total
            
    


###################处理流程######################

print('读取角色列表……')
role_map = {}
role_result = get_role_info()

print('共有角色{}个。准备角色数据……'.format(len(role_result)))
for role in role_result:
    role_map[role[0]] = {'level':role[1], 'create_time':[2]}

print('读取玩家创建角色行为……')
create_role_result = get_action('创建角色', -1)
print('共有创建角色行为{}次。正在分析……'.format(len(create_role_result)))
create_role_map = {}
new_role_lv2_num = 0
for role_id in create_role_result:
    role_id = role_id[0]
    create_role_map[role_id] = True
    if role_map[role_id]['level'] > 1:
        new_role_lv2_num += 1
print('共有{}个用户建号后当天升级到2级以上'.format(new_role_lv2_num))

print('读取玩家登陆行为……')
login_result = get_action('登录', -1)
print('共有登陆行为{}次。正在分析……'.format(len(login_result)))
login_map = {}
user_login_times = 0 #有账号，登录次数
user_login_roles_num = 0 #有账号登陆账号数
churn_login_times = 0 #没账号登录次数
churn_login_roles_num = 0 #没账号登陆账号数

for role_id in login_result:
    role_id = role_id[0]
    if not role_id in login_map: #第一次检测到登陆
        login_map[role_id] = 1
        if role_id in role_map:
            user_login_roles_num += 1
        else:
            churn_login_roles_num += 1
    else:
        login_map[role_id] += 1
    
    if role_id in role_map:
        user_login_times += 1
    else:
        churn_login_times += 1
print('共有{}个用户登陆。'.format(user_login_roles_num + churn_login_roles_num))
print('有角色的登陆行为发生了{}次，来自{}个用户。'.format(user_login_times, user_login_roles_num))
print('没角色的登陆行为发生了{}次，来自{}个用户。'.format(churn_login_times, churn_login_roles_num))

print('读取玩家打开页面行为……')
index_result = get_action('打开首页', -1)
print('共有打开页面行为{}次。正在分析……'.format(len(index_result)))
index_map = {}
user_index_times = 0 #有账号，打开页面次数
user_index_roles_num = 0 #有账号打开页面账号数
churn_index_times = 0 #没账号打开页面次数
churn_index_roles_num = 0 #没账号打开页面账号数

for role_id in index_result:
    role_id = role_id[0]
    if not role_id in index_map: #第一次检测到登陆
        index_map[role_id] = 1
        if role_id in role_map:
            user_index_roles_num += 1
        else:
            churn_index_roles_num += 1
    else:
        index_map[role_id] += 1
    
    if role_id in role_map:
        user_index_times += 1
    else:
        churn_index_times += 1

print('共有{}个用户打开页面。'.format(user_index_roles_num + churn_index_roles_num))
print('有角色的打开页面行为发生了{}次，来自{}个用户。'.format(user_index_times, user_index_roles_num))
print('没角色的打开页面行为发生了{}次，来自{}个用户。'.format(churn_index_times, churn_index_roles_num))

retention, total = get_role_retention(-8, (-7, 0))
print('7日留存为{}/{} = {}'.format(retention, total, retention / total))