#!/usr/bin/env python
from TestBase import *
class BmcCheck(TestBase):
    section_str = "Section: BMC Version Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.BmcCheck= \
		r'(?P<Version>\d+[.]\d{2})'
	self.pattern = self.BmcCheck
	self.bmc_version_p = re.compile(self.pattern)
	self.version = config.Get('BMC_Version')
	self.bmc_username="admin"
	self.bmc_password="admin"
	self.bmc_ip="192.168.4.12"
	self.bmc_command_header="ipmitool -I lanplus -H %s -U %s -P %s %s"
    def Start(self):
	self.log.Print(BmcCheck.section_str)
	try:
	    self.GetBmcIpaddr()
            self.CheckUserSummary()
            self.CheckUserList()
            self.CheckSolInfo()
            #self.CheckMcInfo()
            self.CheckVersion()
            self.CheckFru()
            self.CheckSensor()
            self.CheckSDR()
            self.CheckSelInfo()
            self.CheckSelList()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: BMC Check")
            return 'PASS'
    def GetBmcIpaddr(self):
        #self.comm.SendReturn('ipmitool lan set 1 ipsrc dhcp')
        #line = self.comm.RecvTerminatedBy()
	
	#time.sleep(2)
        #self.comm.SendReturn('ipmitool mc reset warm')
        #line = self.comm.RecvTerminatedBy()

	#time.sleep(10)

        self.comm.SendReturn('service NetworkManager restart')
        line = self.comm.RecvTerminatedBy()
	time.sleep(5)
	self.comm.SendReturn('ipmitool lan print')
	line = self.comm.RecvTerminatedBy()
	self.BmcIpPat= \
		r'IP Address\s+:\s+(?P<bmc_ip>\d+\.\d+\.\d+\.\d+)'
	self.p = re.compile(self.BmcIpPat)
	m = self.p.search(line)
        errCodeStr = 'Get_BMC_IP_Fail'
        if m == None:
	    self.log.Print("Can not get BMC IP ADDRESS")
            raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.bmc_ip=m.group("bmc_ip")
	    if self.bmc_ip.find("192.168.4")<0:
	    	self.log.Print("BMC IP ADDRESS(%s) is not correct if should like 192.168.4.X")
            	raise Error(self.errCode[errCodeStr], errCodeStr)
    def CheckUserSummary(self):
	cmd="user summary"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
        errCodeStr = 'CheckUserSummary_FAIL'
	if line.find("Maximum IDs")<0:
	    	self.log.Print("Check User Summay Fail")
            	raise Error(self.errCode[errCodeStr], errCodeStr)
    def CheckUserList(self):
	cmd="user list"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
        errCodeStr = 'CheckUserList_FAIL'
	if line.find("ADMINISTRATOR")<0:
	    	self.log.Print("Check User List Fail")
            	raise Error(self.errCode[errCodeStr], errCodeStr)
    def CheckSolInfo(self):
	cmd="sol info"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
        errCodeStr = 'Sol_Info_FAIL'
	if line.find("Payload Port")<0:
	    	self.log.Print("Sol Info Check Fail")
            	raise Error(self.errCode[errCodeStr], errCodeStr)
    def CheckFru(self):
	cmd="fru"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
        errCodeStr = 'Fru_FAIL'
	if line.find("Board Mfg Date")<0:
	    	self.log.Print("BMC FRU Check Fail")
            	raise Error(self.errCode[errCodeStr], errCodeStr)

    def CheckSelList(self):
	cmd="sel list"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
        #errCodeStr = 'SEL_List_FAIL'
	#if line.find("Board Mfg Date")<0:
	#    	self.log.Print("BMC FRU Check Fail")
        #    	raise Error(self.errCode[errCodeStr], errCodeStr)
    def CheckSDR(self):
	bmc_sdr_ok_count=self.config.Get('BMC_SDR_OK_Count')
	#to get sdr list
	cmd="sdr"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
	#to check sdr count without no reading
	cmd="sdr | grep -v 'no reading' |wc -l"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
        errCodeStr = 'SDR_FAIL'
	if line.find(bmc_sdr_ok_count)<0:
	    	self.log.Print("BMC SDR Check Fail,some compoment response 'no reading'")
            	raise Error(self.errCode[errCodeStr], errCodeStr)
    def CheckSensor(self):
	bmc_sensor_ok_count=self.config.Get('BMC_Sensor_OK_Count')
	#to get sensor list
	cmd="sensor"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
	#to check sensor list count
	cmd="sensor | grep -E 'ok|0x0080|0x0180' | wc -l"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
        errCodeStr = 'Check_Sensor_FAIL'
	if line.find(bmc_sensor_ok_count)<0:
	    	self.log.Print("BMC Sensor Check Fail some component dosen't OK")
            	raise Error(self.errCode[errCodeStr], errCodeStr)
    def CheckVersion(self):
	#self.comm.SendReturn('service ipmi start')
	#line = self.comm.RecvTerminatedBy()
	cmd='mc info'
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
	m = self.bmc_version_p.search(line)
        errCodeStr = 'Version_Fail'
	print m
        if m == None:
            raise Error(self.errCode[errCodeStr], errCodeStr)
	version = m.group('Version')
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	print version
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	if version != self.version: 
	    self.log.Print("Version number %s is not matched to %s" % \
			(self.version, version))
            raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.log.Print("Version number %s is matched to %s" % \
			(self.version, version))
    def CheckSelInfo(self):
	self.SelVersionCheck= \
		r'Version\s+:\s+(?P<Version>[\w\W]+?)\s+'
	self.p = re.compile(self.SelVersionCheck)
	self.Sel_version = self.config.Get('Sel_Version')
	cmd="sel info"
	command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,cmd)
	self.comm.SendReturn(command)
	line = self.comm.RecvTerminatedBy()
	m = self.p.search(line)
        errCodeStr = 'Sel_Info_FAIL'
	print m
        if m == None:
            raise Error(self.errCode[errCodeStr], errCodeStr)
	version = m.group('Version')
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	print version
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	if version != self.Sel_version: 
	    self.log.Print("Version number %s is not matched to %s" % \
			(self.version, version))
            raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.log.Print("Version number %s is matched to %s" % \
			(self.version, version))
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])",
                          version="0.1")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
	parse.error("wrong number of arguments")
	sys.exit(1)
    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = BmcCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
