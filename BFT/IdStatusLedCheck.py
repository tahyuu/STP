#!/usr/bin/env python

from TestBase import *
from InvokeYesNoButtonPicture import *
from WaitingTimer import WaitingTimer

class IdStatusLedCheck(TestBase):
    section_str = "Section: Status, ID and Fault LEDs Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.home_dir = os.environ['FT']

    def Start(self):
	self.log.Print(IdStatusLedCheck.section_str)
	try:
	    self.comm.SendReturn('ipmitool raw 0x30 0xF3 0x02 0xFF 0x64')
	    line = self.comm.RecvTerminatedBy()
            self.CheckIdLED()
            self.CheckFaultLED()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: ID Blue and Fault Yellow LEDs")
            return 'PASS'

    def CheckIdLED(self):
	self.VerifyIdLED('ON')

    def CheckFaultLED(self):
	self.comm.SendReturn('ipmitool raw 00 04 00 01')
	line = self.comm.RecvTerminatedBy()
	self.VerifyFaultLED('ON')
	self.comm.SendReturn('ipmitool raw 00 04 00 00')
	line = self.comm.RecvTerminatedBy()
	self.VerifyFaultLED('OFF')
    def VerifyIdLED(self, status):
	if status == 'ON':
	    picture = "StatusLED3.gif"
	    msgStr = "Is Indicator Blue LED Flasing?"
	else:
	    picture = "StatusLED1.gif"
	    msgStr = "Is Indicator Blue LED OFF?"
        InvokeYesNoButtonPicture(msgStr, self.home_dir + "/BFT/" + picture)
        try:
            open("REPLY_YES")
        except IOError:
            errCodeStr = 'ID_Blue_Led_Fail'
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            self.log.Print("ID Blue LED Check Pass")

	
    def VerifyFaultLED(self, status):
        if status == 'ON':
            picture = "StatusLED2.gif"
            msgStr = "Is Fault Yellow LED ON?"
        else:
            picture = "StatusLED1.gif"
            msgStr = "Is Fault Yellow LED OFF?"
        InvokeYesNoButtonPicture(msgStr, self.home_dir + "/BFT/" + picture)
        try:
            open("REPLY_YES")
        except IOError:
            errCodeStr = 'Fault_Yellow_Led_Fail'
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            self.log.Print("Fault Yellow LED Check Pass")

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
	parse.error("wrong number of arguments")
	sys.exit(1)
    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = IdStatusLedCheck(config, eventManager, log, comm)
    result = test.Start()
    print result

