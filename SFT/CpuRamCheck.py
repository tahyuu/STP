#!/usr/bin/env python

from TestBase import *

class CpuRamCheck(TestBase):
    section_str = "Section: CPU, mem Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
        self.pCPUID = re.compile(r'ID: (?P<ID>\w{2}\s\w{2}\s\w{2}\s\w{2}\s\w{2}\s\w{2}\s\w{2}\s\w{2})\W*')
	self.pCPUType = re.compile(r'Signature: Type (?P<Type>\d+), Family \d+, Model \d+, Stepping \d+\W*')
	self.pCPUFamily = re.compile(r'Signature: Type \d+, Family (?P<Family>\d+), Model \d+, Stepping \d+\W*')
	self.pCPUModel = re.compile(r'Signature: Type \d+, Family \d+, Model (?P<Model>\d+), Stepping \d+\W*')
	self.pCPUStepping = re.compile(r'Signature: Type \d+, Family \d+, Model \d+, Stepping (?P<Stepping>\d+)\W*')
	self.pCPUSpeed = re.compile(r'Current Speed: (?P<Speed>\d{4})\W*')
	self.pCPUCoreCount = re.compile(r'Core Count: (?P<CoreCount>\d+)\W*')
	self.pCPUCoreEnabled = re.compile(r'Core Enabled: (?P<CoreEnabled>\d+)\W*')
	self.CPUQty = self.config.Get('CPU_Qty')
	if self.config.Get('PcbaSN').find('SZ597') > -1:
	    pass
	elif self.config.Get('PcbaSN').find('SZ605') > -1:
	    self.config.Put('CPU_ID','F2 06 03 00 FF FB EB BF')
	    self.config.Put('CPU_Type','0')
	    self.config.Put('CPU_Family','6')
	    self.config.Put('CPU_Model','63')
	    self.config.Put('CPU_Stepping','2')
	    self.config.Put('CPU_Speed','3200')
	    self.config.Put('CPU_Core_Count','8')
	    self.config.Put('CPU_Core_Enabled','8')

	self.CPUID = self.config.Get('CPU_ID')
	self.CPUType = self.config.Get('CPU_Type')
	self.CPUFamily = self.config.Get('CPU_Family')
	self.CPUModel = self.config.Get('CPU_Model')
	self.CPUStepping = self.config.Get('CPU_Stepping')
	self.CPUSpeed = self.config.Get('CPU_Speed')
	self.CPUCoreCount = self.config.Get('CPU_Core_Count')
	self.CPUCoreEnabled = self.config.Get('CPU_Core_Enabled')

	self.pDIMMTotalWidth = re.compile(r'Total Width: (?P<DIMMTotalWidth>\d+) bits\W*')
	self.pDIMMDataWidth = re.compile(r'Data Width: (?P<DIMMDataWidth>\d+) bits\W*')
	self.pDIMMSize = re.compile(r'Size: (?P<DIMMSize>\d+)\W*')
	self.pDIMMSpeed = re.compile(r'Speed: (?P<DIMMSpeed>\d+)\W*')
	self.DIMMTotalWidth = self.config.Get('DIMM_Total_Width')
	self.DIMMDataWidth = self.config.Get('DIMM_Data_Width')
	self.DIMMSize = self.config.Get('DIMM_Size')
	self.DIMMSpeed = self.config.Get('DIMM_Speed')

    def Start(self):
	self.log.Print(CpuRamCheck.section_str)
	try:
            self.CheckCPU()
            self.CheckDIMM()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        else:
            self.log.Print("TestChk => PASS: CPU, mem Check")
            return 'PASS'

    def CheckCPU(self):
	self.log.Print("Check CPU ------------------------------------")
	self.comm.SendReturn('dmidecode -t 4')
	result  = self.comm.RecvTerminatedBy()
	
	lines = result.split('\n')
	cpu_num = 0
	for line in lines:
            if line.find('ID') > -1:
                cpu_num = cpu_num + 1
                m = self.pCPUID.search(line)
                errCodeStr = 'CPU_ID_Fail'
                if m == None:
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                ID = m.group('ID')
                print ID
                print len(ID)
                print self.CPUID
                print len(self.CPUID)
                if ID != self.CPUID: 
                    self.log.Print("CPU %s ID %s is not matched to %s" % \
                                (cpu_num, ID, self.CPUID))
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    self.log.Print("CPU %s ID %s is matched to %s" % \
                                (cpu_num, ID, self.CPUID))

            if line.find('Signature') > -1:
                m = self.pCPUType.search(line)
                errCodeStr = 'CPU_Type_Fail'
                if m == None:
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                Type = m.group('Type')
                print Type
                print self.CPUType
                if Type != self.CPUType: 
                    self.log.Print(" CPU %s Type %s is not matched to %s" % \
                                (cpu_num, Type, self.CPUType))
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    self.log.Print("CPU %s Type %s is matched to %s" % \
                                (cpu_num, Type, self.CPUType))

                m = self.pCPUFamily.search(line)
                errCodeStr = 'CPU_Family_Fail'
                if m == None:
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                Family = m.group('Family')
                print Family
                print self.CPUFamily
                if Family != self.CPUFamily: 
                    self.log.Print(" CPU %s Family %s is not matched to %s" % \
                                (cpu_num, Family, self.CPUFamily))
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    self.log.Print("CPU %s Family %s is matched to %s" % \
                                (cpu_num, Family, self.CPUFamily))

                m = self.pCPUModel.search(line)
                errCodeStr = 'CPU_Model_Fail'
                if m == None:
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                Model = m.group('Model')
                print Model
                print self.CPUModel
                if Model != self.CPUModel: 
                    self.log.Print("CPU %s Model %s is not matched to %s" % \
                                (cpu_num, Model, self.CPUModel))
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    self.log.Print("CPU %s Model %s is matched to %s" % \
                                (cpu_num, Model, self.CPUModel))

                m = self.pCPUStepping.search(line)
                errCodeStr = 'CPU_Stepping_Fail'
                if m == None:
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                Stepping = m.group('Stepping')
                print Stepping
                print self.CPUStepping
                if Stepping != self.CPUStepping: 
                    self.log.Print("CPU %s Stepping %s is not matched to %s" % \
                                (cpu_num, Stepping, self.CPUStepping))
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    self.log.Print("CPU %s Stepping %s is matched to %s" % \
                                (cpu_num, Stepping, self.CPUStepping))

            if line.find('Current Speed') > -1:
                m = self.pCPUSpeed.search(line)
                errCodeStr = 'CPU_Speed_Fail'
                if m == None:
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                Speed = m.group('Speed')
                print Speed
                print self.CPUSpeed
                if Speed != self.CPUSpeed: 
                    self.log.Print("CPU %s Speed %s is not matched to %s" % \
                                (cpu_num, Speed, self.CPUSpeed))
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    self.log.Print("CPU %s Speed %s is matched to %s" % \
                                (cpu_num, Speed, self.CPUSpeed))

            if line.find('Core Count') > -1:
                m = self.pCPUCoreCount.search(line)
                errCodeStr = 'CPU_Core_Count_Fail'
                if m == None:
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                CoreCount = m.group('CoreCount')
                print CoreCount
                print self.CPUCoreCount
                if CoreCount != self.CPUCoreCount:
                    self.log.Print("CPU %s Core Count %s is not matched to %s" % \
                                   (cpu_num, CoreCount, self.CPUCoreCount))
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    self.log.Print("CPU %s Core Count %s is matched to %s" % \
                                   (cpu_num, CoreCount, self.CPUCoreCount))

            if line.find('Core Enabled') > -1:
                m = self.pCPUCoreEnabled.search(line)
                errCodeStr = 'CPU_Core_Enabled_Fail'
                if m == None:
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                CoreEnabled = m.group('CoreEnabled')
                print CoreEnabled
                print self.CPUCoreCount
                if CoreEnabled != self.CPUCoreCount:
                    self.log.Print("CPU %s Core Enabled %s is not matched to %s" % \
                                   (cpu_num, CoreEnabled, self.CPUCoreCount))
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    self.log.Print("CPU %s Core Enabled %s is matched to %s" % \
                                   (cpu_num, CoreEnabled, self.CPUCoreCount))
                
        errCodeStr = 'CPU_Qty_Fail'
        if str(cpu_num) != self.CPUQty:
            self.log.Print('Physical CPU Qty ' + str(cpu_num) + ' not match to ' + self.CPUQty)
            print ('Physical CPU Qty ' + str(cpu_num) + ' not match to ' + self.CPUQty)
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            print ('Physical CPU Qty ' + str(cpu_num) + ' match to ' + self.CPUQty)
            self.log.Print('Physical CPU Qty ' + str(cpu_num) + ' match to ' + self.CPUQty)                        
            
    def CheckDIMM(self):
	self.log.Print("Check DIMM -------------------------------------")
	self.comm.SendReturn('dmidecode -t 17')
	result = self.comm.RecvTerminatedBy()
	#result = file('/root/log/dimm.log').read()
	if result.find('Manufacturer: NO DIMM') > 0:
            errCodeStr = 'No_DIMM_Fail'
	    self.log.Print('At least one DIMM is missing!')
            raise Error(self.errCode[errCodeStr], errCodeStr)
	self.log.Print("All RAM DIMM Slots are populated")

	ll = result.split('\n')
	dimm_num = 0
	for l in ll:
            if l.find('Total Width') >= 0:
		dimm_num = dimm_num + 1
		#print [l]
                m = self.pDIMMTotalWidth.search(l)
                if m == None:
                    errCodeStr = 'Others_Fail'
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    if m.group('DIMMTotalWidth') == self.DIMMTotalWidth:
                        self.log.Print('DIMM ' + str(dimm_num) + ' Total Width '  + m.group('DIMMTotalWidth') + ' match to ' + self.DIMMTotalWidth )
                    else:                
                        errCodeStr = 'DIMM_Total_Width_Fail'
                        self.log.Print('DIMM ' + str(dimm_num) + ' Total Width '  + m.group('DIMMTotalWidth') + ' not match to ' + self.DIMMTotalWidth )
                        raise Error(self.errCode[errCodeStr], errCodeStr)
            
	    if l.find('Data Width') >= 0:
                m = self.pDIMMDataWidth.search(l)
                if m == None:
                    errCodeStr = 'Others_Fail'
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    if m.group('DIMMDataWidth') == self.DIMMDataWidth:
                        self.log.Print('DIMM ' + str(dimm_num) + ' Data Width '  + m.group('DIMMDataWidth') + ' match to ' + self.DIMMDataWidth )
                    else:                
                        errCodeStr = 'DIMM_Data_Width_Fail'
                        self.log.Print('DIMM ' + str(dimm_num) + ' Data Width '  + m.group('DIMMDatalWidth') + ' not match to ' + self.DIMMDataWidth )
                        raise Error(self.errCode[errCodeStr], errCodeStr)
            
            if l.find('Size') >= 0:
                m = self.pDIMMSize.search(l)
                if m == None:
                    errCodeStr = 'Others_Fail'
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    if m.group('DIMMSize') == self.DIMMSize:
                        self.log.Print('DIMM ' + str(dimm_num) + ' Size '  + m.group('DIMMSize') + ' match to ' + self.DIMMSize )
                    else:                
                        errCodeStr = 'DIMM_Size_Fail'
                        self.log.Print('DIMM ' + str(dimm_num) + ' Size '  + m.group('DIMMSize') + ' not match to ' + self.DIMMSize )
                        raise Error(self.errCode[errCodeStr], errCodeStr)
            
            if l.find('Speed') == 1:
                m = self.pDIMMSpeed.search(l)
                if m == None:
                    errCodeStr = 'Others_Fail'
                    raise Error(self.errCode[errCodeStr], errCodeStr)
                else:
                    if m.group('DIMMSpeed') == self.DIMMSpeed:
                        self.log.Print('DIMM ' + str(dimm_num) + ' Speed '  + m.group('DIMMSpeed') + ' match to ' + self.DIMMSpeed )
                    else:                
                        errCodeStr = 'DIMM_Speed_Fail'
                        self.log.Print('DIMM ' + str(dimm_num) + ' Speed '  + m.group('DIMMSpeed') + ' not match to ' + self.DIMMSpeed )
                        raise Error(self.errCode[errCodeStr], errCodeStr)            

	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
	parser.error("wrong number of arguments")
	sys.exit(1)

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)
    #config.Put('PcbaSN','SZ605FZ5240019')
    config.Put('PcbaSN','SZ597FZ5240010')

    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    serial_port = config.Get('port')
    comm = Comm232(config, log, eventManager, serial_port)

    test = CpuRamCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
