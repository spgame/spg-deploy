#!/usr/bin/python2
#coding=utf-8

'''
用于将版本上传到up云。
sync_to_upyun 本地目录 配置文件 [配置文件] [配置文件]
    --upload 空间名 操作员用户名 操作员密码
        将版本上传到up云
    --remote_path
        指定云空间目录
    --timeout 超时秒数
        指定上传时的超时秒数
    --endpoint 上传节点
        指定上传节点
    --clear_local
        清理本地。注意，清理操作只会清理根目录，不会清理子文件夹
    --clear_remote
        清理up云。注意，清理操作只会清理根目录，不会清理子文件夹
'''

import zipfile
import json
import sys
import os
import upyun

print('###########SPG静态资源上传程序###########')
print('################处理参数#################')
print('参数是{argv}'.format(argv=sys.argv))

arg = None
argi = 0
def next_arg():
    global argi, arg
    argi = argi + 1
    if argi >= len(sys.argv):
        arg = None
        return None
    arg = sys.argv[argi]
    return arg

TEMP_FOLD = '_RM_TEMP_'

config_files = []
local_path = bucket = user = passwd = None 
remote_path = '/'
absolute_path = clear_local = clear_remote = False
timeout = 30
endpoint = upyun.ED_AUTO


while next_arg() is not None:
    if '--upload' == arg:
        bucket = next_arg()
        user = next_arg()
        passwd = next_arg()
        print('上传到云空间：{}，用户：{}'.format(bucket, user))
    elif '--remote_path' == arg:
        remote_path = next_arg()
        if remote_path[-1:] != '/':
            remote_path = remote_path + '/'
        print('云空间目录：{}'.format(remote_path))
    elif '--timeout' == arg:
        timeout = next_arg()
        print('超时秒数：{}'.format(timeout))
    elif '--endpoint' == arg:
        endpoint = next_arg()
        print('上传节点：{}'.format(endpoint))
    elif '--absolute_path' == arg:
        absolute_path = True
        print('指定的配置文件路径是绝对路径')
    elif '--clear_local' == arg:
        clear_local = True
        print('指定了清除不需要的本地文件')
    elif '--clear_remote' == arg:
        clear_remote = True
        print('指定了清除不需要的远程文件')
    elif None == local_path:
        local_path = arg
        print('本地目录 {arg}'.format(arg = arg))
    else:
        config_files.append(arg)
        print('配置文件 {arg}'.format(arg = arg))

if local_path is None:
    print('未指定本地目录！')
    sys.exit(1)
if len(config_files) == 0:
    print('未指定配置文件！')
    sys.exit(1)

used_files = {}
files_size = 0
files_count = 0


print('##############读取配置文件###############')

if absolute_path:
    for i in range(len(config_files)):
        config_files[i] = os.path.relpath(config_files[i], local_path)
        print('转换为相对路径：{}'.format(config_files[i]))

def get_config_json(config_name):
    print('读取配置文件{}'.format(config_name))
    zip_file = zipfile.ZipFile(local_path + '/' + config_name)
    try:
        data = zip_file.read('data.json')
        data = json.loads(data)
    except Exception as e:
        print('读取配置文件{config_name}时发生了异常：\n{e}'.format(config_name = config_name, e = e))
        return {}
    return data
    

for config_name in config_files:
    data = get_config_json(config_name)
    for (k, v) in data.items():
        file_name = v[0]
        files_size += int(v[1])
        files_count += 1
        reference = used_files.get(file_name)
        if reference is None:
            reference = []
            used_files[file_name] = reference
        reference.append(config_name)

def format_size(size):
    ret = str(size % 1024)
    size = size // 1024
    if size == 0:
        return ret
    ret = str(size % 1024) + 'K' + ret
    size = size // 1024
    if size == 0:
        return ret
    ret = str(size % 1024) + 'M' + ret
    size = size // 1024
    if size == 0:
        return ret
    ret = str(size % 1024) + 'G' + ret
    return ret

print('文件总尺寸：{}，总个数：{}'.format(format_size(files_size), files_count))


print('##############检查必须文件###############')
for (k, v) in used_files.items():
    file_path = os.path.join(local_path, k) 
    if not os.path.isfile(file_path):
        print('必须的文件缺失：{}被配置文件{}引用'.format(k, v))
        sys.exit(1)
print('所有被引用的文件都存在')

