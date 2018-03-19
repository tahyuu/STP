#!/usr/bin/env python

import httplib, os
from datetime import datetime
from optparse import OptionParser
from Configure import *
from Log import *
from TestBase import Error

class FFGetUnitInfo():
    section_str = "Section: FlexFlow GetUnitInfo"
    def __init__(self, config, log):
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
	self.STATION_NAME = 'SGT-BFT'

    def BuildErrorTable(self):
        self.errCodePath = '/home/bft/SatiFT/BFT/ErrorCode.txt'
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
	blen = len(self.getUnitInfoXML)
	print self.getUnitInfoXML
	self.requestor = httplib.HTTP(self.SERVER_ADDR, self.SERVER_PORT)
	self.requestor.putrequest("POST", "FFTesterWS_HONEYWELL/FFTesterWS.asmx")
	self.requestor.putheader("Host", self.SERVER_ADDR)
	self.requestor.putheader("Content-Type", 'text/xml; charset="utf-8"')
	self.requestor.putheader("Content-Length", str(blen))
	self.requestor.putheader("SOAPAction", self.SOAP_ACTION)
	print self.requestor.__doc__
	print dir(self.requestor)
	self.requestor.endheaders()

    def Start(self):
	self.log.Print(FFGetUnitInfo.section_str)
	try:
            self.BuildErrorTable()
	    self.Prepare()
	    self.SendSOAP()
	    #self.config.Put('FFCPU',self.GetValue('CPUPN'))
	    #self.config.Put('FFCPU','HW_CPU_6C_85W')
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        else:
            self.log.Print("TestChk=> PASS: FlexFlow Barcode Checking")
	    return 'PASS'

    def SendSOAP(self):
	#raise Error('02020', 'test')
	self.requestor.send(self.getUnitInfoXML)
	(status_code, message, reply_headers) = self.requestor.getreply()
	reply_body = self.requestor.getfile().read()
	self.log.Print('HTTP Recv => ' + reply_body)

	#print "status code:", status_code
	#print "status message:", message
	#print "HTTP reply body:\n", reply_body
	
	l = re.findall("&lt;Name&gt;(.+?)&lt;/Name&gt;&lt;Value&gt;(.*?)&lt;/Value&gt;&lt;UserID&gt;admin&lt;/UserID&gt;",reply_body)
        print reply_body
	for i in l:
            self.unitInfoData[i[0]] = i[1]
	self.unitInfoResult = int(re.findall('<GetUnitInfoResult>(\d+)</GetUnitInfoResult>',reply_body)[0])
	if self.unitInfoResult != 0:
	    errCodeStr = 'Permission_For_Proceeding_Fail'
	    raise Error(self.errCode[errCodeStr], errCodeStr)

    def GetValue(self, name):
	return self.unitInfoData[name]

if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog SerialNumber",
                          version="0.1")
    (options, args) = parser.parse_args()

    if len( args ) != 1:
        sys.exit("Usage: FFGetUnitInfo.py SerailNumber")

    config = Configure('/home/bft/SatiFT/BFTConfig.txt')
    config.Put('PcbaSN', args[0])

    log = Log()
    log.Open('test.log')

    ffclient = FFGetUnitInfo(config, log)
    result = ffclient.Start()
    print result
