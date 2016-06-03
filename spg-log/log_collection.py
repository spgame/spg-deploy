#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import _thread
from db import DB

class LogCollection:
    
    RETURY_CD = 5
    RETURY_TIMES = 3
    
    def __init__(self):
        self.time = time.time()
        self.logs = []
        
    def append_log(self, remote_addr, user_agent, lv, session_key, user_id, summary, detail):
        self.logs.append([time.strftime('%Y-%m-%d %H:%M:%S'), remote_addr, user_agent, lv, session_key, user_id, summary, detail])
            
        return len(self.logs)
    
    def __save(self):
        
        count = 0
        while True:
            db = DB()
            if db.insert_many_log(self.logs):
                print('写数据库完成')
                return
            
            if count > LogCollection.RETURY_TIMES:
                print('写数据库错误超过失败次数。丢弃未存储的{}条记录'.format(len(self.logs)))
                return
            
            print('写数据库时发生错误，{}秒后重试'.format(LogCollection.RETURY_CD))
            count += 1
            time.sleep(LogCollection.RETURY_CD)
    
    def save(self):
        if 0 == len(self.logs):
            return
        _thread.start_new_thread(self.__save, ())
        print('子线程启用')
        
    def __len__(self):
        return len(self.logs)