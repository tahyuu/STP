#!/usr/bin/env python

from subprocess import *
import sys

p = Popen('sg_scan -i', shell=True, stdout=PIPE, stderr=PIPE)
result=p.communicate()
total_list = result[0].split('\n')
drive_list = ''
for drive_index in range(0,len(total_list),2):
	for sg_index in xrange(len(sys.argv)-1):
    		try:
        		if total_list[drive_index+1].find(sys.argv[sg_index+1]) > 0:
	    			drive_list += total_list[drive_index].split(':')[0] + ' '
				break
    		except:
			pass
print '+' + drive_list + '+'
