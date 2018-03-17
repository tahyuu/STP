#!/usr/bin/env python

from TestBase import *
from CpuRamCheck import *
import os


class ConfigurationCheck(TestBase):
    section_str = "Section: Configuration Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.BIOS_p = re.compile(r'(?P<BIOSVersion>\d{2}[.]\d{2})\W+')
	self.BIOSVersion = config.Get('BIOS_Version')

        self.LnkStaPatt = \
                r'LnkSta:\W+' + \
                r'Speed (?P<Speed>\d*[.]*\d)GT\/s,\W+' + \
                r'Width x(?P<Width>\d{1,2}),\W+'
        self.patternLnkSta = re.compile(self.LnkStaPatt)

    def Start(self):
	self.log.Print(ConfigurationCheck.section_str)
        try:
	    self.CheckBIOSVersion()
	    self.CheckBmcVersion()
	    self.CheckBmcMac1()
	    result = CpuRamCheck(self.config, self.eventManager, self.log, self.comm).Start()
	    if result.find('FAIL') > -1:
		errCode = re.findall('\d+',result)[0]
		print errCode
		errCodeStr = result.split(': ')[1]
		print errCodeStr
            	raise Error(errCode, errCodeStr)
	    self.CheckFru()
	    self.CheckPciDevice()
	    self.CheckPciSpeedWidth('Ethernet controller', 'lspci | grep Mellanox', '4', '8', '8')
	    #self.CheckPciSpeedWidth('PCI bridge', 'lspci | grep 8796', '44', '8', '8')
	    self.comm.SendReturn('ipmitool sensor')              
	    self.comm.RecvTerminatedBy()
	    self.CheckBmcSensor('CPU Temp','ipmitool sensor | grep CPU | grep PECI', -70, -5, 'ok')
	    self.CheckBmcSensor('U11 Temp','ipmitool sensor | grep U11', 20, 55, 'ok')
	    self.CheckBmcSensor('FIO Temp','ipmitool sensor | grep FIO', 20, 40, 'ok')
	    self.CheckBmcSensor('PEX8796 Temp','ipmitool sensor | grep PEX8796', 20, 90, 'ok')
	    self.CheckBmcSensor('DIMM Temp','ipmitool sensor | grep CPU | grep DIMM', 20, 55, 'ok')
	    self.CheckBmcSensor('12V','ipmitool sensor | grep 12V', 10.143, 13.846, 'ok')
	    self.CheckBmcSensor('5V','ipmitool sensor | grep 5V', 4.234, 5.767, 'ok')
	    self.CheckBmcSensor('3V3','ipmitool sensor | grep 3V3', 2.793, 3.773, 'ok')
	    self.CheckBmcSensor('PVCCIN_CPU0','ipmitool sensor | grep PVCCIN_CPU0', 1.440, 2.136, 'ok')
	    self.CheckBmcSensor('PVPP_AB','ipmitool sensor | grep PVPP_AB', 2.136, 2.88, 'ok')
	    self.CheckBmcSensor('CPU_VCCIO','ipmitool sensor | grep CPU_VCCIO', 0.888, 1.2, 'ok')
	    self.CheckBmcSensor('P1V05_PCH','ipmitool sensor | grep P1V05_PCH', 0.888, 1.2, 'ok')
	    self.CheckBmcSensor('P1V05_AUX_PCH','ipmitool sensor | grep P1V05_AUX_PCH', 0.888, 1.2, 'ok')
	    self.CheckBmcSensor('P1V5','ipmitool sensor | grep P1V5', 1.272, 1.728, 'ok')
	    self.CheckBmcSensor('PDVDQ_AB','ipmitool sensor | grep PVDDQ_AB', 1.032, 1.392, 'ok')
	    self.CheckBmcSensor('PVTT_AB','ipmitool sensor | grep PVTT_AB', 0.504, 0.696, 'ok')
	    self.CheckBmcSensor('Fan','ipmitool sensor | grep Fan', 11000, 13760, 'ok')
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        except Exception, exception:
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail'))
            print exception
            return 'FAIL ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail')
        else:
            self.log.Print("TestChk => PASS: PCIe SLIC Devices Link Speed and Width Verified")
	    return 'PASS'

    def CheckBIOSVersion(self):
    	section_str = "Section: Bios Version Check"
	self.comm.SendReturn('dmidecode -s bios-version')
	line = self.comm.RecvTerminatedBy()
	#m = self.BIOS_p.search(line)
        #errCodeStr = 'Others_Fail'
        #if m == None:
        #    raise Error(self.errCode[errCodeStr], errCodeStr)
	#version = m.group('BIOSVersion')
	version = line.strip()
        errCodeStr = 'BIOS_Version_Fail'
	if version != self.BIOSVersion: 
	    self.log.Print("BIOS Version number %s is not matched to %s" % (self.BIOSVersion, version))
            raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.log.Print("BIOS Version number %s is matched to %s" % (self.BIOSVersion, version))
	
    def CheckBmcVersion(self):
    	section_str = "Section: Bmc Version Check"
	self.pattern = r'Firmware Revision\s+:\s+(?P<Version>\d{1,2}[.]\d{1,2})'	
	self.p = re.compile(self.pattern)
	self.version = self.config.Get('BMC_Version')
	self.comm.SendReturn('ipmitool mc info')
	line = self.comm.RecvTerminatedBy()
	m = self.p.search(line)
        errCodeStr = 'Bmc_Version_Fail'
        if m == None:
            raise Error(self.errCode[errCodeStr], errCodeStr)
	version = m.group('Version')
	if version == self.version:
	    self.log.Print("BMC Version number %s is matched to %s" % (version, self.version))
	else:
	    self.log.Print("BMC Version number %s is not matched to %s" % (version, self.version))
            raise Error(self.errCode[errCodeStr], errCodeStr)

    def CheckBmcMac1(self):
        bmcMac = self.config.Get('BmcMAC1')
        self.comm.SendReturn('ipmitool lan print 1')
        result = self.comm.RecvTerminatedBy()
        pMAC = re.compile(r'MAC Address\W+:\W+(?P<MAC>aa:bb:cc:dd:\w{2}:\w{2})')
        m = pMAC.search(result)
        errorCodeStr = 'Check_Mac1_Fail'
        if m != None:
            self.log.Print("PASS: BMC Mac1 = %s" % bmcMac)
        else:
            self.log.Print("FAIL: BMC Mac1 != %s" % bmcMac)
            raise Error(self.errCode[errorCodeStr], errorCodeStr)

    def CheckFru(self):
    	section_str = "Section: Fru Check"
	self.comm.SendReturn('ipmitool fru > /root/Zuari-EVT/TestConfig/fru.txt')              
	self.comm.RecvTerminatedBy()
        self.comm.SendReturn('cat /root/Zuari-EVT/TestConfig/fru.txt')
        self.comm.RecvTerminatedBy()
	cmdstr = 'diff /root/Zuari-EVT/TestConfig/fru.txt /root/Zuari-EVT/TestConfig/frulist.txt'
	print cmdstr
        self.comm.SendReturn(cmdstr)
        line = self.comm.RecvTerminatedBy()
        errCodeStr = 'Check_Fru_Fail'
        #self.comm.SendReturn('echo $?')
        #line = self.comm.RecvTerminatedBy()
        #if line.find('0') < 0:
        if line.find('<') > -1:
            self.log.Print("Check Fru Fail")
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            self.log.Print("Check Fru Pass")

    def CheckPciDevice(self):
    	section_str = "Section: PCIe Devices Check"
	self.log.Print(section_str)
        self.comm.SendReturn('lspci > /root/Zuari-EVT/TestConfig/pci.txt')
        self.comm.RecvTerminatedBy()
        self.comm.SendReturn('cat /root/Zuari-EVT/TestConfig/pci.txt')
        line = self.comm.RecvTerminatedBy()
	if self.config.Get('PcbaSN').find('SZ597') > -1:
	    if line.find('00:1f.2 SATA controller:') > -1:
	    	cmdstr = 'diff /root/Zuari-EVT/TestConfig/pci.txt /root/Zuari-EVT/TestConfig/M.2_597_pcilist.txt'
	    else:
	    	cmdstr = 'diff /root/Zuari-EVT/TestConfig/pci.txt /root/Zuari-EVT/TestConfig/usb_597_pcilist.txt'
	elif self.config.Get('PcbaSN').find('SZ605') > -1:
	    if line.find('00:1f.2 SATA controller:') > -1:
	    	cmdstr = 'diff /root/Zuari-EVT/TestConfig/pci.txt /root/Zuari-EVT/TestConfig/M.2_605_pcilist.txt'
	    else:
	    	cmdstr = 'diff /root/Zuari-EVT/TestConfig/pci.txt /root/Zuari-EVT/TestConfig/usb_605_pcilist.txt'
	print cmdstr
        self.comm.SendReturn(cmdstr)
        line = self.comm.RecvTerminatedBy()
        errCodeStr = 'Check_PciDevice_Fail'
        #self.comm.SendReturn('echo $?')
        #line = self.comm.RecvTerminatedBy()
        #if line.find('0') < 0:
        if line.find('<') > -1:
            self.log.Print("Check Pci Device Fail")
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            self.log.Print("Check Pci Device Pass")
			
    def CheckPciSpeedWidth(self, field, cmd, number, speed, width):
    	section_str = "Section: PCIe Devices Link Speed and Width Check"
        self.comm.SendReturn(cmd)
        result = self.comm.RecvTerminatedBy()
	if result.count(field) != int(number):
	    errCodeStr = 'CheckPciSpeedWidth(' + field + ')_Number_Fail'
            raise Error(self.errCode[errCodeStr], errCodeStr)
	bus_list = re.findall('\w{2}:\w{2}.\w', result)
	for i in bus_list:
            commandStr = 'lspci -vvns ' + i
            self.comm.SendReturn(commandStr)
            result = self.comm.RecvTerminatedBy()
            m = self.patternLnkSta.search(result)
            if m == None:
            	raise Error(self.errCode['Others_Fail'], 'Others_Fail')
            testspeed = m.group('Speed')
            testwidth = m.group('Width')
	    errCodeSpeedStr = 'CheckPciSpeedWidth(' + field + ')_Speed_Fail'
            if testspeed != speed:
		self.log.Print("FAIL: %s PCIe link speed %s is not reached %s" % (i, testspeed, speed))
		raise Error(self.errCode[errCodeSpeedStr], errCodeSpeedStr)
	    else:
		self.log.Print("PASS: %s PCIe link speed %s" % (i, speed))
	    errCodeWidthStr = 'CheckPciSpeedWidth(' + field + ')_Width_Fail'
            if testwidth != width:
		self.log.Print("FAIL: %s PCIe link Width %s is not %s" % (i, testwidth, width))
		raise Error(self.errCode[errCodeWidthStr], errCodeWidthStr)
	    else:
		self.log.Print("PASS: %s PCIe link Width %s" % (i, width))

    def CheckBmcSensor(self, field, cmd, low, high, status):
    	section_str = "Section: Bmc Sensors Check"
	self.comm.SendReturn(cmd)
	result = self.comm.RecvTerminatedBy()
	lines = result.split('\n')

	'''
	print cmd
	tmp = re.findall('\| grep (\S+)', cmd)
	print tmp
	lines = []
	for i in file('/root/log/sensor.log').read().split('\n'):
	    if len(tmp) == 1:
		if i.find(tmp[0]) > -1:
		    lines.append(i)
	    elif len(tmp) == 2:
		if i.find(tmp[0]) > -1 and i.find(tmp[1]) > -1:
		    lines.append(i)
	print '\n'.join(lines)
	'''

	errorCodeStr = 'Check_Sensor(' + field  + ')_Fail'
	for i in lines:
            if i != '' and i.find('ipmitool') == -1 and i.find('ROOT') == -1 and i.find('|') > -1:
		temp = i.split('|')[1].strip()
                status = i.split('|')[3].strip()
		try:
		    float(temp)
		except ValueError:
		    errorCodeStr = 'Check_Sensor(na value)_Fail'
                    self.log.Print( field.split()[0] + ' na value FAIL')
                    raise Error(self.errCode[errorCodeStr], errorCodeStr)
                if low <= float(temp) <= high:
		    print field + ' PASS: '+str(low)+' <= '+temp+' <= '+str(high)
                    self.log.Print( field + ' PASS: '+str(low)+' <= '+temp+' <= '+str(high))
                else:
		    print field + ' FAIL: '+str(low)+' <= '+temp+' <= '+str(high)
                    self.log.Print( field + ' FAIL: '+str(low)+' <= '+temp+' <= '+str(high))
                    raise Error(self.errCode[errorCodeStr], errorCodeStr)
                #if status != 'ok':
                #    self.log.Print( field.split()[0] + ' status FAIL')
                #    raise Error(self.errCode[errorCodeStr], errorCodeStr)


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RCS0976428G00BM", \
                      help="serialNumber specifies the UUT SN")

    parser.add_option("-p", "--part_number", \
                      action="store", \
                      dest="partNumber", \
                      default="303-335-201B-02", \
                      help="partNumber specifies the UUT PN")

    (options, args) = parser.parse_args()

    if len( args ) != 0:
        parser.error("wrong number of arguments")
        sys.exit(1)

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)
    config.Put('PcbaSN', options.serialNumber)
    config.Put('PcbaSN', 'SZ605FZ5240010')
    #config.Put('PcbaSN', 'SZ597FZ5240010')

    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    serial_port = config.Get('port')
    comm = Comm232(config, log, eventManager, serial_port) 
    test = ConfigurationCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
