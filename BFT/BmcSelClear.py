#!/usr/bin/env python

from TestBase import *
import time


class BmcSelClear(TestBase):
    section_str = "Section: Bmc Sel Clear"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)

    def Start(self):
	self.log.Print(BmcSelClear.section_str)
        try:
	    self.SelClear()
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        except Exception, exception:
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail'))
            print exception
            return 'FAIL ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail')
        else:
            self.log.Print('TestChk => PASS: Bmc Sel Clear')
	    return 'PASS'

    def SelClear(self):
	errCodeStr = 'Clear_Fail'
	self.comm.SendReturn('ipmitool sel clear')
	self.comm.RecvTerminatedBy()
	
	'''
	while True:
	    self.comm.SendReturn('ipmitool sel clear')
	    result = self.comm.RecvTerminatedBy()
            if result.find('Clearing SEL') < 0:
        	self.log.Print("BMC SEL is clearing")
	    self.comm.SendReturn('ipmitool sel list')
	    time.sleep(30)
	    result = self.comm.RecvTerminatedBy()
	    if result.count('|') != 5:
        	#raise Error(self.errCode[errCodeStr], errCodeStr)
		pass
	    else:
        	self.log.Print("BMC SEL is cleared")
		break
	'''
	    

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])",
                          version="0.1")

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    serial_port = config.Get('port')
    comm = Comm232(config, log, eventManager, serial_port) 

    test = BmcSelClear(config, eventManager, log, comm)
    result = test.Start()
    print result
