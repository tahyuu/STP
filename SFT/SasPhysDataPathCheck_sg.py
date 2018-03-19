#!/usr/bin/env python

from TestBase import *
from InvokeYesNoButtonPicture import *
from multiprocessing import Pool
import time


class SasPhysDataPathCheck_sg(TestBase):
    section_str = "Section: SAS Phys Data Path Check"
    def __init__(self, config, eventManager, log, comm, numOfCycle, numOfDisk):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.numOfCycle = numOfCycle
	self.numOfDisk = numOfDisk

    def Start(self):
	self.log.Print(SasPhysDataPathCheck_sg.section_str)
	self.Prepare()
	try:
            self.DiscoverDisks()
	    for i in range(self.numOfCycle):
                self.ExerciseDisks()
                #self.ExerciseDisksAll()
            #self.EnterGEM()
            #self.CheckPhyCounter()
            #self.LeaveGEM()
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
	self.comm.SendReturn('discover_drives_sg.py ' + 'SEAGATE '+'HITACHI')
	result = self.comm.RecvTerminatedBy()
	self.drives_list = result.split('+')[1].split()
	print len(self.drives_list)
	if len(self.drives_list) != int(self.numOfDisk):
	    raise Error(self.errCode['Disk_Discover_Fail'],'Disk_Discover_Fail')
	
    def ExerciseDisks(self):
	drives=""
	for drive in self.drives_list:
	    drives=drives+drive+" "
	#for drive in self.drives_list:	
	self.comm.SendReturn('exercise_drive_sg.py ' + drives)
	print "+++++++++++++++++++++++++++++++++++++"
	print "exercise_drive_sg.py "+drives
	line = self.comm.RecvTerminatedBy()
	print "+++++++++++++++++++++++++++++++++++++"
	print line
	if line.find('Fail') >= 0:
	        raise Error(self.errCode['Disk_ReadWrite_Fail'],'Disk_ReadWrite_Fail')

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
                      default="24", \
                      help="num_of_disk is 48 with HBA otherwise is 24")

    (options, args) = parser.parse_args(sys.argv)

    home_dir = os.environ['SATI_FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    numOfCycle = int(options.numOfCycle)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = SasPhysDataPathCheck_sg(config, eventManager, log, comm, numOfCycle, options.num_of_disk)
    startTime=time.time() 
    result = test.Start()
    endTime=time.time()
    print "********************************************"
    print "Exerice time cost:%s",endTime-startTime
    print "********************************************"

    print result
