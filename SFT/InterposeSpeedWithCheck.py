#!/usr/bin/env python

from TestBase import *
from InvokeMessagePopup import *
from InvokeYesNoButtonPicture import *
from WaitingTimer import WaitingTimer
from subprocess import *
import pexpect
import time

class InterposeSpeedWithCheck(TestBase):
    section_str = "Section: PCIe Devices Link Speed and Width Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.Int1_Storage1= ('18:00.0', '8', '8', 'Interpose1_Storage1_Ctrl')
	self.Int1_Storage2= ('18:00.1', '8', '8', 'Interpose1_Storage2_Ctrl')
	self.Int1_Ethernet= ('18:00.2', '8', '8', 'Interpose1_Ethernet_Ctrl')
	self.Int2_Storage1= ('19:00.0', '8', '8', 'Interpose2_Storage1_Ctrl')
	self.Int2_Storage2= ('19:00.1', '8', '8', 'Interpose2_Storage2_Ctrl')
	self.Int2_Ethernet= ('19:00.2', '8', '8', 'Interpose2_Ethernet_Ctrl')
	self.Int3_Storage1= ('af:00.0', '8', '8', 'Interpose3_Storage1_Ctrl')
	self.Int3_Storage2= ('af:00.1', '8', '8', 'Interpose3_Storage2_Ctrl')
	self.Int3_Ethernet= ('af:00.2', '8', '8', 'Interpose3_Ethernet_Ctrl')
	self.Int4_Storage1= ('b0:00.0', '8', '8', 'Interpose4_Storage1_Ctrl')
	self.Int4_Storage2= ('b0:00.1', '8', '8', 'Interpose4_Storage2_Ctrl')
	self.Int4_Ethernet= ('b0:00.2', '8', '8', 'Interpose4_Ethernet_Ctrl')
        self.LnkStaPatt = \
                r'LnkSta:\W+' + \
                r'Speed (?P<Speed>\d*[.]*\d)GT\/s,\W+' + \
                r'Width x(?P<Width>\d{1,2}),\W+'
        self.patternLnkSta = re.compile(self.LnkStaPatt)

    def Start(self):
        try:
	    self.CheckPciSpeedWidth(self.Int1_Storage1)
	    self.CheckPciSpeedWidth(self.Int1_Storage2)
	    self.CheckPciSpeedWidth(self.Int1_Ethernet)
	    self.CheckPciSpeedWidth(self.Int2_Storage1)
	    self.CheckPciSpeedWidth(self.Int2_Storage2)
	    self.CheckPciSpeedWidth(self.Int2_Ethernet)
	    self.CheckPciSpeedWidth(self.Int3_Storage1)
	    self.CheckPciSpeedWidth(self.Int3_Storage2)
	    self.CheckPciSpeedWidth(self.Int3_Ethernet)
	    self.CheckPciSpeedWidth(self.Int4_Storage1)
	    self.CheckPciSpeedWidth(self.Int4_Storage2)
	    self.CheckPciSpeedWidth(self.Int4_Ethernet)
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd Chk => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        except Exception, exception:
            #self.log.Print(exception)
            print exception
            return 'FAIL ErrorCode=%s' % self.errCode['Others_Fail']
        else:
            self.log.Print("Tester Chk => OK: PCIe Devices Link Speed and Width Verified")
	    return 'PASS'

    def CheckPciSpeedWidth(self, dev):
	self.log.Print('Subsection: ' + dev[3] + ' Speed and Width Check')
        commandStr = 'lspci -s ' + dev[0] + ' -vvn'
        self.comm.SendReturn(commandStr)
        result = self.comm.RecvTerminatedBy()
        m = self.patternLnkSta.search(result)
        speed = m.group('Speed')
        width = m.group('Width')
        if m == None:
            raise Error(self.errCode[errCodeSpeedStr], errCodeSpeedStr)
	errCodeSpeedStr = dev[3] + '_Speed_Fail'
        if speed != dev[1]:
            self.log.Print("FAIL: %s PCIe link speed %s is not reached %s" % \
                        (dev[3], speed, dev[1]))
            raise Error(self.errCode[errCodeSpeedStr], errCodeSpeedStr)
        else:
            self.log.Print("PASS: %s PCIe link speed %s" % \
                        (dev[3], speed))
	errCodeWidthStr = dev[3] + '_Width_Fail'
        if width != dev[2]:
            self.log.Print("FAIL: %s PCIe link Width %s is not %s" % \
                        (dev[3], width, dev[2]))
            raise Error(self.errCode[errCodeWidthStr], errCodeWidthStr)
        else:
	    self.log.Print("PASS: %s PCIe link Width is %s" % \
			(dev[3], width))


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RCS0976428G00BM", \
                      help="serialNumber specifies the UUT SN")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
        parser.error("wrong number of arguments")
        sys.exit(1)

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)
    #config.Put('SATI_II_SN', 'RCZ0976428G006X')
    config.Put('SATI_II_SN', options.serialNumber)
    config.Put('PcbaSN', options.serialNumber)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port) 
    test = InterposeSpeedWithCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
