#!/usr/bin/env python

import httplib, os, time
from datetime import datetime
from optparse import OptionParser
from Configure import *
from Log import *
from TestBase import Error
import xml.sax.saxutils

class FFSaveResult():
    section_str = "Section: FlexFlow SaveResult"
    def __init__(self, config, log):
	self.config = config
	self.log = log
	self.s = open(self.config.Get('HOME_DIR') + '/TestConfig/saveResult.xml', 'r').read()
	#self.s = open('/TestConfig/saveResult.xml', 'r').read()
	self.SERVER_ADDR = "10.192.155.42"
	#self.SERVER_ADDR = "172.30.31.28"
	self.SERVER_PORT = 80
	self.SOAP_ACTION = "http://www.flextronics.com/FFTesterWS/SaveResult"
	self.STATION_NAME = 'SGT-BFT'
	self.DutName="Laguna Seca"
	self.CUSTOMER="Seagate"
	#self.STATION_NAME = 'BFT01_NPI-C3C'

    def BuildErrorTable(self):
        self.errCodePath = self.config.Get('HOME_DIR') + '/FT/ErrorCode.txt'
        #self.errCodePath = '/home/bft/SatiFT/FT/ErrorCode.txt'
        self.errCode = {}
        try:
            f = open(self.errCodePath, 'r')
        except IOError, exception:
            print "ErrorCode file not found", exception
            sys.exit(1)
        for l in f.readlines():
            ll = l.split('\t')
	    if len(ll)<2:
		continue
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
	SN = self.config.Get('PcbaSN') 
	#self.config.Put('StartTime', datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
	timeStampStart = self.config.Get('StartTime')
	timeStampEnd = self.config.Get('EndTime')
	time_format = '%Y-%m-%d %H:%M:%S'
	#self.config.Put('StartTime', datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
	#testTime = str(datetime.strptime(timeStampEnd, time_format) - datetime.strptime(timeStampStart, time_format)).split('.')[0]
	print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	print (datetime.strptime(timeStampEnd, time_format) - datetime.strptime(timeStampStart, time_format)).seconds
	#testTimestr = datetime.strptime(timeStampEnd, time_format) - datetime.strptime(timeStampStart, time_format)
	#testTimestr = datetime.strptime(timeStampEnd, time_format) - datetime.strptime(timeStampStart, time_format)
	testTime=(datetime.strptime(timeStampEnd, time_format) - datetime.strptime(timeStampStart, time_format)).seconds
	#print time.mktime(datetime.strptime(timeStampEnd, time_format))
	testErrorCode = self.config.Get('ErrorCode')
	testGroup = ''
	for index, value in enumerate(self.config.Get('flexflow_group')):
	    if len(value)<3 or (len(value)>0 and value[0]==""):
		continue
	    #tmp = '&lt;GROUP NAME="@step@" COMMENT="@errorcode@" SETPGROUP="" GROUPINDEX="@index@" LOOPINDEX="" TYPE="" RESOURSE="" MODULETIME="" TOTALTIME="@duration@" TIMESTAMP="@start@" STATUS="@status@" /&gt;'
	    tmp = '&lt;GROUP NAME="@step@" STEPGROUP="" GROUPINDEX="@index@" LOOPINDEX="-1" TYPE="" TIMESTAMP="@start@" MODULETIME="0"  RESOURCE="" TOTALTIME="@duration@" STATUS="@status@" &gt;'\
                  '&lt;TEST NAME="@step@" DESCRIPTION="@errorcode@" UNIT="" VALUE="" HILIM="" LOLIM="" STATUS="@status@" RULE="EQ" TARGET="" DATATYPE="" /&gt;&lt;/GROUP&gt;'
	    t0 = tmp.replace('@DUT_NAME@', self.DutName)
	    t1 = t0.replace('@CUSTOMER@', self.CUSTOMER)
	    t1 = t0.replace('@step@', value[2])
	    t2 = t1.replace('@errorcode@', value[3])
	    t3 = t2.replace('@index@', str(index+1))
	    t4 = t3.replace('@duration@', value[1])
	    t5 = t4.replace('@start@', value[0])
	    if value[3] != '':
		t6 = t5.replace('@status@', 'Failed')
	    else:
		t6 = t5.replace('@status@', 'Passed')
	    testGroup = testGroup + t6
	#print 'testGroup = ' + testGroup
	#html_str='''<?xml version="1.0" ?><BATCH TIMESTAMP="" SYNTAX_REV="" COMPATIBLE_REV=""><FACTORY NAME="PNG-P5" LINE="" TESTER="@STATION_NAME@" FIXTURE="" SHIFT="" USER="admin"/><PRODUCT NAME="@DUT_NAME@" REVISION="" FAMILY="" CUSTOMER="@CUSTOMER@" /><REFS SEQ_REF="" FTS_REF="" LIM_REF="" CFG_REF="" CAL_REF="" INSTR_REF=""/><PANEL ID="" COMMENT="" RUNMODE="Production" TIMESTAMP="" TESTTIME="61.025213" WAITTIME="0" STATUS="Passed"><DUT ID="RMS1003612G0007" COMMENT="" PANEL="0" SOCKET="0" TIMESTAMP="2016-03-18T02:11:21.287+08:00" TESTTIME="61.025213" STATUS="Passed"></DUT></PANEL></BATCH>'''
	html_str='''<?xml version="1.0" ?><BATCH TIMESTAMP="" SYNTAX_REV="" COMPATIBLE_REV=""><FACTORY NAME="PNG-P5" LINE="" TESTER="@STATION_NAME@" FIXTURE="" SHIFT="" USER="admin"/><PRODUCT NAME="@DUT_NAME@" REVISION="" FAMILY="" CUSTOMER="@CUSTOMER@" /><REFS SEQ_REF="" FTS_REF="" LIM_REF="" CFG_REF="" CAL_REF="" INSTR_REF=""/><PANEL ID="" COMMENT="" RUNMODE="Production" TIMESTAMP="" TESTTIME="@TEST_TIME@" WAITTIME="0" STATUS="@TEST_RESULT@"><DUT ID="@SERIAL_NUMBER@" COMMENT="" PANEL="0" SOCKET="0" TIMESTAMP="@TIME_STAMP_START@.000" TESTTIME="@TEST_TIME@" STATUS="@TEST_RESULT@">@Test_Group@</DUT></PANEL></BATCH>'''
	html_html_1=xml.sax.saxutils.escape(html_str)
	self.saveResultXML  = self.s.replace("@ResultsXML@",html_html_1)
	#self.saveResultXML  = s7.replace("@ResultsXML@",html_html_1) 
	s0 = self.saveResultXML.replace('@DUT_NAME@', self.DutName)
	testResult = self.config.Get('TestResult')
	SN=self.config.Get('CanisterSN')
	s1 = s0.replace("@SERIAL_NUMBER@", SN) 
	s2 = s1.replace("@TIME_STAMP_START@", timeStampStart) 
	s3 = s2.replace("@TIME_STAMP_END@", timeStampEnd) 
	s4 = s3.replace("@TEST_TIME@", str(testTime)) 
	s5 = s4.replace("@TEST_RESULT@", testResult) 
	s6 = s5.replace("@STATION_NAME@", self.STATION_NAME) 
	s7  = s6.replace("@ERROR_CODE@", testErrorCode) 
	s8  = s7.replace('@CUSTOMER@', self.CUSTOMER)
	s9  = s8.replace('@Test_Group@', testGroup)
	self.saveResultXML  = s9
	self.log.Print('HTTP Send => ' + self.saveResultXML)
	self.ConstructHead()
	self.unitInfoResult = 2
	self.unitInfoData = {}

    def ConstructHead(self):
	blen = len(self.saveResultXML)
	self.requestor = httplib.HTTP(self.SERVER_ADDR, self.SERVER_PORT)
	self.requestor.putrequest("POST", "/fftesterws_seagate/fftesterws.asmx")
	#self.requestor.putrequest("POST", "/fftestereuropa/FFTesterWS.asmx")
	self.requestor.putheader("Host", self.SERVER_ADDR)
	self.requestor.putheader("Content-Type", 'text/xml; charset="utf-8"')
	self.requestor.putheader("Content-Length", str(blen))
	self.requestor.putheader("SOAPAction", self.SOAP_ACTION)
	self.requestor.endheaders()

    def Start(self):
	self.log.Print(FFSaveResult.section_str)
        try:
	    self.BuildErrorTable()
	    self.Prepare()
            self.SendSOAP()
        except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        else:
            self.log.Print("TestChk => OK: FlexFlow Save Result")
            return 'PASS'

    def SendSOAP(self):
	#raise Error('03020', 'test')
	self.requestor.send(self.saveResultXML)
	(status_code, message, reply_headers) = self.requestor.getreply()
	reply_body = self.requestor.getfile().read()
	self.log.Print('HTTP Recv <= ' + reply_body)

	#print "status code:", status_code
	#print "status message:", message
	#print "HTTP reply body:\n", reply_body

	try:
            self.unitInfoResult = int(re.findall('<SaveResultResult>(\d+)</SaveResultResult>',reply_body)[0])
	    if self.unitInfoResult != 0:
            	errCodeStr = 'Return_Error_Fail'
            	raise Error(self.errCode[errCodeStr], errCodeStr)
        except IndexError:
	    self.unitInfoData = re.findall('<faultstring>(.+)</faultstring>', reply_body)[0]
	    self.log.Print('flexflow: '+self.unitInfoData)
            errCodeStr = 'Permission_For_Proceeding_Fail'
            raise Error(self.errCode[errCodeStr], errCodeStr)

    def GetValue(self, name):
	return self.unitInfoData[name]

if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog SerialNumber TestResult TestErrorCode",
                          version="0.1")
    (options, args) = parser.parse_args()
    
    if len( args ) != 3:
        sys.exit("Usage: FFSaveResult.py SerialNumber TestResult TestErrorCode")

    home_dir = os.environ['SATI_FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR', home_dir)
    #SN = 'fzhb30500040'
    config.Put('CanisterSN', args[0])

    log = Log()
    log.Open('test.log')

    config.Put('TestResult', args[1]) 
    config.Put('ErrorCode', args[2]) 
    timeStampStart = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time.sleep(10)
    timeStampEnd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    config.Put('StartTime', timeStampStart)
    config.Put('EndTime', timeStampEnd)
    #config.Put('flexflow_group', [['2014-08-04 15:28:32', '0:00:44', 'BmcSelClear', '26010']])
    config.Put('flexflow_group', [])
    print config.Get('PcbaSN')
    print config.Get('TestResult')
    print config.Get('ErrorCode')
    print config.Get('StartTime')
    print config.Get('EndTime')
    print config.Get('flexflow_group'), type(config.Get('flexflow_group'))

    ffclient = FFSaveResult(config, log)
    result = ffclient.Start()
    print result
