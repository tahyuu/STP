#!/usr/bin/env python

from TestBase import *
from InvokeMessagePopup import *
from InvokeYesNoButtonPicture import *
from WaitingTimer import WaitingTimer
from subprocess import *
import pexpect
import time

class PciSpeedWidthCheck(TestBase):
    section_str = "Section: PCIe Devices Link Speed and Width Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
        self.PciList_file = self.config.Get('PciList_file')
	self.ASPEED = ('02:00.0', '5', '1', 'ASPEED')
	self.FIBER  = ('18:00.0', '8', '8', 'FIBBER')
	self.RAID1 =   ('5f:00.0', '8', '8', 'RAID1')
	self.Ethernet1 = ('af:00.0', '5', '4', 'Ethernet1')
	self.Ethernet2 = ('af:00.1', '5', '4', 'Ethernet2')
	self.RAID2 =   ('b1:00.0', '8', '8', 'RAID2')
	self.RAID_s1 =   ('d8:00.0', '8', '8', 'RAID1')
        self.LnkStaPatt = \
                r'LnkSta:\W+' + \
                r'Speed (?P<Speed>\d*[.]*\d)GT\/s,\W+' + \
                r'Width x(?P<Width>\d{1,2}),\W+'
        self.patternLnkSta = re.compile(self.LnkStaPatt)

    def Start(self):
        try:
	    print self.PciList_file
	    self.CheckPciSpeedWidth(self.ASPEED)
	    self.CheckPciSpeedWidth(self.FIBER)
            if self.PciList_file == "s4.list":
	    	self.CheckPciSpeedWidth(self.RAID1)
            if self.PciList_file == "s1.list":
	    	self.CheckPciSpeedWidth(self.RAID_s1)
	    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	    print self.PciList_file
	    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            if self.PciList_file == "s3.list" or self.PciList_file == "s4.list":
	    	self.CheckPciSpeedWidth(self.RAID2)
	    	self.CheckPciSpeedWidth(self.Ethernet1)
	    	self.CheckPciSpeedWidth(self.Ethernet2)
            if self.PciList_file == "s1.list" or self.PciList_file == "s2.list":
		self.Ethernet1 = ('d9:00.0', '5', '4', 'Ethernet1')
		self.Ethernet2 = ('d9:00.1', '5', '4', 'Ethernet2')
	    	self.CheckPciSpeedWidth(self.Ethernet1)
	    	self.CheckPciSpeedWidth(self.Ethernet2)
		
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
        commandStr = 'lspci -s 0000:' + dev[0] + ' -vvn'
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
    config = Configure(home_dir + '/SFTConfig.txt')
    config.Put('HOME_DIR',home_dir)
    #config.Put('SATI_II_SN', 'RCZ0976428G006X')
    config.Put('SATI_II_SN', options.serialNumber)
    config.Put('PcbaSN', options.serialNumber)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port) 
    test = PciSpeedWidthCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
