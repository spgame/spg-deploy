#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import json

def md5(str):
	import hashlib
	m = hashlib.md5()   
	m.update(str)
	return m.hexdigest()

class A17API:
	'17作业OPENAPI'
	
	SERVER_URL = 'http://www.17zuoye.com/v1'
	
	def __init__(self, app_key, secret_key, session_key):
		self.app_key = app_key
		self.secret_key = secret_key
		self.session_key = session_key
	
	def send(self, url, params):
		params['app_key'] = self.app_key
		params['session_key'] = self.session_key
		#计算sig
		str = ''
		for key in sorted(params.keys()):
			str += key + '=' + params[key] + '&'
		str = str[0:-1] + self.secret_key
		print('待签名文本是{}'.format(str))
		params['sig'] = md5(str.encode("utf8"))
		print('签名是{}'.format(params['sig']))
		print('地址是{}'.format(A17API.SERVER_URL + url + '.vpage'))
		
		try:
			response = requests.post(
				url = A17API.SERVER_URL + url + '.vpage',
				params = params
			)
		except requests.exceptions.RequestException as e:
			print(e)
			return None
		
		if 200 == response.status_code:
			print(response.content)
			result = json.loads(response.content.decode('utf-8'))
			if 'success' == result.get('result'):
				return result
		
		return None
		
	def user_get(self):
		return self.send('/user/get', {})