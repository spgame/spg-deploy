#!/usr/bin/python2
#coding=utf-8

'''
用于删除不再需要的资源文件。指定需要保留的配置文件，不被这些配置文件引用的资源文件将被删除。
'''

import zipfile
import json
import sys
import os

print('###########SPG静态资源清理程序###########')
print('################处理参数################')
print('参数是{argv}'.format(argv=sys.argv))

arg = None
argi = 0
def next_arg():
	global argi, arg
	argi = argi + 1
	if argi >= len(sys.argv):
		arg = None
		return False
	arg = sys.argv[argi]
	return True

TEMP_FOLD = '_RM_TEMP_'

#这个程序读取指定根目录下的文件列表，找出没有在配置文件中指明的那些文件

_base_fold = None
_config_files = []
_used_files = {}

while next_arg():
	if None == _base_fold:
		print('根目录 {arg}'.format(arg = arg))
		_base_fold = arg
	else:
		print('配置文件 {arg}'.format(arg = arg))
		_config_files.append(arg)

#os.chdir(_base_fold)

#if os.path.exists(TEMP_FOLD):
#	os.rmdir(TEMP_FOLD)
#	
#os.mkdir(TEMP_FOLD)

def get_config_json(config_name):
	zip_file = zipfile.ZipFile(_base_fold + '/' + config_name)
	try:
		data = zip_file.read('data.json')
		data = json.loads(data)
	except Exception as e:
		print('读取配置文件{config_name}时发生了异常：\n{e}'.format(config_name = config_name, e = e))
		return {}
	return data
	

for config_name in _config_files:
	data = get_config_json(config_name)
	for (k, v) in data.items():
		_used_files[v[0]] = config_name
		
print _used_files

for file_name in os.listdir(_base_fold):
	file_path = os.path.join(_base_fold, file_name) 
	if os.path.isfile(file_path):
		if _used_files.get(file_name) is None:
			print(file_name + '没有被使用')
		else:
			print (file_name + '使用中')
	  