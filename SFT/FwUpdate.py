#!/usr/bin/env python

from TestBase import *
#from GetBarcode import *
import sys
import time
import string
import pexpect
#from BristolConfig import *
from WaitingTimer import WaitingTimer

class FwUpdate(TestBase):
    section_str = "Section: FW update"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
    def Connect(self):
        self.child = pexpect.spawn('ssh root@127.0.0.1', timeout=540)
        self.child.expect('password')
	print self.child.before
	self.child.sendline('123456')
	self.child.expect(']#')
	print self.child.before

    def Start(self):
	self.log.Print(FwUpdate.section_str)
	try:
	    self.Connect()
	    self.UpdateFW()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: Fw Updated PASSED")
            return 'PASS'

    def UpdateFW(self):
        #self.child = pexpect.spawn('cd  /root/CBFT/FW/flex_cannonball_mainboard_v007/', timeout=60)
	fw_path="/root/CBFT/FW/flex_cannonball_mainboard_v007/"
        self.child.sendline('cd %s' %fw_path)
	self.child.expect(']#')
	print self.child.before
	#self.child.sendline('ls -ltr')              
	self.child.sendline('rm -rf fw_update.log')              
	self.child.expect(']#')
	self.child.sendline('./update_all.sh > fw_update.log')              
	WaitingTimer(500)
	#self.child.expect(']#')
	file_object = open("%s/fw_update.log" %fw_path)
	all_the_text = ""
	try:
     		all_the_text = file_object.read( )
	finally:
     		file_object.close( )
	result=all_the_text
	self.log.Print(result)
	#time.sleep(25)
	if result.find("Update Flash Chip O.K.")<0:
        	errCodeStr = 'FW_Update_Fail'
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
    test = FwUpdate(config, eventManager, log, comm)
    result = test.Start()
    print result
