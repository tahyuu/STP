#!/usr/bin/env python

from TestBase import *
from InvokeYesNoButtonPicture import *
from multiprocessing import Pool
import time


class SataSSDCheck(TestBase):
    section_str = "Section: Sata SSD Phys Data Path Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.numOfCycle = int(self.config.Get('SataPhy_cycle'))
	self.numOfDisk = int(self.config.Get('SataPhy_number'))

    def Start(self):
	self.log.Print(SataSSDCheck.section_str)
	#self.Prepare()
	#if True:
	try:
                self.TestSSD()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd Chk => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: All SAS Data Path Check Pass")
            return 'PASS'
    def TestSSD(self):
	home_dir = self.config.Get('HOME_DIR')
	checkList=[]
	checkList.append(['-pciid 8086:a1d2','2','200'])
	checkList.append(['-pciid 8086:a182','2','200'])
	TestStatus=True
	for check in checkList:
		self.cmd_ssd_info="%s/tools/storage-tool-64  %s  -devicecount %s -action info -smart" %(home_dir,check[0],check[1])
        	self.cmd_ssd_rwspeed="%s/tools/storage-tool-64 %s  -devicecount %s -action testspeed -speed %s" %(home_dir,check[0],check[1],check[2])
        	self.cmd_ssd_ramdom_test="%s/tools/storage-tool-64 %s  -devicecount %s -action writeread -count 1M -force" %(home_dir,check[0],check[1])
		self.comm.SendReturn(self.cmd_ssd_info)
		results=self.comm.RecvTerminatedBy()
		if results.find('Device count matches')<0:
			TestStatus=TestStatus and False
		self.comm.SendReturn(self.cmd_ssd_rwspeed)
		results=self.comm.RecvTerminatedBy()
		if results.find('Speed test status: Pass')<0:
			TestStatus=TestStatus and False
		self.comm.SendReturn(self.cmd_ssd_ramdom_test)
		results=self.comm.RecvTerminatedBy()
		if results.find('Write-Read-Compare test status: Pass')<0:
			TestStatus=TestStatus and False
	#if not TestStatus:
	if TestStatus==False:
	    errCodeStr="SSD_CHECK_FAIL"
            raise Error(self.errCode[errCodeStr], errCodeStr)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-n", "--numOfCycle", \
                      action="store", \
                      dest="numOfCycle", \
                      default="4", \
                      help="numOfCycle specifies how many cycles for the stress test")
    parser.add_option("-d", "--num_of_disk", \
                      action="store", \
                      dest="num_of_disk", \
                      default="14", \
                      help="num_of_disk is 5 ")

    (options, args) = parser.parse_args(sys.argv)

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    config.Put('HOME_DIR',home_dir)
    numOfCycle = int(options.numOfCycle)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = SataSSDCheck(config, eventManager, log, comm)
    startTime=time.time() 
    result = test.Start()
    endTime=time.time()
    print "********************************************"
    print "Exerice time cost:%s",endTime-startTime
    print "********************************************"

    print result
