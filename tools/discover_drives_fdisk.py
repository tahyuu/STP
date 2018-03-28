#!/usr/bin/env python

from subprocess import *
import sys
import re

p = Popen('fdisk -l | grep %s' %sys.argv[1], shell=True, stdout=PIPE, stderr=PIPE)
result=p.communicate()
devPat= \
	r'\/dev\/\w+'
pDrives = re.compile(devPat)
drive_list = pDrives.findall(result[0])
#total_list = result[0].split('\n')
str_drive_list=""
for drive in drive_list:
	str_drive_list += drive+ ' '
	
print '+' + str_drive_list + '+'
