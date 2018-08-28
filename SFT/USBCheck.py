#!/usr/bin/env python

from TestBase import *
from InvokeMessagePopup import *
from InvokeYesNoButtonPicture import *
from WaitingTimer import WaitingTimer

class USBCheck(TestBase):
    section_str = "Section: USB Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.fw1 = self.config.Get('SSD_FW_V1')
	self.model = self.config.Get('SSD_MODEL')
	self.size=self.config.Get("SSD_SIZE")
	#below item for DVT
	#self.cmd_usb_virtual_device_info="./storage-tool-64 -pciid 8086:8d31 -usbpath 0:3.1:1.0 -usbpath 0:3.2:1.0 -usbpath 0:3.3:1.0 -devicecount 4 -action info"
	#below item for PVT
	#self.cmd_usb_virtual_device_info="./storage-tool-64 -pcipath 0000:00:1d.0 -usbpath 0:1.3.1:1.0 -usbpath 0:1.3.2:1.0 -usbpath 0:1.3.3:1.0 -devicecount 4 -action info"
        #self.cmd_usb_info="./storage-tool-64 -pciid 8086:8d31 -usbpath 0:2:1.0 -devicecount 1 -action info -smart"
        #self.cmd_usb_rwspeed="./storage-tool-64 -pciid 8086:8d62 -scsipath 0:0:0:0 -devicecount 1 -action testspeed -speed 10"
        #self.cmd_usb_rwspeed="./storage-tool-64 -pciid 8086:8d31 -scsipath 0:0:0:0 -devicecount 1 -action testspeed -speed 10"
        self.PciList_file = self.config.Get('PciList_file')
        if self.PciList_file == "s1.list" or self.PciList_file == "s2.list":
		self.usb_path="-usbpath 0:3:1.0 -usbpath 0:2:1.0"
	elif self.PciList_file == "zt_s1.list":
		self.usb_path="-usbpath 0:1:1.0"
	else:
		self.usb_path="-usbpath 0:5:1.0 -usbpath 0:2:1.0"
        #self.cmd_usb_rwspeed="./storage-tool-64 -pciid 8086:8d31 -usbpath 0:1:1:0 -devicecount 1 -action testspeed -speed 10"
        #####################################Check with Pciid###################################
        self.cmd_usb1_info="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af %s -devicecount 1 -action info" %self.usb_path
        self.cmd_usb1_rwspeed="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af %s -devicecount 1 -action testspeed -speed 35" %self.usb_path
        self.cmd_usb1_ramdom_test="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af %s -devicecount 1 -action writeread -count 1M -force" %self.usb_path
        self.cmd_usb2_info="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af -usbpath 0:3:1.0 -devicecount 1 -action info"
        self.cmd_usb2_rwspeed="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af -usbpath 0:3:1.0 -devicecount 1 -action testspeed -speed 10"
        self.cmd_usb2_ramdom_test="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af -usbpath 0:3:1.0 -devicecount 1 -action writeread -count 1M -force"
        self.cmd_usb3_info="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af -usbpath 0:4:1.0 -devicecount 1 -action info"
        self.cmd_usb3_rwspeed="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af -usbpath 0:4:1.0 -devicecount 1 -action testspeed -speed 10"
        self.cmd_usb3_ramdom_test="/root/CMCC/tools/storage-tool-64 -pciid 8086:a1af -usbpath 0:4:1.0 -devicecount 1 -action writeread -count 1M -force"
        #####################################Check with Pciid###################################
        #####################################Check with PciBUS###################################
        #self.cmd_usb1_info="./storage-tool-64 -pcipath 0000:00:14.0 -usbpath 0:1:1.0 -devicecount 1 -action info"
        #self.cmd_usb1_rwspeed="./storage-tool-64 -pcipath 0000:00:14.0 -usbpath 0:1:1.0 -devicecount 1 -action testspeed -speed 10"
        #self.cmd_usb1_ramdom_test="./storage-tool-64 -pcipath 0000:00:14.0 -usbpath 0:1:1.0 -devicecount 1 -action writeread -count 1M -force"
        #self.cmd_usb2_info="./storage-tool-64 -pcipath 0000:00:14.0 -usbpath 0:2:1.0 -devicecount 1 -action info"
        #self.cmd_usb2_rwspeed="./storage-tool-64 -pcipath 0000:00:14.0 -usbpath 0:2:1.0 -devicecount 1 -action testspeed -speed 10"
        #self.cmd_usb2_ramdom_test="./storage-tool-64 -pcipath 0000:00:14.0 -usbpath 0:2:1.0 -devicecount 1 -action writeread -count 1M -force"
        #####################################Check with PciBUS###################################

	#self.fw1 = "X211200"
	#self.model = "SanDisk"
	self.patternFW = r'FwRev=(?P<fw>\w+),\W+'
	self.pFW = re.compile(self.patternFW)
	self.patternModel = r'Model=(?P<model>\w+),\W+'
	self.pModel = re.compile(self.patternModel)
    def LoadDriver(self):
        self.comm.SendReturn("modprobe -r usb_storage")
	line = self.comm.RecvTerminatedBy()
	time.sleep(3)
        self.comm.SendReturn("modprobe -r sg")
	line = self.comm.RecvTerminatedBy()
	time.sleep(3)
        self.comm.SendReturn("modprobe -r xhci_hcd")
	line = self.comm.RecvTerminatedBy()
	time.sleep(3)
        self.comm.SendReturn("modprobe xhci_hcd")
	line = self.comm.RecvTerminatedBy()
	time.sleep(3)
        self.comm.SendReturn("modprobe sg")
	line = self.comm.RecvTerminatedBy()
	time.sleep(3)
        self.comm.SendReturn("modprobe usb_storage")
	line = self.comm.RecvTerminatedBy()
        self.comm.SendReturn("lsmod | grep usb")
	line = self.comm.RecvTerminatedBy()
	time.sleep(3)
        errCodeStr = 'USB_Load_Driver_Fail'
	if line.find("usb_storage")<0:
		self.log.Print("USB Driver load fail")
		raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
		self.log.Print("USB Driver load sucess")

    def Start(self):
	self.log.Print(USBCheck.section_str)
        try:
	    self.FindUSBDevices()
	    self.TestUSBDrivesCacheReadSpeed(1)
	    #self.TestUSBDrivesCacheReadSpeed(2)
	    #self.comm.setTimeout(22)
	    #self.TestUSBDriveswithRandomData(2)
	    #self.FindSataSSD()
	    #self.CheckModelFW()
	    #self.WriteReadTestData()
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
            self.log.Print("Tester Chk => OK: USB Verify")
	    return 'PASS'
	
    def TestUSBDriveswithRandomData(self,index):
	if index==1:
		cmd_usb_ramdom_test=self.cmd_usb1_ramdom_test
	else:
		cmd_usb_ramdom_test=self.cmd_usb2_ramdom_test
        self.comm.SendReturn(cmd_usb_ramdom_test)
	line = self.comm.RecvTerminatedBy()
	#line='''count 1 -action writeread -count 1M -forceid 8086:8d62 -scsipath 0:0:0:0 -device
	#Storage test tool
	#Version 2.5 Copyright Flextronics Penang
	#
	#Creating random files. done.
	#Transfer data to device, read back, and compare....... done.
	#
	#Write-Read-Compare status for /dev/sg1
	#  Info: /tmp/13246d827d2f3a404883980113193f61 created with 536,870,912 bytes of random data
	#  Info: Input file crc = 6d529bbf
	#  Info: running sg_dd if=/tmp/13246d827d2f3a404883980113193f61 of=/dev/sg1 bs=512 time=1 sync=1
	#    time to transfer data: 1.513201 secs at 354.79 MB/sec
	#    >> Synchronizing cache on /dev/sg1
	#    1048576+0 records in
	#    1048576+0 records out
	#  Info: /tmp/13246d827d2f3a404883980113193f61 removed
	#  Info: running sg_dd if=/dev/sg1 of=/tmp/61716dd6f7c12ca4c0de028999231f27 bs=512 time=1 sync=1 count=1M
	#    time to transfer data: 2.664430 secs at 201.50 MB/sec
	#    1048576+0 records in
	#    1048576+0 records out
	#  Info: Output file crc = 6d529bbf
	#  Info: /tmp/61716dd6f7c12ca4c0de028999231f27 removed
	#  Info: CRC matches
	#
	#********************************************
	#*** Write-Read-Compare test status: Pass ***
	#********************************************
	#'''
        errCodeStr = 'USB_RWC_Fail'
	if line.find("Write-Read-Compare test status: Pass")<0:
		self.log.Print("USB%s Write Read compare test Fail" %index)
		raise Error(self.errCode[errCodeStr], errCodeStr)
    def TestUSBDrivesCacheReadSpeed(self,index):
        errCodeStr = 'USB_Speed_Fail'
	if index==1:
		cmd_usb_rwspeed=self.cmd_usb1_rwspeed
	else:
		cmd_usb_rwspeed=self.cmd_usb2_rwspeed
        self.comm.SendReturn(cmd_usb_rwspeed)
	line = self.comm.RecvTerminatedBy()
	#line='''Version 2.5 Copyright Flextronics Penang
	#Test bus speed on /dev/sg1
	#  Info: sg_read if=/dev/sg1 bs=512 time=2 blk_sgio=1 dio=1 count=100k
	#  Pass: Speed is 326.13 MB/sec, more then 10 MB/sec
	#*******************************
	#*** Speed test status: Pass ***
	#*******************************
	#'''
	if line.find("Speed test status: Pass")<0:
		self.log.Print("USB%s Speed test  Fail" %index)
		raise Error(self.errCode[errCodeStr], errCodeStr)
    def FindUSBDevices(self):
	usbFlag=False
	usb1Flag=False
	usb2Flag=False
	usb3Flag=False
	testTimes=0
	#find USB1/USB2
	while ((not usbFlag) and  testTimes<5):
		if (not usbFlag) and testTimes>0:
			#self.LoadDriver()
            		InvokeMessagePopup('Please check the tree usb insert well', 'Proceed')
		usb1Flag=self.CheckUSBDrivesInfo(1)
		usb2Flag=True
		usb3Flag=True
		#usb2Flag=self.CheckUSBDrivesInfo(2)
		#usb3Flag=self.CheckUSBDrivesInfo(3)
		usbFlag=usb1Flag and usb2Flag and usb3Flag
		testTimes=testTimes+1
	    		#print "Please Check the USB Insert well and the USB LED is on!!"
        errCodeStr = 'USB_Not_Found_Fail'
	if not usbFlag:
		if not usb1Flag:
			self.log.Print("USB1 Not Found")
		if not usb2Flag:
			self.log.Print("USB2 Not Found")
		if not usb3Flag:
			self.log.Print("USB3 Not Found")
		raise Error(self.errCode[errCodeStr], errCodeStr)
	#find USB1
    def CheckUSBDrivesInfo(self,index):
	if index==1:
		cmd_usb_info=self.cmd_usb1_info
	elif index==2:
		cmd_usb_info=self.cmd_usb2_info
	else:
		cmd_usb_info=self.cmd_usb3_info
        self.comm.SendReturn(cmd_usb_info)
	line = self.comm.RecvTerminatedBy()
	str_size=r'Size=[\S\s]+\s(?P<Size>\d+).\d+\s+GB'
	p_size=re.compile(str_size)
	str_product=r'Product=(?P<Product>\w+)'
	p_product=re.compile(str_product)
	str_rev=r'Revision=(?P<Revision>\w+)'
	p_rev=re.compile(str_rev)
