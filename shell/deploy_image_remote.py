#!/usr/bin/python2
#coding=utf-8

# Install the Python Requests library:
# `pip install requests`

import requests
import json
import sys
import time

API_KEY = "463ba78e87df793fdfcf00a6acd942decbb75e44"
SERVER_URL = "http://spgmaster.just4test.net:1016/"

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

TAG_KEY = TAG_VALUE = API_CONTENT = REGISTRY_NAME = CONTAINER_NAME = IMAGE_NAME = None
CONTAINER_COUNT = 1
REMOVE_CURRENT = NEED_PULL = DEBUG_MODE = False
ENVS = []

while next_arg():
	if '--image' == arg:
		next_arg()
		print('镜像名 {arg}'.format(arg = arg))
		IMAGE_NAME = arg
	elif '--pull' == arg:
		print('指定了在使用镜像前先进行更新')
		NEED_PULL = True
	elif '--registry' == arg:
		next_arg()
		print('仓库名 {arg}'.format(arg = arg))
		REGISTRY_NAME = arg
	elif '--name' == arg:
		next_arg()
		print('容器名 {arg}'.format(arg = arg))
		CONTAINER_NAME = arg
	elif '--remove_current' == arg:
		print('尝试移除同名容器。必须同时指定容器名')
		REMOVE_CURRENT = True
	elif '--count' == arg:
		next_arg()
		print('每主机数量 {arg}'.format(arg = arg))
		CONTAINER_COUNT = arg
	elif '--env' == arg:
		next_arg()
		print('追加环境变量 {arg}'.format(arg = arg))
		ENVS.append(arg)
	elif '--debug' == arg:
		print('调试模式')
		DEBUG_MODE = True
	elif None == TAG_KEY:
		print('标签key {arg}'.format(arg = arg))
		TAG_KEY = arg
	elif None == TAG_VALUE:
		print('标签value {arg}'.format(arg = arg))
		TAG_VALUE = arg
	elif None == API_CONTENT:
		print('API文件 {arg}'.format(arg = arg))
		API_CONTENT = open(arg).read()
		print(API_CONTENT)
	else:
		print('无法理解的参数 {arg}'.format(arg = arg))
		sys.exit(1)


#显示http返回值
def show_http(responseOrError, statusCode = [200]):
	if(isinstance(responseOrError, requests.exceptions.RequestException)):
		print('请求失败: {error}'.format(error = responseOrError))
	elif DEBUG_MODE or 200 != responseOrError.status_code:
		print('状态码: {status_code}'.format(status_code=responseOrError.status_code))
		print('响应体: {content}'.format(content=responseOrError.content))

JOB_MAP = {}
#检查异步任务状态
def check_job(jobId):

	global JOB_MAP
	if not JOB_MAP.has_key(jobId):
		JOB_MAP[jobId] = []
		print('################检查任务################')

	def check_one_time():
		#如果结果未决，返回 -1
		#如果成功，返回 0
		#如果失败，返回 1
		action = None
		try:
			response = requests.get(
				url = SERVER_URL + "api/jobs/" + jobId,
				headers = {
					"Csphere-Api-Key":API_KEY,
				},
			)
			show_http(response)
		except requests.exceptions.RequestException as e:
			show_http(e)
			return 1

		def cmp_job(a,b):
			time_cmp = cmp(a['time'], b['time'])
			if 0 != time_cmp:
				return time_cmp
			if a.has_key('finished'):
				return 1
			else:
				return -1

		if 200 == response.status_code:
			arr = json.loads(response.content)
			arr.sort(cmp = cmp_job)
			resultCode = 0
			while(len(arr) > len(JOB_MAP[jobId])):
				obj = arr[len(JOB_MAP[jobId])]
				#处理创建容器流程
				if 'create_containers' == obj['action']:
					if None == action:
						print('{time}	创建容器'.format(time = obj['time']))
						action = obj['action']
					if obj.has_key('status'):
						print('{time}	=>节点 {node} 正在执行 {status}'.format(time = obj['time'], node = obj['node_id'], status = obj['status']))
					elif obj.has_key('cid'):
						print('{time}	=>节点 {node} 容器创建成功 {cid}'.format(time = obj['time'], node = obj['node_id'], cid = obj['cid']))
						if obj.has_key('errmsg'):
							print('{time}	=>启动失败 {errmsg}'.format(time = obj['time'], errmsg = obj['errmsg']))
							resultCode = 1
					elif obj.has_key('errmsg'):
						print('{time}	=>节点 {node} 失败 {errmsg}'.format(time = obj['time'], node = obj['node_id'], errmsg = obj['errmsg']))
						resultCode = 1
					elif obj.has_key('finished'):
						print('{time}	=>完成'.format(time = obj['time']))
						return resultCode
					else:
						print('遇到无法解析的对象 {obj}'.format(obj = obj))
						return 1
				#处理停止容器流程
				elif 'stop_container' == obj['action']:
					if None == action:
						print('{time}	停止容器'.format(time = obj['time']))
						action = obj['action']
					if obj.has_key('finished'):
						print('{time}	=>完成'.format(time = obj['time']))
						return resultCode
					else:
						print('遇到无法解析的对象 {obj}'.format(obj = obj))
						return 1
				#处理停止容器流程
				elif 'pull_image' == obj['action']:
					if None == action:
						print('{time}	拉镜像'.format(time = obj['time']))
						action = obj['action']
					if obj.has_key('finished'):
						print('{time}	=>完成'.format(time = obj['time']))
						return resultCode
					elif obj.has_key('node_id'):
						print('{time}	=>节点 {node} 正在拉镜像……'.format(time = obj['time'], node = obj['node_id']))
					else:
						print('遇到无法解析的对象 {obj}'.format(obj = obj))
						return 1

				JOB_MAP[jobId].append(obj)

			return -1
		return 1
	result = -1
	while(-1 == result):
		result = check_one_time()
		time.sleep(1)
	return result


