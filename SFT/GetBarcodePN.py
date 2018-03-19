#!/usr/bin/env python
from TestBase import *
from Configure import *
from Log import *
import os,sys
import pexpect
import re


class GetBarcode():
    section_str = "Section: Get Barcodes from ShopFloor"
    def __init__(self, config):
	#TestBase.__init__(self, config, eventManager, log, comm)
	self.config = config
	home_str = os.environ['HOME']
	self.pattLabel = re.compile('\w+=\w+')
	self.map = {	'PCBA_SN': 'CanisterSN', \
			'PartNumber': 'CanisterPN', \
			'Matrix_LS_BMCMAC1': 'BmcMAC1', \
			'Matrix_LS_BMCMAC2': 'BmcMAC2', \
			'Matrix_LS_ETHMAC1': 'EthMAC1', \
			'Matrix_LS_ETHMAC2': 'EthMAC2', \
			'Matrix_LS_ETHMAC3': 'EthMAC3', \
			'Matrix_LS_CTRLWWN': 'SasCtlWWN', \
			'Matrix_LS_EXPWWN': 'SasExpWWN', \
			'Matrix_LS_EXPMAC': 'SasExpMAC', \
			'LS_PCBAPN': 'PcbaPN', \
			'Matrix_LS_PCBASN': 'PcbaSN',\
			'Mxsys_LS_PCBASN': 'PcbaSN',\
			'MxSys_LS_BMCMAC1': 'BmcMAC1', \
			'MxSys_LS_BMCMAC2': 'BmcMAC2', \
			'MxSys_LS_ETHMAC1': 'EthMAC1', \
			'MxSys_LS_ETHMAC2': 'EthMAC2', \
			'MxSys_LS_ETHMAC3': 'EthMAC3', \
			'MxSys_LS_CTRLWWN': 'SasCtlWWN', \
			'MxSys_LS_EXPWWN': 'SasExpWWN', \
			'MxSys_LS_EXPMAC': 'SasExpMAC', \
			'LS_PCBASN': 'PcbaSN', \
			'LS_HLAPN': 'CanisterPN', \
}

    def Start(self):
	try:
		self.Connect()
		self.GetFromShopFloor()
		self.Get()
		print self.config.Get("CanisterPN")
		#self.CheckMacSequence()
		#self.CheckIBLast5Digits()
		#self.CheckIbGuidSequence()
		#self.CheckExpCtrl30HDifference()
		#self.CheckSNLast5Digits()
	except Error, error:
            errCode, errMsg = error
            return 'FAIL ErrorCode=%s' % errCode
        else:
            return 'PASS'

    def Connect(self):
        #self.child = pexpect.spawn('ssh root@192.168.5.210', timeout=60)
        #self.child.expect('cisuts:~ #')
        #print self.child.before
        self.child = pexpect.spawn('ssh root@localhost', timeout=60)
        #self.child.expect('cisuts:~ #')
	self.child.expect('password: ')
        print self.child.before
        self.child.sendline('1234567')

    def GetFromShopFloor(self):
        #promptStr = 'tin]#'
        promptStr = ']#'
        #sn = self.config.Get('PcbaSN')
        sn = self.config.Get('LS_Canister_SN')
        #self.child.sendline('ssh stars@stars')
        self.child.expect(promptStr)
        print self.child.before
        self.child.sendline('pwd')
        self.child.expect(promptStr)
        print self.child.before
        self.child.sendline('cd SFC')
        self.child.expect(promptStr)
        print self.child.before
        #self.child.sendline('cd BFT')
        #self.child.expect(promptStr)
        #print self.child.before 
	print sn
        self.child.sendline('pwd')
        self.child.expect(promptStr)
	print promptStr
        #self.child.sendline("./HLAStdIntr " + sn+" | grep -v DELL_ | grep -v DATE_ALPHA | grep -v FC=")
        self.child.sendline("./HLAStdIntr " + sn+" | grep -v DELL_ | grep -v DATE_ALPHA | grep -v FC= | grep -v HLASN | grep -v Matrix_LS_ETHMAC1WITHDASH")
        #self.child.sendline("./HLAStdIntr " + sn)
        self.child.expect(promptStr)
	print promptStr
        ShopGOT=self.child.before
        if not 'SUCCESS' in ShopGOT:
           print 'The SN you sent has Error !'
           self.child.close()
           sys.exit(1)
        self.config.Put('ShopFloorLabels', self.child.before)
        self.child.sendline('echo $?')
        self.child.expect(promptStr)
        result = self.child.before
        print result
        result2 = result.split('\r\n')

        self.child.sendline('exit')
        #self.child.expect('cisuts:~ #')
        print self.child.before
        self.child.close()
        #m = self.pReturn.search(result)
        #if m != None:
        #    print 'return value = ', m.group('value')
        if result2[1] != '0':
            raise Error('05010', 'Proceeding_Test_Fail')

    def CheckMacSequence(self):
	ll = ['EthMAC1', 'EthMAC2', 'EthMAC3','BmcMAC1', 'BmcMAC2']
	#ll = ['EthMAC1', 'EthMAC2', 'BmcMAC1', 'BmcMAC2', 'IbMAC1', 'IbMAC2']
	num0 = int(self.config.Get(ll[0]), 16)
	for l in ll:
	    #print l, self.config.Get(l), int(self.config.Get(l), 16)
	    num = int(self.config.Get(l), 16)
	    print l, hex(num), num0==num
	    num0 = num0 + 1

    def CheckExpCtrl30HDifference(self):
        expWWN = int(self.config.Get('SasExpWWN'), 16)
        ctlWWN = int(self.config.Get('SasCtlWWN'), 16)
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        print expWWN, ctlWWN
	print (ctlWWN - expWWN) 
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        if (ctlWWN - expWWN) != 50:
                raise Error('02050', 'ExpCtrlWWN30H_Fail')

    def CheckSNLast5Digits(self):
        print self.config.Get('CanisterSN')[-5:] == self.config.Get('PcbaSN')[-5:]
	print "**********************************************"
	print self.config.Get('CanisterSN')[-5:]
	print self.config.Get('PcbaSN')[-5:]
	print "**********************************************"
        if self.config.Get('CanisterSN')[-5:] != self.config.Get('PcbaSN')[-5:]:
            raise Error('02060', 'SNLast5Digits_Fail')


    def Get(self):
        lineStr = self.config.Get('ShopFloorLabels')
	lines = lineStr.split('\n')
	flag = 0
	try:
		for line in lines:
		    print line
		    if self.pattLabel.match(line):
			line2 = line.split('=')
			if line2[0].find('Matrix_LS_SASCTRLWWN') >= 0 and flag==0:
			    self.config.Put(self.map[line2[0]], line2[1].strip('\r'))
			    flag = 1
			if line2[0].find('Matrix_LS_SASCTRLWWN') < 0:
			    self.config.Put(self.map[line2[0]], line2[1].strip('\r'))
		############################################
		#in DVT there is a station not pass, remove to bft by force,so there is no CanisterPN in shop floor add below line to temporaly
		############################################
		#if self.config.Get('CanisterPN')=="No such key":
		#	self.config.Put("CanisterPN",'1003612-02')
	
	except:
		errCodeStr="Get_Barcode_Fail"
	else:
        	return 'PASS'


   	#there is no Canister PN in the Shop floor. so need to set it to defalt value 
	#self.config.Put('PcbaPN', '0980107-02')
	#canisterSN = self.config.Get('CanisterSN')
	#num = 'RCS0980107G' + canisterSN[-4:]
	#self.config.Put('PcbaSN', num) 
     	#yong
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RMS1003612G006J", \
                      help="serialNumber specifies the UUT SN")
                      # 00 -> RCS0976428G00X0
    (options, args) = parser.parse_args()
    home_dir = os.environ['SATI_FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    serial_port = config.Get('port')

    eventManager = EventManager()

    config.Put('CanisterSN', options.serialNumber)
    config.Put('LS_Canister_SN', options.serialNumber)
    #log = Log()
    #log.Open('test.log')
    #comm = Comm232(config, log, eventManager, serial_port)
    #comm = None

    test = GetBarcode(config )
    result = test.Start()
    print result
