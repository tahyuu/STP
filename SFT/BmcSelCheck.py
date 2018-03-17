#!/usr/bin/env python

from TestBase import *
from subprocess import *


class BmcSelCheck(TestBase):
    section_str = "Section: Bmc Sel Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)

    def Start(self):
	self.log.Print(BmcSelCheck.section_str)
	#self.comm.setTimeout(40)
        try:
	    self.SelDump()
	    #self.SelRawWhiteListCheck()
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        except Exception, exception:
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail'))
            print exception
            return 'FAIL ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail')
        else:
	    return 'PASS'

    def SelDump(self):
	self.comm.SendReturn('ipmitool sel elist')
	result = self.comm.RecvTerminatedBy()
	numOfFault = result.count('failure')
	#numOfFault = result.count('Fault')
	numOfWarning = result.count('warning')
	numOfFailed = result.count('failed')
	numTotal = numOfFault + numOfWarning + numOfFailed
	self.log.Print('Total Bmc Log Abnormal Message = %d' % numTotal)
	self.log.Print('Fault Message = %d' % numOfFault)
	self.log.Print('Warning Message = %d' % numOfWarning)
	self.log.Print('Failed Message = %d' % numOfFailed)

    def SelRawWhiteListCheck(self):
	self.comm.SendReturn('cd /mnt/live/Zuari/')
	self.comm.RecvTerminatedBy()
	self.comm.SendReturn('ipmitool sel writeraw bmcraw.log')
	result = self.comm.RecvTerminatedBy()
	self.comm.SendReturn('BmcSelWhiteListCheck.py')
	result = self.comm.RecvTerminatedBy()
        if result.find("PASS") < 0:
            self.log.Print("FAIL: BMC SEL has events not included in WhiteList")
            #raise Error(self.errCode["WhiteList_Check_Fail"], "WhiteList_Check_Fail")
        else:
            self.log.Print("PASS: BMC SEL has no event not included in WhiteList")

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])",
                          version="0.1")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RCS0976428G00BM", \
                      help="serialNumber specifies the UUT SN")

    (options, args) = parser.parse_args()

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    serial_port = config.Get('port')
    comm = Comm232(config, log, eventManager, serial_port) 
    
    config.Put('PcbaSN', options.serialNumber)
    test = BmcSelCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
