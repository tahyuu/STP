#!/usr/bin/env python

from TestBase import *
from InvokeMessagePopup import *
from InvokeYesNoButtonPicture import *
from WaitingTimer import WaitingTimer
from subprocess import *
import pexpect
import time

class ButterFlySpeedWithCheck(TestBase):
    section_str = "Section: PCIe Devices Link Speed and Width Check"
    def __init__(self, config, eventManager, log, comm,butterFlyIndex):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.butterFlyIndex=butterFlyIndex
	self.But1_Ethernet1= ('86:00.0', '8', '8', 'ButterFly1_Ethernet_Ctrl1')
	self.But1_Ethernet2= ('86:00.1', '8', '8', 'ButterFly1_Ethernet_Ctrl2')
	self.But1_Ethernet3= ('86:00.2', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But1_Ethernet4= ('87:00.0', '8', '8', 'ButterFly1_Ethernet_Ctrl1')
	self.But1_Ethernet5= ('87:00.1', '8', '8', 'ButterFly1_Ethernet_Ctrl2')
	self.But1_Ethernet6= ('87:00.2', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But1_Ethernet7= ('d8:00.0', '8', '8', 'ButterFly1_Ethernet_Ctrl1')
	self.But1_Ethernet8= ('d8:00.1', '8', '8', 'ButterFly1_Ethernet_Ctrl2')
	self.But1_Ethernet9= ('d8:00.2', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But1_Ethernet10= ('d9:00.0', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But1_Ethernet11= ('d9:00.1', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But1_Ethernet12= ('d9:00.2', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But2_Ethernet1= ('3b:00.0', '8', '8', 'ButterFly1_Ethernet_Ctrl1')
	self.But2_Ethernet2= ('3b:00.1', '8', '8', 'ButterFly1_Ethernet_Ctrl2')
	self.But2_Ethernet3= ('3b:00.2', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But2_Ethernet4= ('3c:00.0', '8', '8', 'ButterFly1_Ethernet_Ctrl1')
	self.But2_Ethernet5= ('3c:00.1', '8', '8', 'ButterFly1_Ethernet_Ctrl2')
	self.But2_Ethernet6= ('3c:00.2', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But2_Ethernet7= ('5e:00.0', '8', '8', 'ButterFly1_Ethernet_Ctrl1')
	self.But2_Ethernet8= ('5e:00.1', '8', '8', 'ButterFly1_Ethernet_Ctrl2')
	self.But2_Ethernet9= ('5e:00.2', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But2_Ethernet10= ('5f:00.0', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But2_Ethernet11= ('5f:00.1', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
	self.But2_Ethernet12= ('5f:00.2', '8', '8', 'ButterFly1_Ethernet_Ctrl3')
        self.LnkStaPatt = \
                r'LnkSta:\W+' + \
                r'Speed (?P<Speed>\d*[.]*\d)GT\/s,\W+' + \
                r'Width x(?P<Width>\d{1,2}),\W+'
        self.patternLnkSta = re.compile(self.LnkStaPatt)

    def Start(self):
        try:
	    if self.butterFlyIndex==1:
	    	self.CheckPciSpeedWidth(self.But1_Ethernet1)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet2)
	   	self.CheckPciSpeedWidth(self.But1_Ethernet3)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet4)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet5)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet6)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet7)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet8)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet9)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet10)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet11)
	    	self.CheckPciSpeedWidth(self.But1_Ethernet12)
	    elif self.butterFlyIndex==2:
	    	self.CheckPciSpeedWidth(self.But2_Ethernet1)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet2)
	   	self.CheckPciSpeedWidth(self.But2_Ethernet3)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet4)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet5)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet6)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet7)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet8)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet9)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet10)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet11)
	    	self.CheckPciSpeedWidth(self.But2_Ethernet12)
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
    test = ButterFlySpeedWithCheck(config, eventManager, log, comm,2)
    result = test.Start()
    print result
