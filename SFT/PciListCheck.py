#!/usr/bin/env python

from TestBase import *
#from InvokeMessagePopup import *
#from InvokeYesNoButtonPicture import *
#from WaitingTimer import WaitingTimer
#from GetBarcode import *
from subprocess import *
#import pexpect
import time

class PciListCheck(TestBase):
    section_str = "Section: PCIe List Check"
    def __init__(self, config, eventManager, log, comm,list_file):
	self.list_file=list_file
	TestBase.__init__(self, config, eventManager, log, comm)
    def LspciCheck(self,check_list,lspci_list_gold):
	# check_list: the list which lspci command return
	# lspci_list_gold: the list gold list which stored in pc
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	print check_list 
	print lspci_list_gold
	all_component_flags=[]
	for li in lspci_list_gold:
		#to check li in lspci_check file and create a temp array to store the coponent flag
		component_flag=False
		for  lli in check_list:
			if li.replace('\n','')==lli.replace('\r\n',''):
				component_flag=True
				break
		all_component_flags.append(component_flag)
	#print all_component_flags
	return all_component_flags

    def Start(self):
	self.log.Print(PciListCheck.section_str)
	lspci_list_gold=[]
	sku=self.config.Get('CanisterPN')
        try:
	    #to read the golden file
	    sku="SFT1_EVT"
	    errCodeStr="Pci_List_standard_file_missing"
	    check_filename="/root/CMCC/PciList/%s" %self.list_file
            try:
                fsock = open(check_filename, "rb", 0)
            	try:
                #fsock.seek(-128, 2)
	 		tagdata = fsock.readlines()
			for li in tagdata:
				lspci_list_gold.append(li.replace('\n',''))
		finally:
			fsock.close()
	    except IOError:
		self.log.Print( "Please check if there is %s.list standard file in PciList folder. if there is no such file ,please create it \n\
					Method : issue command 'lspci' in Goldern Unit DUT, and store the response as %s.list standard file" %(sku,sku))
                raise Error(self.errCode[errCodeStr], errCodeStr)
	        pass
	    errCodeStr="Pci_List_Error"
	    self.log.Print('Subsection:  PCIE List Check')
            commandStr = 'lspci'
            self.comm.SendReturn(commandStr)
            result = self.comm.RecvTerminatedBy()
	    print result
	    #to check if there is some pcie device missing.
	    all_component_flags=self.LspciCheck(result.split('\n')[0:-1],lspci_list_gold)
 	    #print test results
	    all_component_flag=True
	    for co in all_component_flags:
		all_component_flag=all_component_flag and co
	    if all_component_flag:
		self.log.Print( "PASS,all compnent in lspci check list")
	    else:
		self.log.Print("FAIL,Pcie List check missing same component")
		i=0
		for ar in all_component_flags:
			if not ar:
				self.log.Print("  PCI/PCIE Device %s is missing" %lspci_list_gold[i].replace('\n',''))
			i=i+1
                raise Error(self.errCode[errCodeStr], errCodeStr)
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd Chk => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        except Exception, exception:
            #self.log.Print(exception)
            print exception
            return 'FAIL ErrorCode=%s' % self.errCode['Others_Fail']
        else:
            self.log.Print("Tester Chk => OK: PCIe List Verified")
	    return 'PASS'

    def CheckPciSpeedWidth(self, dev):
	self.log.Print('Subsection: ' + dev[3] + ' Speed and Width Check')
        commandStr = 'pciutils-3.1.10/lspci -s ' + dev[0] + ' -vvn'
        self.comm.SendReturn(commandStr)
        result = self.comm.RecvTerminatedBy()
        m = self.patternLnkSta.search(result)
        speed = m.group('Speed')
        width = m.group('Width')
        if m == None:
            raise Error(self.errCode[errCodeSpeedStr], errCodeSpeedStr)
	errCodeSpeedStr = dev[3] + '_Speed_Fail'
        if speed != dev[1]:
            self.log.Print("FAIL: %s PCIe link speed %s is not reached %s" % \
                        (dev[3], speed, dev[1]))
            raise Error(self.errCode[errCodeSpeedStr], errCodeSpeedStr)
        else:
            self.log.Print("PASS: %s PCIe link speed %s" % \
                        (dev[3], speed))
	errCodeWidthStr = dev[3] + '_Width_Fail'
        if width != dev[2]:
            self.log.Print("FAIL: %s PCIe link Width %s is not %s" % \
                        (dev[3], width, dev[2]))
            raise Error(self.errCode[errCodeWidthStr], errCodeWidthStr)
        else:
	    self.log.Print("PASS: %s PCIe link Width is %s" % \
			(dev[3], width))


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RCS0976428G00BM", \
                      help="serialNumber specifies the UUT SN")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
        parser.error("wrong number of arguments")
        sys.exit(1)

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    config.Put('HOME_DIR',home_dir)
    #config.Put('SATI_II_SN', 'RCZ0976428G006X')
    config.Put('SATI_II_SN', options.serialNumber)
    config.Put('PcbaSN', options.serialNumber)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    config.Put('CanisterSN', options.serialNumber)
    #config.Put('SATI_II_Canister_SN', options.serialNumber)
    comm = Comm232(config, log, eventManager, serial_port) 
    #test = GetBarcode(config, eventManager, log, comm)
    #result = test.Start()
    test = PciListCheck(config, eventManager, log, comm,"SFT_EVT_Cycle.list")
    result = test.Start()
    print result