#获取指定名字的仓库的id
def get_registry_id(name):
	print('################查找仓库################')
	try:
		response = requests.get(
			url = SERVER_URL + "api/registry",
			headers = {
				"Csphere-Api-Key":API_KEY,
			},
		)
		show_http(response)
	except requests.exceptions.RequestException as e:
		show_http(e)
		return None

	if 200 == response.status_code:
		for data in json.loads(response.content):
			if data['name'] == name:
				return data['id']

	return None

#列出具有指定标签的节点id
def get_nodes_by_tag(key, value):
	print('################列出节点################')

	try:
		response = requests.post(
			url = SERVER_URL + "api/labels/node",
			params = {
				"logic":"union",
			},
			headers = {
				"Csphere-Api-Key":API_KEY,
			},
			data = json.dumps([
				{
					"key": key,
					"value": value
				}
			])
		)
		show_http(response)
	except requests.exceptions.RequestException as e:
		show_http(e)
		return []

	if 200 == response.status_code:
		return json.loads(response.content)

	return []

#在指定的节点上查找指定名称的容器id
def find_container(nodes, names, moreInfo = False):
	if(not isinstance(nodes, list)):
		nodes = [nodes]
	if(not isinstance(names, list)):
		names = [names]

	ret = []

	print('在节点{nodes}中查找名为{names}的容器'.format(nodes=nodes, names=names))
	if moreInfo:
		print('返回完整容器信息')
	else:
		print('返回容器ID')

	for node in nodes:
		try:
			response = requests.get(
				url = SERVER_URL + "api/containers",
				params={
					"node_id": node,
				},
				headers={
					"Csphere-Api-Key":API_KEY,
				},
			)
			show_http(response)
		except requests.exceptions.RequestException as e:
			show_http(e)
			continue

		if 200 != response.status_code:
			continue

		for container in json.loads(response.content):
			for name in names:
				if '/' + name == container['Names'][0]:
					if moreInfo:
						ret.append(json.dumps(container))
					else:
						ret.append(container['Id'])
					break

	return ret


# 停止指定的容器
def stop_container(containers):
	if(not isinstance(containers, list)):
		containers = [containers]

	for container in containers:
		print('停止容器{container}'.format(container=container))
		try:
			response = requests.post(
				url = SERVER_URL + "api/containers/" + container + "/stop",
				headers={
					"Csphere-Api-Key":API_KEY,
				},
			)
			show_http(response)
		except requests.exceptions.RequestException as e:
			show_http(e)
			continue

		if 200 != response.status_code:
			continue

		return check_job(json.loads(response.content)['Id'])

