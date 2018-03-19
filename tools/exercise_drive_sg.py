#!/usr/bin/env python

from subprocess import *
import sys
import multiprocessing
def ExerciseData(drive):
	#drive = sys.argv[1]
	printStr=""
	writeCmdStr = 'sg_dd if=/dev/shm/random_10M.bin of=' + drive + ' count=20480 time=2 dio=1 blk_sgio=1 bs=512'
	readCmdStr = 'sg_dd if=' + drive + ' of=/dev/shm/test.bin count=20480 time=2 dio=1 blk_sgio=1 bs=512'
	#print writeCmdStr
	printStr=printStr+writeCmdStr
	pw = Popen(writeCmdStr, shell=True, stdout=PIPE, stderr=PIPE)
	result = pw.communicate()
	#print result[0]
	printStr=printStr+result[0]
	#print result[1]
	printStr=printStr+result[1]
	pr = Popen(readCmdStr, shell=True, stdout=PIPE, stderr=PIPE)
	result = pr.communicate()
	#print result[0]
	printStr=printStr+result[0]
	#print result[1]
	printStr=printStr+result[1]
	#checksumRandom = 'd7a013472640879bc4aef4136974dac0'
	checksumRandom = '2859fde508cd54b04da2874d900865eb'
	pchecksum = Popen('md5sum /dev/shm/test.bin', shell=True, stdout=PIPE, stderr=PIPE)
	result = pchecksum.communicate()
	if result[0].split()[0] == checksumRandom:
	    #print "Write/Read test data Checksum match"
	    printStr=printStr+"Write/Read test data Checksum match"
	    #print "Pass"
	    printStr=printStr+"Pass"
	else:
	    #print "Write/Read test data Checksum doesn't match"
	    printStr=printStr+"Write/Read test data Checksum doesn't match"
	    #print "Fail"
	    printStr=printStr+"Fail"
	print printStr

if __name__=="__main__":
        pool = multiprocessing.Pool(processes=10)
        for i in range(1, len(sys.argv)):
            pool.apply_async(ExerciseData, (sys.argv[i], ))
        pool.close()
        pool.join()
        print "Sub-process(es) done."