if clear_local:
    print('##############检查多余文件###############')
    for file_name in os.listdir(local_path):
        file_path = os.path.join(local_path, file_name) 
        if os.path.isfile(file_path):
            if used_files.get(file_name) is None:
                os.remove(file_path)
                print('删除了没有使用的文件：{}'.format(file_name))



if bucket is None:
    print('###############任务已完成################')
    exit()
    
print('###############进行云同步################')
up = upyun.UpYun(bucket, user, passwd, timeout=timeout, endpoint=endpoint)

print('#############获取云文件列表##############')

print('检查远程目录：{}'.format(remote_path))
flag = False
for i in range(3):
    try:
        up.mkdir(remote_path)
        remote_list = up.getlist(remote_path)
        flag = True
        break
    except upyun.UpYunServiceException as se:
        print 'Except an UpYunServiceException ...'
        print 'Request Id: ' + se.request_id
        print 'HTTP Status Code: ' + str(se.status)
        print 'Error Message:    ' + se.msg + '\n'
    except upyun.UpYunClientException as ce:
        print 'Except an UpYunClientException ...'
        print 'Error Message: ' + ce.msg + '\n'
if not flag:
    print('网络操作失败')
    sys.exit(1)

remote_files = {}
for item in remote_list:
    if item['type'] == 'N':
        remote_files[item['name']] = True

config_fold = os.path.dirname(config_files[0])
print('检查远程目录：{}'.format(remote_path + config_fold + '/'))
flag = False
for i in range(3):
    try:
        up.mkdir(remote_path + config_fold + '/')
        remote_config_list = up.getlist(remote_path + config_fold + '/')
        flag = True
        break
    except upyun.UpYunServiceException as se:
        print 'Except an UpYunServiceException ...'
        print 'Request Id: ' + se.request_id
        print 'HTTP Status Code: ' + str(se.status)
        print 'Error Message:    ' + se.msg + '\n'
    except upyun.UpYunClientException as ce:
        print 'Except an UpYunClientException ...'
        print 'Error Message: ' + ce.msg + '\n'
if not flag:
    print('网络操作失败')
    sys.exit(1)

remote_config_files = {}
for item in remote_config_list:
    if item['type'] == 'N':
        remote_config_files[config_fold + '/' + item['name']] = True


print('################上传文件#################')
upload_size = 0
upload_count = 0

def upload(file_name, exit_if_error = True):
    global upload_size, upload_count
    print('上传：{}'.format(file_name))
    upload_size += os.path.getsize(os.path.join(local_path, file_name))
    upload_count += 1
    for i in range(3):
        try:
            with open(os.path.join(local_path, file_name), 'rb') as f:
                up.put(remote_path + file_name, f, checksum=True)
            return
        except upyun.UpYunServiceException as se:
            print 'Except an UpYunServiceException ...'
            print 'Request Id: ' + se.request_id
            print 'HTTP Status Code: ' + str(se.status)
            print 'Error Message:    ' + se.msg + '\n'
        except upyun.UpYunClientException as ce:
            print 'Except an UpYunClientException ...'
            print 'Error Message: ' + ce.msg + '\n'
    print('网络操作失败')
    sys.exit(1)

for i in range(len(config_files)):
    if remote_config_files.get(config_files[i]) is None:
        upload(config_files[i])
    else:
        pass
        # print('远程文件已存在：{}'.format(config_files[i]))

for (k, v) in used_files.items():
    if remote_files.get(k) is None:
        upload(k)
    else:
        pass
        # print('远程文件已存在：{}'.format(k))

print('上传总尺寸：{}，总个数：{}'.format(format_size(upload_size), upload_count))

def delete_remote(file_name):
    print('删除远程文件：{}'.format(file_name))
    
    for i in range(3):
        try:
            up.delete(remote_path + file_name)
            return
        except upyun.UpYunServiceException as se:
            print 'Except an UpYunServiceException ...'
            print 'Request Id: ' + se.request_id
            print 'HTTP Status Code: ' + str(se.status)
            print 'Error Message:    ' + se.msg + '\n'
        except upyun.UpYunClientException as ce:
            print 'Except an UpYunClientException ...'
            print 'Error Message: ' + ce.msg + '\n'
    print('网络操作失败')
    sys.exit(1)
    
if clear_remote:
    print('##############检查多余文件###############')
    for (k, v) in remote_files.items():
        if used_files.get(k) is None:
            delete_remote(k)
            

print('###############任务已完成################')