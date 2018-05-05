#!/usr/bin/env python

from TestBase import *
from InvokeMessagePopup import *
from WaitingTimer import WaitingTimer
from telnetlib import Telnet
from subprocess import *
from GetBarcode import *
from ScanBarCode import *

class FiberLoopbackCheck4Port(TestBase):
    section_str = "Section: Ethernet 1GB loopback test"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.config = config
        self.PciList_file = self.config.Get('PciList_file')
        #self.pattern = self.cmdPattern.EthernetVersion
        self.pattern = "(?P<Version>0x800009fa)"
        self.p = re.compile(self.pattern)
	self.port0=""
	self.port1=""
	self.port2=""
	self.port3=""
        if self.PciList_file == "s1.list" or self.PciList_file == "s2.list":
		self.busIds=["0000:d9:00.0","0000:d9:00.1"]
	else:
		self.busIds=["0000:af:00.0","0000:af:00.1"]
	self.busIds=["0000:5e:00.0","0000:5e:00.1","0000:5e:00.2","0000:5e:00.3"]
	self.device="ixgbe"
	self.fw="0x800009fa"
    def Start(self):
	self.log.Print(FiberLoopbackCheck4Port.section_str)
        try:
	    self.FindEthDev()
   	    #self.CheckFWPort(self.port0)
   	    #self.CheckFWPort(self.port1)
	    #self.CheckPortMAC(self.port0)
	    #self.CheckPortMAC(self.port1)
	    self.EthernetLoopbackTest(self.port0,self.port1)
	    time.sleep(3)
            #InvokeMessagePopup('Please Plug in Ethernet Cable to Port0 Port1', 'Proceed')
	    self.EthernetLoopbackTest(self.port2,self.port3)
	    #time.sleep(5)
	    #self.EthernetLoopbackTest(self.port0,self.port2)
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd Chk => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        except Exception, error:
            self.log.Print('ERROR: %s\n' % str(error))
            errCodeStr = 'Others_Fail'
            errCode = self.errCode[errCodeStr]
            return 'FAIL ErrorCode=%s' % errCode

        else:
            self.log.Print("Tester Chk => OK: Ethernet 1G loopback Verify")
	    return 'PASS'
    def FindEthDev(self):
        #self.comm.SendReturn('/root/bin/ethdevfind.sh')
        self.comm.SendReturn('')
        line = self.comm.RecvTerminatedBy()
        self.comm.SendReturn('ifconfig -a | grep eth | cut -d " " -f 1')
        line = self.comm.RecvTerminatedBy()
        eth_list = line.split()
        #print eth_list
        #eth_list = eth_list [12:-2]
        print eth_list
        for ethdev in eth_list:
            self.comm.SendReturn('ethtool -i ' + ethdev)
            line = self.comm.RecvTerminatedBy()
            if self.port0 != '' and self.port1 != '' and self.port2!='' and self.port3!='':
               break
            if line.find(self.busIds[0]) > 0:
		self.port0 = ethdev.replace(':','')
		continue	
            if line.find(self.busIds[1]) > 0:
		self.port1 = ethdev.replace(':','')
		continue	
            if line.find(self.busIds[2]) > 0:
		self.port2 = ethdev.replace(':','')
		continue	
            if line.find(self.busIds[3]) > 0:
		self.port3 = ethdev.replace(':','')
		continue	
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	print self.port0
	print self.port1
	print self.port2
	print self.port3

    def CheckFWPort(self, port):
	self.version = self.config.Get('ETHERNET_Version')
	self.comm.SendReturn('ethtool -i ' + port)
        line = self.comm.RecvTerminatedBy()
	print "********************************"
	print self.cmdPattern.EthernetVersion
	print self.version
	print line
	print "********************************"
        self.log.Print(line)
        m = self.p.search(line)
	print m
	if port==self.port0:
        	errCodeStr = 'FW_Version_Port0_Fail'
	elif port==self.port1:
        	errCodeStr = 'FW_Version_Port1_Fail'
	else:
        	errCodeStr = 'FW_Version_Port2_Fail'
        if m == None:
            raise Error(self.errCode[errCodeStr], errCodeStr)
        version = m.group('Version')
	print version
        if version != self.fw:
            self.log.Print("Version number %s is not matched to %s" % \
                        (self.fw, version))
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            self.log.Print("Version number %s is matched to %s" % \
                        (self.fw, version))

    def CheckPortMAC(self, port):
	self.port0MAC = self.config.Get('EthMAC1')
	self.port1MAC = self.config.Get('EthMAC2')
	self.port2MAC = self.config.Get('EthMAC3')
	good_macAddr=""
	if port==self.port0:
		good_macAddr=self.port0MAC
	elif port==self.port1:
		good_macAddr=self.port1MAC
	else:
		good_macAddr=self.port2MAC
        pattern = self.cmdPattern.EthernetMAC
        p = re.compile(pattern)
        self.comm.SendReturn("ifconfig " + port)
	line = self.comm.RecvTerminatedBy()
	matchMAC = p.search(line)
        errorCodeStr = ''
	if port==self.port0:
        	errorCodeStr = 'MAC_Port0_Fail'
	elif port==self.port1:
        	errorCodeStr = 'MAC_Port1_Fail'
	else:
        	errorCodeStr = 'MAC_Port2_Fail'
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	print matchMAC
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	if matchMAC != None:
	    macAddr = matchMAC.group('MAC').replace(':', '')
	    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	    print macAddr
	    print good_macAddr
	    if macAddr == good_macAddr:
	        print "PASS: Ethernet Port %s MAC Check" % port
	    else:
                raise Error(self.errCode[errorCodeStr], errorCodeStr)
	else:
            raise Error(self.errCode[errorCodeStr], errorCodeStr)

    def EthernetLoopbackTest(self,portA,portB):
	
	#setp1 stop fire firewall
	#  commands:
	#	service iptables stop
	#	echo 0 > /selinux/enforce
        self.comm.SendReturn("systemctl stop firewalld.service")
	line = self.comm.RecvTerminatedBy()
        self.comm.SendReturn('service NetworkManager stop')
        line = self.comm.RecvTerminatedBy()
	time.sleep(3)

        #self.comm.SendReturn("service vsftpd start")
	#line = self.comm.RecvTerminatedBy()

        #self.comm.SendReturn("echo 0 > /selinux/enforce")
	#line = self.comm.RecvTerminatedBy()

	#
	#setp2 start fire firewall
	#  commands:
	#	service vsftpd start

	#step3 excute loop back test
	#  commands:
	#	netloop-testtool -d1 eth0 -d2 eth1 -ftpuser root -ftppassword 111111 -ftpsize 100M -maxerror 1
	#  except string 
	#	All Passed 

        errorCodeStr = 'Ethernet_Loopback_Fail'
        #self.comm.SendReturn("/root/CMCC/tools/netloop-testtool3-64 -d1 %s -d2 %s -ftpuser root -ftppassword 123456 -ftpsize 1G -maxerror 1" %(portA,portB))
        self.comm.SendReturn("/root/CMCC/tools/netloop-testtool3-64 -d1 %s -d2 %s -iperfspeed 9000" %(portA,portB))
	line = self.comm.RecvTerminatedBy()
        self.comm.SendReturn('service NetworkManager start')
        self.comm.RecvTerminatedBy()
	time.sleep(3)
	if line.find("All Passed")<0:
        	raise Error(self.errCode[errorCodeStr], errorCodeStr)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RMS1003612G006T", \
                      help="serialNumber specifies the UUT SN")
    (options, args) = parser.parse_args()

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    time.sleep(1)
    #config.Put('CanisterSN', options.serialNumber)
    #config.Put('SATI_II_Canister_SN', options.serialNumber)
    #config.Put('LS_Canister_SN', options.serialNumber)
    comm = Comm232(config, log, eventManager, serial_port) 
    #test = ScanBarCode(config,)
    #test = GetBarcode(config, eventManager, log, comm)
    #result = test.Start()

    test = FiberLoopbackCheck4Port(config, eventManager, log, comm)
    result = test.Start()
    print result
