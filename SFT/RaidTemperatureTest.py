#!/usr/bin/env python

from TestBase import *
#from GetBarcode import *
import sys
import time
import string
#from BristolConfig import *
from WaitingTimer import WaitingTimer

class RaidTemperatureTest(TestBase):
    section_str = "Section: Raid Temperature Test"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.raidtemplimit=80

    def Start(self):
	self.log.Print(RaidTemperatureTest.section_str)
	try:
	    self.CheckTemperture()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: Raid Temperature Test PASS")
            return 'PASS'

    def CheckTemperture(self):
        self.tempStaPatt = \
                r'ROC\s+temperature\s+:\s+(?P<TEMP>\d+)\s+degree\s+Celsius'
        self.patternTempSta = re.compile(self.tempStaPatt)
	self.comm.SendReturn('/opt/MegaRAID/MegaCli/MegaCli64 -Adpallinfo -aALL |grep -i temp |grep -i ROC')              
	result = self.comm.RecvTerminatedBy()
        m = self.patternTempSta.search(result)
        if m == None:
            raise Error(self.errCode['Others_Fail'], 'Others_Fail')
        temperature = m.group('TEMP')
	if int(temperature)>self.raidtemplimit:
            self.log.Print('Raid Temperature is %s. not in range[0,%s]' %(temperature,self.raidtemplimit))
            errCodeStr = 'Raid_Temperature_Fail'
            raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
            self.log.Print('Raid Temperature is %s. in range[0,%s]' %(temperature,self.raidtemplimit))
	
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
    config = Configure(home_dir + '/SFTConfig.txt')
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
    test = RaidTemperatureTest(config, eventManager, log, comm)
    result = test.Start()
    print result
