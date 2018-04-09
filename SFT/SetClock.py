#!/usr/bin/env python

from TestBase import *
import re

class SetClock(TestBase):
    section_str = "Section: Set Sati System and HW Clock"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.maxTimeDiff = 100 

    def Start(self):
	self.log.Print(SetClock.section_str)
        try:
	    self.GetDateTime()
	    self.SetDateTime()
	    #self.CheckDateTime()
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd Chk => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        except Exception, exception:
            print exception
            return 'FAIL ErrorCode=%s' % self.errCode['Others_Fail']
        else:
            self.log.Print("Tester Chk => OK: Set Sati System and HW Clock")
	    return 'PASS'

    def GetDateTime(self):
	#p = re.compile(r'(?P<date>\d{12})')
        cmdStr = "date +'%m%d%H%M%Y'"
	proc_date = subprocess.Popen(cmdStr, shell=True, \
                                      stdout=subprocess.PIPE, \
                                      stderr=subprocess.PIPE)
        proc_date.wait()
        result = proc_date.communicate()[0].strip()
	self.log.Print("Month/Day/Hour/Minute/Year : " + result)
	self.datetime = result

    def SetDateTime(self):
	#restart bmc
        self.comm.SendReturn('ipmitool lan set 1 ipsrc dhcp')
        line = self.comm.RecvTerminatedBy()
	
	time.sleep(2)
        self.comm.SendReturn('ipmitool mc reset warm')
        line = self.comm.RecvTerminatedBy()
	self.comm.SendReturn("")
	self.comm.RecvTerminatedBy()
	cmdStr = 'date ' + self.datetime
	self.comm.SendReturn(cmdStr)
	self.comm.RecvTerminatedBy()
	self.comm.SendReturn('hwclock --systohc --utc')
	self.comm.RecvTerminatedBy()

    def CheckDateTime(self):
	self.comm.SendReturn("")
	self.comm.RecvTerminatedBy()
        cmdStr = "date +%s"
	self.comm.SendReturn(cmdStr)
	result = self.comm.RecvTerminatedBy()
        errCodeStr = 'Set_Date_Time_Fail'
	deltaTime = int(result.split('\r\n')[1].strip()) - self.GetDateTimeEpoch()
	if abs(deltaTime) > self.maxTimeDiff:
            self.log.Print("The time difference is %d seconds" % abs(deltaTime))
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            self.log.Print("The time difference is %d seconds" % deltaTime)
            self.log.Print("Set System and HW clock OK")


    def GetDateTimeEpoch(self):
	#p = re.compile(r'(?P<date>\d{12})')
        cmdStr = "date +%s"
	proc_date = subprocess.Popen(cmdStr, shell=True, \
                                      stdout=subprocess.PIPE, \
                                      stderr=subprocess.PIPE)
        proc_date.wait()
        result = proc_date.communicate()[0].strip()
	#print result, len(result)
	return int(result)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    (options, args) = parser.parse_args()

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    time.sleep(1)
    comm = Comm232(config, log, eventManager, serial_port) 
    test = SetClock(config, eventManager, log, comm)
    result = test.Start()
    print result
