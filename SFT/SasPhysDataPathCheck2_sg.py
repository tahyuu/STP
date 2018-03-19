#!/usr/bin/env python

from TestBase import *
from InvokeYesNoButtonPicture import *

class SasPhysDataPathCheck(TestBase):
    section_str = "Section: SAS Phys Data Path Check"
    def __init__(self, config, eventManager, log, comm, numOfCycle):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.numOfCycle = numOfCycle

    def Start(self):
	self.log.Print(SasPhysDataPathCheck.section_str)
	self.Prepare()
	try:
            self.DiscoverDisks()
	    self.EnterGEM()
	    self.GetPhyCounter()
	    self.LeaveGEM()
	    for i in range(self.numOfCycle):
                self.ExerciseDisks()
            self.EnterGEM()
            self.CheckPhyCounter()
            self.LeaveGEM()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            self.LeaveGEM()
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: All SAS Data Path Check Pass")
            return 'PASS'

    def Prepare(self):
	self.comm.setTimeout(60)
	self.comm.SendReturn('cp -n /root/random_10M.bin /dev/shm')
	self.comm.RecvTerminatedBy()
	self.comm.SendReturn('rm -f /dev/shm/test.bin')
	self.comm.RecvTerminatedBy()
	self.comm.SendReturn('echo 1 > /proc/scsi/sg/allow_dio')
	self.comm.RecvTerminatedBy()
	self.comm.setTimeout(20)
    def DiscoverDisks(self):
	self.comm.SendReturn('discover_drives_sg.py ' + 'SEAGATE')
	result = self.comm.RecvTerminatedBy()
	self.drives_list = result.split('+')[1].split()
	print self.drives_list
	if len(self.drives_list) != int(self.config.Get('NUM_DISKS')):
	    raise Error(self.errCode['Disk_Discover_Fail'],'Disk_Discover_Fail')
	
    def ExerciseDisks(self):
	for drive in self.drives_list:	
	    self.comm.SendReturn('exercise_drive_sg.py ' + drive)
	    line = self.comm.RecvTerminatedBy()
	    if line.find('Fail') >= 0:
	        raise Error(self.errCode['Disk_ReadWrite_Fail'],'Disk_ReadWrite_Fail')

    def EnterGEM(self):
        self.comm.SendReturn('miniterm.py\n')
        line = self.comm.RecvTerminatedBy('GEM>')

    def LeaveGEM(self):
        self.comm.SendReturn('\x1d')
        line = self.comm.RecvTerminatedBy()

    def GetPhyCounter(self):
        self.comm.SendReturn('ddump_phycounters')
        result = self.comm.RecvTerminatedBy('GEM>')
        self.phycounter = self.comm.RecvTerminatedBy('GEM>')

    def CheckPhyCounter(self):
        self.comm.SendReturn('ddump_phycounters')
        result = self.comm.RecvTerminatedBy('GEM>')
        result = self.comm.RecvTerminatedBy('GEM>')
	if self.phycounter[30:-30] == result[30:-30]:
	    self.log.Print("The phy counter doesn't increase")
	else:
	    self.log.Print("Error: The phy counter increases")
	if result.count('Valid            : 1') != 36:
	    raise Error(self.errCode['Phy_Counter_Valid_Fail'], 'Phy_Counter_Valid_Fail')
	self.log.Print('Phy 0-35 Counter Valid PASS')
	if result.count('Link Rate        : 6.0Gbps') != 36:
	    raise Error(self.errCode['Phy_Counter_Link_Rate_Fail'], 'Phy_Counter_Link_Rate_Fail')
	self.log.Print('Phy 0-35 Counter Link Rate PASS')
	if result.count('Invalid DWORDs   : 0') != 36:
            raise Error(self.errCode['Phy_Counter_Invalid_DWORDS_Fail'], 'Phy_Counter_Invalid_DWORDS_Fail')
        self.log.Print('Phy 0-35 Counter Invalid DWORDS PASS')
	if result.count('Disparity errs   : 0') != 36:
            raise Error(self.errCode['Phy_Counter_Disparity_errs_Fail'], 'Phy_Counter_Disparity_errs_Fail')
        self.log.Print('Phy 0-35 Counter Disparity errs PASS')
	if result.count('DWORD sync loss  : 0') != 36:
            raise Error(self.errCode['Phy_Counter_DWORDS_sync_loss_Fail'], 'Phy_Counter_DWORDS_sync_loss_Fail')
        self.log.Print('Phy 0-35 Counter DWORDS sync loss PASS')
	if result.count('PHY reset failed : 0') != 36:
            raise Error(self.errCode['Phy_Counter_reset_failed_Fail'], 'Phy_Counter_reset_failed_Fail')
        self.log.Print('Phy 0-35 Counter reset failed PASS')

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-n", "--numOfCycle", \
                      action="store", \
                      dest="numOfCycle", \
                      default="1", \
                      help="numOfCycle specifies how many cycles for the stress test")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
	parse.error("wrong number of arguments")
	sys.exit(1)
    home_dir = os.environ['SATI_FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    numOfCycle = int(options.numOfCycle)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = SasPhysDataPathCheck(config, eventManager, log, comm, numOfCycle)
    result = test.Start()
    print result
