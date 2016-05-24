#!/usr/bin/python

import upyun
import sys

up = upyun.UpYun('spgam', 'wangyu', 'Vs5CvDsqr*!8', timeout=5, endpoint=upyun.ED_AUTO)

try:
	up.put('/ascii.txt', 'abcdefghijklmnopqrstuvwxyz\n')
except upyun.UpYunServiceException as se:
	print 'Except an UpYunServiceException ...'
	print 'Request Id: ' + se.request_id
	print 'HTTP Status Code: ' + str(se.status)
	print 'Error Message:    ' + se.msg + '\n'
	sys.exit()
except upyun.UpYunClientException as ce:
	print 'Except an UpYunClientException ...'
	print 'Error Message: ' + ce.msg + '\n'
	
print up.getlist()