#	line='''Storage test tool
#	Version 2.5 Copyright Flextronics Penang
#	
#	Device info for /dev/sg1
#	  Host#=1
#	  Bus#=0
#	  SCSI Id#=0
#	  LUN#=0
#	  Type=0
#	  Size=128035676160 bytes, 122104.3 MiB, 128.04 GB
#	  Block device=/dev/sda
#	  Vendor=ATA
#	  Product=Micron_M550_MTFD
#	  Revision=MU01
#	  Serial number=14220C2CF27C
#	  Controller=Intel Corporation Wellsburg sUSB Controller [AHCI mode]
#	  Controller PCI vendorID:deviceID=8086:8d62
#	  Controller PCI path=0000:00:11.4
#	  Controller SCSI path=0:0:0:0
#	    Info: smartctl -a /dev/sg1
#	      Pass smartctl -a /dev/sg1, return code is 0
#	*******************************
#	*** Info check status: Pass ***
#	*******************************
#	****************************
#	*** Device count matches ***
#	****************************'''
	#to check the SSD Present
        errCodeStr = 'USB_Not_Found_Fail'
	if line.find("Device count matches")>0:
	#	self.log.Print("USB%s Not Found" %index)
	#	raise Error(self.errCode[errCodeStr], errCodeStr)
		return True
	else:
		return False
	#smart error check
#        errCodeStr = 'USB_Smart_Error_Fail'
#	if line.find("Info check status: Pass")<0:
#		self.log.Print("USB Smart Errror Check Fail")
#		raise Error(self.errCode[errCodeStr], errCodeStr)
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    (options, args) = parser.parse_args()

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    time.sleep(1)
    comm = Comm232(config, log, eventManager, serial_port) 
    test = USBCheck(config, eventManager, log, comm)
    result = test.Start()
