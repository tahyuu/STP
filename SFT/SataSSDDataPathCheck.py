#!/usr/bin/env python

from TestBase import *
from InvokeYesNoButtonPicture import *
from multiprocessing import Pool
import time


class SataSSDDataPathCheck(TestBase):
    section_str = "Section: Sata SSD Phys Data Path Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.numOfCycle = int(self.config.Get('SataPhy_cycle'))
	self.numOfDisk = int(self.config.Get('SataPhy_number'))

    def Start(self):
	self.log.Print(SataSSDDataPathCheck.section_str)
	self.Prepare()
	#if True:
	try:
            self.DiscoverDisks()
	    for i in range(self.numOfCycle):
                self.ExerciseDisks()
                #self.ExerciseDisksAll()
            #self.EnterGEM()
            #self.CheckPhyCounter()
            #self.LeaveGEM()
	    pass
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd Chk => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: All SAS Data Path Check Pass")
            return 'PASS'

    def Prepare(self):
	home_dir = self.config.Get('HOME_DIR')
	self.comm.SendReturn('cp -n %s/tools/random_10M.bin /dev/shm' %home_dir)
	self.comm.RecvTerminatedBy()
	self.comm.SendReturn('rm -f /dev/shm/test.bin')
	self.comm.RecvTerminatedBy()
	self.comm.SendReturn('echo 1 > /proc/scsi/sg/allow_dio')
	self.comm.RecvTerminatedBy()
    def DiscoverDisks(self):
	home_dir = self.config.Get('HOME_DIR')
	#self.comm.SendReturn(home_dir+'/tools/discover_drives_sg.py ' + 'SEAGATE '+'HITACHI '+ 'ATA')
	self.comm.SendReturn(home_dir+'/tools/discover_drives_sg.py ' + 'Micron')
	result = self.comm.RecvTerminatedBy()
	self.drives_list = result.split('+')[1].split()
	if len(self.drives_list) != int(self.numOfDisk):
	    print len(self.drives_list)
	    print self.numOfDisk
	    errCodeStr="Disk_Discover_Fail"
            raise Error(self.errCode[errCodeStr], errCodeStr)
	
    def ExerciseDisks(self):
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx"
	drives=""
	home_dir = self.config.Get('HOME_DIR')
	for drive in self.drives_list:
	    if drive=="/dev/sg1":
		continue
	    drives=drives+drive+" "
	print drives
	#for drive in self.drives_list:	
	self.comm.SendReturn(home_dir+'/tools/exercise_drive_sg.py ' + drives)
	print "+++++++++++++++++++++++++++++++++++++"
	print "exercise_drive_sg.py "+drives
	line = self.comm.RecvTerminatedBy()
	print "+++++++++++++++++++++++++++++++++++++"
	print line
	if line.find('Fail') >= 0:
	    errCodeStr="Disk_ReadWrite_Fail"
            raise Error(self.errCode[errCodeStr], errCodeStr)

    def EnterGEM(self):
        self.comm.SendReturn('miniterm.py\n')
        line = self.comm.RecvTerminatedBy('GEM>')

    def LeaveGEM(self):
        self.comm.SendReturn('\x1d')
        line = self.comm.RecvTerminatedBy()

    def CheckPhyCounter(self):
        self.comm.SendReturn('ddump_phycounters')
        result = self.comm.RecvTerminatedBy('GEM>')
        result = self.comm.RecvTerminatedBy('GEM>')
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
                      default="4", \
                      help="numOfCycle specifies how many cycles for the stress test")
    parser.add_option("-d", "--num_of_disk", \
                      action="store", \
                      dest="num_of_disk", \
                      default="14", \
                      help="num_of_disk is 5 ")

    (options, args) = parser.parse_args(sys.argv)

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    config.Put('HOME_DIR',home_dir)
    numOfCycle = int(options.numOfCycle)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = SataSSDDataPathCheck(config, eventManager, log, comm)
    startTime=time.time() 
    result = test.Start()
    endTime=time.time()
    print "********************************************"
    print "Exerice time cost:%s",endTime-startTime
    print "********************************************"

    print result
