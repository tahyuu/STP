#!/usr/bin/env python

from TestBase import *


class SSDCheck(TestBase):
    section_str = "Section: SSD Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.model = self.config.Get('SSD_Model')
        self.patternModel = r'Product:\s+(?P<model>\w+\s\w+)\W+'
        self.pModel = re.compile(self.patternModel)

        self.fw1 = self.config.Get('SSD_FW_V1')
        self.fw2 = self.config.Get('SSD_FW_V2')
        self.fw3 = self.config.Get('SSD_FW_V3')
	self.patternFW = r'Revision:\s+(?P<fw>\w+)\W+'
	self.pFW = re.compile(self.patternFW)

        self.WSpeed = float(self.config.Get('SSD_WSpeed'))
        self.RSpeed = float(self.config.Get('SSD_RSpeed'))
	self.patternSpeed = r'(?P<Speed>\d{1,3}.\d{1,3}\s)+MB/s'
	self.pSpeed = re.compile(self.patternSpeed)
   
	self.size = self.config.Get('SSD_Size') 
        self.Qty = self.config.Get('SSD_Qty')
	#self.comm.setTimeout(90)
        
    def Start(self):
	self.log.Print(SSDCheck.section_str)
        try:
	    self.FindSSD()
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        except Exception, exception:
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail'))
	    print exception
            return 'FAIL ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail')
        else:
            self.log.Print("TestChk => PASS: SSD Verify")
	    return 'PASS'

    def FindSSD(self):
	self.comm.SendReturn('fdisk -l | grep "%s GB"' % self.size)
	line = self.comm.RecvTerminatedBy()
	drive_list = re.findall(r'Disk (\S+):', line)
	print drive_list
	if len(drive_list) != int(self.Qty):
            errCodeStr = 'Device_Count_Fail'
	    self.log.Print('SSD Qty %s is not match to %s'%(len(drive_list),self.Qty))
            raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.log.Print('SSD Qty %s is match to %s'%(len(drive_list),self.Qty))	
            #self.comm.setTimeout(120)		
            self.comm.SendReturn('dd if=/dev/urandom of=/dev/shm/TestDataIn.dat bs=1M count=500')
            result = self.comm.RecvTerminatedBy()
	    for drive in drive_list:
                self.CheckModelFW(drive)
	    for drive in drive_list:
    		self.WriteReadTestData(drive)

    def CheckModelFW(self, drive):
	self.comm.SendReturn('smartctl -d scsi -a ' + drive)
	result = self.comm.RecvTerminatedBy()
	m = self.pModel.search(result)
	if m == None:
            errCodeStr = 'Others_Fail'
	    raise Error(self.errCode[errCodeStr], errCodeStr)
	errCodeStr = 'SSD_Model_Fail'
	print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
	tmp = [m.group('model')]
	print tmp
	print [self.model]
	print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
	if m.group('model').strip() != self.model:
	    self.log.Print('SSD model %s is not correct' % m.group('model'))
	    raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.log.Print('SSD model %s is correct' % m.group('model'))
        	    
    	m = self.pFW.search(result)
	if m == None:
            errCodeStr = 'Others_Fail'
	    raise Error(self.errCode[errCodeStr], errCodeStr)    	
	errCodeStr = 'SSD_FW_Version_Fail'
	if m.group('fw') != self.fw1 and m.group('fw') != self.fw2 and m.group('fw') != self.fw3:
	    self.log.Print('SSD FW version %s is not correct' % m.group('fw'))
	    raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.log.Print('SSD FW version %s is correct' % m.group('fw'))
            
    def WriteReadTestData(self, drive):
        self.comm.SendReturn('dd if=/dev/shm/TestDataIn.dat of=' + drive + ' bs=1M count=500 oflag=dsync')
        result = self.comm.RecvTerminatedBy()
        m = self.pSpeed.search(result)
        if m == None:
            errCodeStr = 'Others_Fail'
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            if float(m.group('Speed')) > self.WSpeed:
                self.log.Print ('The Write Speed ' + str(m.group('Speed')) + ' is greater than ' +  \
                    str(self.WSpeed))
            else:
                self.log.Print ('The Write Speed ' + str(m.group('Speed')) + ' is lower than ' + \
                    str(self.WSpeed))
                errCodeStr = 'Write_Speed_Fail'
                raise Error(self.errCode[errCodeStr], errCodeStr)
	time.sleep(0.2)
	#time.sleep(1)
        self.comm.SendReturn('dd if=' + drive + ' of=/dev/shm/TestDataOut.dat bs=1M count=500 oflag=dsync')
	result = self.comm.RecvTerminatedBy()
        m = self.pSpeed.search(result)
	if m == None:
            errCodeStr = 'Others_Fail'
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            if float(m.group('Speed')) > self.RSpeed:
                self.log.Print ('The Read Speed ' + str(m.group('Speed')) + ' is greater than ' +  \
                    str(self.RSpeed))
            else:
                self.log.Print ('The Read Speed ' + str(m.group('Speed')) + ' is lower than ' + \
                    str(self.RSpeed))
                errCodeStr = 'Read_Speed_Fail'
                raise Error(self.errCode[errCodeStr], errCodeStr)

        self.comm.SendReturn('diff /dev/shm/TestDataOut.dat /dev/shm/TestDataIn.dat')
	line = self.comm.RecvTerminatedBy()
	#self.comm.SendReturn('echo $?')
	#line = self.comm.RecvTerminatedBy()
	errCodeStr = 'Write_Read_Fail'
	if line.find('differ') > -1:
            self.log.Print("SSD Read Write Fail")
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            self.log.Print("SSD Read Write Pass")


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    (options, args) = parser.parse_args()

    home_dir = os.environ['Zuari_BFT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    serial_port = config.Get('port')
    comm = Comm232(config, log, eventManager, serial_port) 

    test = SSDCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
