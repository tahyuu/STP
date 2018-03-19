#!/usr/bin/env python

import httplib, os
from TestBase import *
from datetime import datetime
from optparse import OptionParser
from Configure import *
from Log import *
from TestBase import Error

class FFGetUnitInfo(TestBase):
    section_str = "Section: FlexFlow GetUnitInfo"
    #def __init__(self, config, log):
    def __init__(self, config,log, comm):
	eventManager=None
	TestBase.__init__(self, config, eventManager, log, comm)
	self.config = config
	self.log = log
	self.s = open('/home/bft/SatiFT/TestConfig/getUnitInfo.xml', 'r').read()
	self.SERVER_ADDR = "10.209.40.153"
	#self.SERVER_ADDR = "pnantd27/FFTesterWS_HONEYWELL/"
	#self.SERVER_ADDR = "pnantd27"
	self.SERVER_PORT = 80
	self.SOAP_ACTION = "http://www.flextronics.com/FFTesterWS/GetUnitInfo"
	#self.SOAP_ACTION = "http://pnantd27/FFTesterWS_HONEYWELL/FFTesterWS.asmx?op=GetUnitInfo"
	#self.SOAP_ACTION = "http://pnantd27/FFTesterWS_HONEYWELL/FFTesterWS.asmx?op=GetUnitInfo"
	self.STATION_NAME = 'SGT-SFT'
	self.map = {	'SerialNumber': 'CanisterSN', \
			'Canister_PN': 'CanisterPN', \
			'MAC1': 'BmcMAC1', \
			'MAC2': 'BmcMAC2', \
			'MAC3': 'EthMAC1', \
			'MAC4': 'EthMAC2', \
			'MAC5': 'EthMAC3', \
			'WWN1': 'SasCtlWWN', \
			'WWN2': 'SasExpWWN', \
			'MAC6': 'SasExpMAC', \
			'PCBA_PN': 'PcbaPN', \
			'SystemLevelSN': 'PcbaSN'}

    def BuildErrorTable(self):
        self.errCodePath = '/home/bft/SatiFT/SFT/ErrorCode.txt'
        self.errCode = {}
        try:
            f = open(self.errCodePath, 'r')
        except IOError, exception:
            print "ErrorCode file not found", exception
            sys.exit(1)
        for l in f.readlines():
            ll = l.split()
            ll2 = ll[1].split('.')
            #print l, ll
            #print ll2, self.__class__.__name__
            try:
                if ll2[0] == self.__class__.__name__:
                    self.errCode[ll2[1].strip()] = ll[0]
            except IndexError:
                pass
        #print self.errCode
        f.close()

    def Prepare(self):
	s1 = self.s.replace("@SERIAL_NUM@", self.config.Get('PcbaSN')) 
	self.getUnitInfoXML = s1.replace("@STATION_NAME@", self.STATION_NAME) 
	self.log.Print('HTTP Send => '+self.getUnitInfoXML)
	self.ConstructHead()
	self.unitInfoResult = 2
	self.unitInfoData = {}

    def ConstructHead(self):
	print self.getUnitInfoXML
	#self.getUnitInfoXML='''<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><GetUnitInfo xmlns="http://www.flextronics.com/FFTesterWS/"><strRequest>&lt;GetUnitInfo xmlns="urn:GetUnitInfo-schema" SerialNumber="RMS1003612G0007" /&gt;</strRequest><strUnitInfo /><strStationName>SGT-BFT</strStationName><strUserID /></GetUnitInfo></soap:Body></soap:Envelope>'''
	blen = len(self.getUnitInfoXML)
	self.requestor = httplib.HTTP(self.SERVER_ADDR, self.SERVER_PORT)
	self.requestor.putrequest("POST", "/fftesterws_seagate/fftesterws.asmx")
	self.requestor.putheader("Host", self.SERVER_ADDR)
	self.requestor.putheader("Content-Type", 'text/xml; charset="utf-8"')
	self.requestor.putheader("Content-Length", str(blen))
	self.requestor.putheader("SOAPAction", self.SOAP_ACTION)
	self.requestor.endheaders()

    def Start(self):
	self.log.Print(FFGetUnitInfo.section_str)
	try:
            self.BuildErrorTable()
	    self.Prepare()
	    self.SendSOAP()
	    self.Get()
	    #self.config.Put('FFCPU',self.GetValue('CPUPN'))
	    #self.config.Put('FFCPU','HW_CPU_6C_85W')
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        else:
            self.log.Print("TestChk=> PASS: FlexFlow Barcode Checking")
	    return 'PASS'

    def Get(self):
	for key in self.map.keys():
		print self.map[key]
		if key:
			Value=self.GetValue(key,self.reply_body)
		if Value:
			self.config.Put(self.map[key],Value)
			print Value
		else:
			self.log.Print("Can't get the %s Value in flex flow" %key)
	    		errCodeStr = 'Permission_For_Proceeding_Fail'
	    		raise Error(self.errCode[errCodeStr], errCodeStr)
        self.log.PrintNoTime('      PCBA SN: ' + \
                self.config.Get('PcbaSN'))
        self.log.PrintNoTime('      PCBA PN: ' + \
                self.config.Get('PcbaPN'))
        self.log.PrintNoTime('  Canister SN: ' + \
                self.config.Get('CanisterSN'))
        self.log.PrintNoTime('     BMC MAC1: ' + \
                       self.config.Get('BmcMAC1'))
        self.log.PrintNoTime('     BMC MAC2: ' + \
                       self.config.Get('BmcMAC2'))
        self.log.PrintNoTime('     ETH MAC1: ' + \
                       self.config.Get('EthMAC1'))
        self.log.PrintNoTime('     ETH MAC2: ' + \
                       self.config.Get('EthMAC2'))
        self.log.PrintNoTime('     ETH MAC3: ' + \
                       self.config.Get('EthMAC3'))
        self.log.PrintNoTime(' SAS CTRL WWN: ' + \
                       self.config.Get('SasCtlWWN'))
        self.log.PrintNoTime('  SAS EXP MAC: ' + \
                       self.config.Get('SasExpMAC'))
        self.log.PrintNoTime('  SAS EXP WWN: ' + \
                       self.config.Get('SasExpWWN'))
        self.log.PrintNoTime('')
	#for line in lines:
	#    if self.pattLabel.match(line):
	#	line2 = line.split('=')
	#	print self.GetValue(line2[1],self.reply_body)
			
		
    def SendSOAP(self):
	#raise Error('02020', 'test')
	self.requestor.send(self.getUnitInfoXML)
	(status_code, message, reply_headers) = self.requestor.getreply()
	reply_body = self.requestor.getfile().read()
	self.reply_body = reply_body
	self.log.Print('HTTP Recv => ' + reply_body)

	l = re.findall("&lt;Name&gt;(.+?)&lt;/Name&gt;&lt;Value&gt;(.*?)&lt;/Value&gt;&lt;UserID&gt;admin&lt;/UserID&gt;",reply_body)
	for i in l:
            self.unitInfoData[i[0]] = i[1]
	if re.findall('<GetUnitInfoResult>(\d+)</GetUnitInfoResult>',reply_body):
		self.unitInfoResult = int(re.findall('<GetUnitInfoResult>(\d+)</GetUnitInfoResult>',reply_body)[0])
	else:
		self.log.Print("please make sure you can access the url http://10.209.40.153/fftesterws_seagate/fftesterws.asmx")
	    	errCodeStr = 'Permission_For_Proceeding_Fail'
	    	raise Error(self.errCode[errCodeStr], errCodeStr)
	#print self.PaserResponse("Canister_PN",reply_body)
	if self.unitInfoResult != 0:
	    self.log.Print("the flex flow return value is %s, for more information please connect IT guys." %self.unitInfoResult)
	    errCodeStr = 'Permission_For_Proceeding_Fail'
	    raise Error(self.errCode[errCodeStr], errCodeStr)
    def GetValue(self,key,reply_body):
	value=""
	p= re.compile(r'%s[\s\S]+?Value&gt;(?P<Value>[\s\S]+?)&lt;/Value' %key)
	if key:
		p= re.compile(r'%s[\s\S]+?Value&gt;(?P<Value>[\s\S]+?)&lt;/Value' %key)
		m = p.search(reply_body)
		if m:
			value= m.group('Value')
	return value

    #def GetValue(self, name):
#	return self.unitInfoData[name]

if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog SerialNumber",
                          version="0.1")
    (options, args) = parser.parse_args()

    if len( args ) != 1:
        sys.exit("Usage: FFGetUnitInfo.py SerailNumber")

    config = Configure('/home/bft/SatiFT/SFTConfig.txt')
    config.Put('PcbaSN', args[0])

    log = Log()
    log.Open('test.log')

    comm = None
    #eventManager = EventManager()
    #ffclient = FFGetUnitInfo(config, eventManager, log, comm)
    ffclient = FFGetUnitInfo(config,  log, comm)
    result = ffclient.Start()
    print result
