# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os

from ipip import IP
from ipip import IPX

IP.load("17monipdb.dat")
print IP.find("118.28.8.8"), "!", "!"