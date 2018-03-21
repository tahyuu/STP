#!/usr/bin/env python

from TestBase import *
from InvokeMessagePopup import *
from WaitingTimer import WaitingTimer
from telnetlib import Telnet
from subprocess import *
from GetBarcode import *

class Ethernet10GbLoopbackCheck(TestBase):
    section_str = "Section: Ethernet 10 GB loop back test"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.config = config
        #self.pattern = self.cmdPattern.EthernetVersion
        self.pattern = "(?P<Version>0x800003e2)"
        self.p = re.compile(self.pattern)
	self.port0=""
	self.port1=""
	self.device="ixgbe"
	self.fw="0x800003e2"
    def Start(self):
	self.log.Print(Ethernet10GbLoopbackCheck.section_str)
        try:
	    self.FindEthDev()
   	    self.CheckFWPort(self.port0)
   	    self.CheckFWPort(self.port1)
	    self.CheckPortMAC(self.port0)
	    self.CheckPortMAC(self.port1)
	    self.Ethernet10GbLoopbackTest()
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
            self.log.Print("Tester Chk => OK: Ethernet 10Gb loop back Verify")
	    return 'PASS'
    def FindEthDev(self):
        #self.comm.SendReturn('/root/bin/ethdevfind.sh')
        self.comm.SendReturn('ifconfig -a | grep eth | cut -d " " -f 1')
        line = self.comm.RecvTerminatedBy()
        eth_list = line.split()
        eth_list = eth_list [12:]
        #print eth_list
        for ethdev in eth_list:
            self.comm.SendReturn('ethtool -i ' + ethdev)
            line = self.comm.RecvTerminatedBy()
            if self.port0 != '' and self.port1 != '':
               break
            #if line.find(self.device) > 0:
            if line.find(self.device) > 0 and line.find(self.fw)>0:
               if self.port0 == '':
                   self.port0 = ethdev
               else:
                   self.port1 = ethdev
                   break
        #***********************************************
        #date 2014-05-23
        #Author: Yong Tan
        #Comment: to sort the eth port,sometimes the eth index will disorder. use below code to sort the eth.
        #***********************************************
        self.comm.SendReturn('ifconfig -a | grep eth')
        line = self.comm.RecvTerminatedBy()
        eth_list = line.split('\n')
        AddrStr=[]
        for line in eth_list:
                if line.split()[0]==self.port0 or line.split()[0]==self.port1:
                        AddrStr.append(line.split())
        if eval('0x'+AddrStr[0][4].replace(':',''))> eval('0x'+AddrStr[1][4].replace(':','')):
                temp=AddrStr[0]
                AddrStr[0]=AddrStr[1]
                AddrStr[1]=temp

        print "***********************************************"
        print AddrStr
        print "***********************************************"
        self.port0=AddrStr[0][0]
        self.port1=AddrStr[1][0]

        print 'The UUT IB10GBE Port 1 is: ' + self.port0
        print 'The UUT IB10GBE Port 2 is: ' + self.port1

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
        errCodeStr = 'FW_Version_Port' + port + '_Fail'
        if m == None:
            raise Error(self.errCode[errCodeStr], errCodeStr)
        version = m.group('Version')
        if version != self.version:
            self.log.Print("Version number %s is not matched to %s" % \
                        (self.version, version))
            raise Error(self.errCode[errCodeStr], errCodeStr)
        else:
            self.log.Print("Version number %s is matched to %s" % \
                        (self.version, version))

    def CheckPortMAC(self, port):
	self.port0MAC = self.config.Get('EthMAC1')
	self.port1MAC = self.config.Get('EthMAC2')
	good_macAddr=""
	if port==self.port0:
		good_macAddr=self.port0MAC
	else:
		good_macAddr=self.port1MAC
        pattern = self.cmdPattern.EthernetMAC
        p = re.compile(pattern)
        self.comm.SendReturn("ifconfig " + port)
	line = self.comm.RecvTerminatedBy()
	matchMAC = p.search(line)
        errorCodeStr = ''
	if port==self.port0:
        	errorCodeStr = 'MAC_Port0_Fail'
	else:
        	errorCodeStr = 'MAC_Port1_Fail'
	if matchMAC != None:
	    macAddr = matchMAC.group('MAC').replace(':', '')
	    if macAddr == good_macAddr:
	        print "PASS: Ethernet Port %s MAC Check" % port
	    else:
                raise Error(self.errCode[errorCodeStr], errorCodeStr)
	else:
            raise Error(self.errCode[errorCodeStr], errorCodeStr)

    def Ethernet10GbLoopbackTest(self,):
	
	#setp1 stop fire firewall
	#  commands:
	#	service iptables stop
	#	echo 0 > /selinux/enforce
        self.comm.SendReturn("service iptables stop")
	line = self.comm.RecvTerminatedBy()

        self.comm.SendReturn("echo 0 > /selinux/enforce")
	line = self.comm.RecvTerminatedBy()

	#
	#setp2 start fire firewall
	#  commands:
	#	service vsftpd start
        self.comm.SendReturn("service vsftpd start")
	line = self.comm.RecvTerminatedBy()

	#step3 excute loop back test
	#  commands:
	#	netloop-testtool -d1 eth0 -d2 eth1 -ftpuser root -ftppassword 111111 -ftpsize 100M -maxerror 1
	#  except string 
	#	All Passed 

        errCodeStr = 'Ethernet_10Gb_Loopback_Fail'
        self.comm.SendReturn("netloop-testtool -d1 %s -d2 %s -ftpuser root -ftppassword 111111 -ftpsize 100M -maxerror 1" %(self.port0,self.port1))
	line = self.comm.RecvTerminatedBy()
	if line.find("All Passed")<0:
        	raise Error(self.errCode[errorCodeStr], errorCodeStr)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RMS1000801G04WT", \
                      help="serialNumber specifies the UUT SN")
    (options, args) = parser.parse_args()

    home_dir = os.environ['SATI_FT']
    config = Configure(home_dir + '/FTConfig.txt')

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    time.sleep(1)
    #config.Put('CanisterSN', options.serialNumber)
    #config.Put('SATI_II_Canister_SN', options.serialNumber)
    comm = Comm232(config, log, eventManager, serial_port) 
    test = GetBarcode(config, eventManager, log, comm)
    result = test.Start()

    test = Ethernet10GbLoopbackCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