# 删除指定的容器
def remove_container(containers):
	if(not isinstance(containers, list)):
		containers = [containers]

	for container in containers:
		print('删除容器{container}'.format(container=container))
		try:
			response = requests.delete(
				url = SERVER_URL + "api/containers/" + container,
				params={
					"force": "1",
				},
				headers={
					"Csphere-Api-Key":API_KEY,
				},
			)
			show_http(response)
		except requests.exceptions.RequestException as e:
			show_http(e)
			continue

		if 404 == response.status_code:
			print('找不到要删除的容器{container}'.format(container=container))

		if 200 == response.status_code:
			print('删除了容器{container}'.format(container=container))


# 拉镜像
def pull_image(nodes, registry_id, image):
	if(not isinstance(nodes, list)):
		nodes = [nodes]
	print('################更新镜像################')
	print(nodes)
	csv = ''
	errcode = 0
	for n in nodes:
		try:
			response = requests.post(
				url = SERVER_URL + "api/images/create",
				params={
					"nodes": n,
					"fromImage": image,
					"registry_id": registry_id,
				},
				headers={
					"Csphere-Api-Key":API_KEY,
				},
			)
			show_http(response)
		except requests.exceptions.RequestException as e:
			show_http(e)
			errcode = errcode + 1
			continue
		if 200 != response.status_code:
			errcode = errcode + 1
			continue
		errcode = check_job(json.loads(response.content)['Id']) + errcode


# 在指定的节点上创建容器
def creat_containers(nodes, data, image = None, registry_id = None, name = None, count = 1):
	print('################创建容器################')

	if(not isinstance(nodes, list)):
		nodes = [nodes]
	csv = ''
	for n in nodes:
		if '' == csv:
			csv = n
		else:
			csv = csv + ',' + n
	params = {
		"nodes":csv
	}

	if registry_id:
		params['registry_id'] = registry_id

	if name:
		params['name'] = name

	if 1 != count:
		params['count'] = count

	data = json.loads(data)

	#如果指定了REMOVE_CURRENT则移除目标节点上的同名容器
	if REMOVE_CURRENT:
		if not name:
			print('指定了移除同名容器，但未指定容器名')
		else:
			print('查找并移除同名容器……')
			if 1 == count:
				nameList = name
			else:
				nameList = []
				for i in range(1, count):
					nameList.append(name + string.atoi(i))
			oldContainers = find_container(nodes, name)
			remove_container(oldContainers)

	if not data["Env"]:
		data["Env"] = []

	data["Env"].extend(ENVS)

	if image:
		data['Image'] = image

	if not data['Image']:
		print('API文件中没有指定镜像名，也没有通过 --image 参数传入镜像名')
		return None

	#拉镜像
	if NEED_PULL:
		print('更新镜像……')
		if not registry_id:
			print('获取官方仓库ID……')
			publicRegistryId = get_registry_id('Docker Hub Public Registry')
		if pull_image(nodes, registry_id or publicRegistryId, data['Image']):
			return None




	print('API {arg}'.format(arg = json.dumps(data)))
	print('PARAMS {}'.format(json.dumps(params)))

	try:
		response = requests.post(
			url = SERVER_URL + "api/containers/create",
			params = params,
			headers = {
				"Csphere-Api-Key":API_KEY,
			},
			data = json.dumps(data)
		)
		show_http(response)
	except requests.exceptions.RequestException as e:
		show_http(e)
		return None

	if 200 == response.status_code:
		obj = json.loads(response.content)
		if obj.has_key('Id'):
			return obj['Id']

	return None




#######################

if None != REGISTRY_NAME:
	registry_id = get_registry_id(REGISTRY_NAME)
	if None == registry_id:
		print('没有找到指定的仓库')
		sys.exit(1)
	print('仓库ID是{id}'.format(id=registry_id))
else:
	registry_id = None

nodes = get_nodes_by_tag(TAG_KEY, TAG_VALUE)
print('主机节点：{nodes}'.format(nodes=nodes))
if 0 == len(nodes):
	sys.exit(1)

jobId = creat_containers(nodes, API_CONTENT, image = IMAGE_NAME, registry_id = registry_id, name = CONTAINER_NAME, count = CONTAINER_COUNT)

if None == jobId:
	print("创建任务失败")
	sys.exit(1)

if check_job(jobId):
	print("任务执行失败")
	sys.exit(1)
