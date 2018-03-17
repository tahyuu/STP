#!/usr/bin/env python

from TestBase import *
#from GetBarcode import *
import sys
import time
import string
#from BristolConfig import *
from WaitingTimer import WaitingTimer

class ProgramBmcMacFru(TestBase):
    section_str = "Section: Program BMC MAC and FRU"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)

    def Start(self):
	self.log.Print(ProgramBmcMacFru.section_str)
	try:
	    self.ProgramMac()
	    self.ProgramFru()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: Program BMC MAC and FRU")
            return 'PASS'

    def StartIpmiService(self):
	self.comm.SendReturn('service ipmi start')
	result = self.comm.RecvTerminatedBy()
        errCodeStr = 'Ipmi_Start_Fail'
	if result.find('FAILED') > 0 :
            raise Error(self.errCode[errCodeStr], errCodeStr)

    def ProgramMac(self):
	bmcMac = self.config.Get('BmcMAC1')
	lh = len(bmcMac)/2
	mac1_hex_str = "0x"+bmcMac[0:2]
	mac1_com_str = bmcMac[0:2]
	for i in range(1,lh):
            mac1_hex_str = mac1_hex_str+ ' 0x' + bmcMac[2*i:2*i+2] 
            mac1_com_str = mac1_com_str + ':' + bmcMac[2*i:2*i+2] 

	bmcMac = self.config.Get('BmcMAC2')
	lh = len(bmcMac)/2
	mac2_hex_str = "0x"+bmcMac[0:2]
	mac2_com_str = bmcMac[0:2]
	for i in range(1,lh):
            mac2_hex_str = mac2_hex_str + ' 0x' + bmcMac[2*i:2*i+2] 
            mac2_com_str = mac2_com_str + ':' + bmcMac[2*i:2*i+2] 

	print mac1_hex_str  
	print mac2_hex_str  
	self.comm.SendReturn('ipmitool raw 0x06 0x52 0x0D 0xA0 0x00 0x1C 0x00 %s 0x00 0x00 %s 0x00 0x00' %(mac1_hex_str,mac2_hex_str))
	self.comm.RecvTerminatedBy()
	self.comm.SendReturn('ipmitool mc reset cold')              
	result = self.comm.RecvTerminatedBy()
	#time.sleep(25)
        WaitingTimer(35)
	self.comm.SendReturn('ipmitool lan print 1')              
	lanRe=self.comm.RecvTerminatedBy()
	lanRe=string.upper(lanRe)
	if lanRe.find(string.upper(mac1_com_str))<0:
        	errCodeStr = 'Program_Bmc_Mac1_Fail'
		raise Error(self.errCode[errCodeStr], errCodeStr)
	self.comm.SendReturn('ipmitool lan print 8')              
	lanRe=self.comm.RecvTerminatedBy()
	lanRe=string.upper(lanRe)
	if lanRe.find(string.upper(mac2_com_str))<0:
        	errCodeStr = 'Program_Bmc_Mac2_Fail'
		raise Error(self.errCode[errCodeStr], errCodeStr)
	

    def ProgramFru(self):
	# write fur header 0
	self.comm.SendReturn('ipmitool raw 0x0a 0x12 0x00 0x00 0x00 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0xff')
	self.comm.RecvTerminatedBy()
	# write fur header 1
	self.comm.SendReturn('ipmitool raw 0x0a 0x12 0x01 0x00 0x00 0x01 0x00 0x00 0x00 0x00 0x01 0x00 0xFE 0xC1 0x82 0x00 0x00 0xBD')
	self.comm.RecvTerminatedBy()
	# check fur header 0
	self.comm.SendReturn('ipmitool raw 0x0a 0x11 0x00 0x00 0x00 0x08')
	result = self.comm.RecvTerminatedBy()
	Fail_Flag=False
	if result.find("01 00 00 00 00 00 00 ff")<0:
		Fail_Flag=True
		
	# check fur header 1
	self.comm.SendReturn('ipmitool raw 0x0a 0x11 0x01 0x00 0x00 0x0D')
	result = self.comm.RecvTerminatedBy()
	if result.find("01 00 00 00 00 01 00 fe c1 82 00 00 bd")<0:
		Fail_Flag=True
	# check fur header 1
	
        errCodeStr = 'Program_Bmc_Fru_Fail'
	if Fail_Flag:
            raise Error(self.errCode[errCodeStr], errCodeStr)
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RMS0974572G0BAY", \
                      help="serialNumber specifies the UUT Canister SN")

    (options, args) = parser.parse_args()

    if len( args ) != 0:
	parser.error("wrong number of arguments")
	sys.exit(1)
    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)
    config.Put('BmcMAC1',"0140D4F5129D")
    config.Put('BmcMAC2',"0140D4F5129F")
    config.Put('SATI_II_Canister_SN', options.serialNumber)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)
    #test = GetBarcode(config, eventManager, log, comm)
    #result = test.Start()
    test = ProgramBmcMacFru(config, eventManager, log, comm)
    result = test.Start()
    print result
