#!/usr/bin/env python

from ShopFloorQueryJDM import *
from InvokeMessagePopup import *
from InvokeYesNoButton import *
from Log import Log
from datetime import datetime
from TestItem import TestItem

#from Comm232 import Comm232
#from FFGetUnitInfo import *
#from FFSaveResult import *
import sys 
import os
import subprocess
from Configure import Configure
from ScanBarCode import ScanBarCode
from FFGetUnitInfo import FFGetUnitInfo
from datetime import *
from PowerDown import *
from GetBarcodeCSV import *
from GetBarcodePN import *
from ShopFloorQuery import *
from ShopFloorPass import *
from ShopFloorFail import *
from FFSaveResult import *

class TestEngine:
    def __init__(self, config, sku):
	self.config = config
	self.sequence = self.config.Get('TestSequence')
	self.dut_name = self.config.Get('DUT_Name')
        self.eventManager = EventManager()
	self.log = Log()
	port = self.config.Get('port')
	print self.config.Get('port')
        self.comm = Comm232(self.config, self.log, self.eventManager, port)
	#self.comm.UnsetVerbose()
	#print "*********************", self.comm.verboseFlag
        #self.comm.setTimeout(3)
	self.testItems = []
	self.testItemResults=[]
	self.BuildTestItems()
	self.testResult = ''
	self.PrepareForInit()
	self.powerdown = PowerDown(self.config, self.eventManager, self.log, \
			   self.comm, 2, True)
	self.shopFloorPass = ShopFloorPass(self.config)
	self.shopFloorFail = ShopFloorFail(self.config)

    def PrepareForInit(self):
	cmdStr = '/bin/hostname'
        lsopenfile = subprocess.Popen(cmdStr, shell=True, \
                                      stdout=subprocess.PIPE, \
                                      stderr=subprocess.PIPE)
        lsopenfile.wait()
        self.hostname = lsopenfile.communicate()[0]
	self.testDate = datetime.now().strftime("%Y/%m/%d")

    def PrepareForEachTest(self):
        self.log_filename = self.config.Get('CanisterSN') + \
	     '-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
        #self.log_filename2 = self.config.Get('CanisterSN') + \
	#     '-' + datetime.now().strftime("%Y%m%d%H%M%S") + '-boot.log'
	#self.config.Put('BootLogFileName', self.log_filename2)
	print self.log_filename
	#print self.log_filename2
	home_dir = self.config.Get('HOME_DIR')
        self.log.Open(home_dir + '/FTLog/TMP/' + self.log_filename)
        #self.log.Open2(home_dir + '/FTLog/TMP/' + self.log_filename2)
        self.log.PrintNoTime('                                ')
        self.log.PrintNoTime('                                ')
	#self.log.PrintNoTime('Station : ' + self.hostname)
	#self.log.PrintNoTime('Date    : ' + self.testDate) 
	#self.log.PrintNoTime('Version : ' + self.config.Get('Version')) 
	#############################################3333
	# No need to print the below item in log, Because there information already print by GetBarcode
	#############################################3333
	#self.log.PrintNoTime('PN      : ' + self.config.Get('PN')) 
	#self.log.PrintNoTime('SN      : ' + self.config.Get('SN')) 
	#self.log.PrintNoTime('BMC_MAC1: ' + self.config.Get('BMC_MAC1')) 
	#self.log.PrintNoTime('BMC_MAC2: ' + self.config.Get('BMC_MAC2')) 
	#self.log.PrintNoTime('ETH_MAC1: ' + self.config.Get('ETH_MAC1')) 
	#self.log.PrintNoTime('ETH_MAC2: ' + self.config.Get('ETH_MAC2')) 
	#self.log.PrintNoTime('ETH_MAC3: ' + self.config.Get('ETH_MAC3')) 
	#self.log.PrintNoTime('SAS_EXP : ' + self.config.Get('WWW_SAS_Exp')) 
	#self.log.PrintNoTime('SAS_Ctl : ' + self.config.Get('WWW_SAS_Contr')) 

    def BuildTestItems(self):
	self.testItems = []
	home_dir = self.config.Get('HOME_DIR')
	f = open(home_dir+'/TestConfig/' + self.sequence ,'r')
        lines = f.readlines()
        for line in lines:
            if line[0] == '#':
                continue
	    #print line
            #self.testItems.append(eval(line))
            #************************************
            #Date:2014-07-14
            #Author:Yong Tan
            #this following code will let the testscript  import the model automotally, we not need to update the TestEngine.py file(import the New test Item),when there are same new test item added.
            #we split the Class Name and Pramater, And Then import the Class Name(the Class Name must same as the Model Name) and to create a new object with the Class Name, and Paramter.
            #************************************
	    print line
            modelPatt="(?P<ClassName>^\w+)(?P<Parameter>\([\w\W]*\)$)"
            patternModel = re.compile(modelPatt)
            m = patternModel.search(line)
            className = m.group('ClassName')
            if className=="GetBarcode":
                className="FFGetUnitInfo"
            if className=="ShopFloorQuery":
                continue

            parameter = m.group('Parameter')
            m_import=__import__(className)
            m_testItem=getattr(m_import,className)
            #eval("m_testItem%s" %parameter)
	    print m_testItem
            self.testItems.append(eval("m_testItem%s" %parameter))

	
    def Run(self):
	self.PrepareForEachTest()
        self.errorCodeList = '' 
	flexflow_group = []
	self.config.Put('StartTime', datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
	for test_oo in self.testItems:
	    #print "=====================", self.comm.verboseFlag
	    #flexflow_tmp = ['start','duration','name','']
	    flexflow_tmp = ['','','','']
	    self.log.Print('##############################################################')

	    testItemResult=TestItem()
	    testItemResult.testName=test_oo.section_str
	    self.testResult = test_oo.Start()
	    if self.testResult[0:4] == 'FAIL':
	    	flexflow_tmp[0] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	    	flexflow_tmp[1] = str((datetime.now() - datetime.strptime(flexflow_tmp[0], ("%Y-%m-%d %H:%M:%S"))).seconds)
	    	flexflow_tmp[2] =test_oo.section_str
		flexflow_tmp[3] = self.testResult[15:20]
	    	testItemResult.testResult="FAIL"
	        self.config.Put('Sati_ErrorCode', self.testResult[-5:])
		self.log.Print("Test Fail: %s" % test_oo.section_str)
		self.config.Put('Sati_TestResult', 'Failed')
        	#self.errorCodeList = self.errorCodeList + self.testResult[-5:] + ', '
        	self.errorCodeList = self.errorCodeList + self.testResult[-5:]
		#self.ffSaveResult.Start()
		testItemResult.errorCode=self.testResult[-5:]
	        self.testItemResults.append(testItemResult)
	    	flexflow_group.append(flexflow_tmp)
	    	self.config.Put('flexflow_group', flexflow_group)
    		self.config.Put('TestResult', "Failed") 
                return self.testResult 
	    elif self.testResult == 'PASS':
    		self.config.Put('TestResult', "Passed") 
	    	testItemResult.testResult="PASS"
	    	self.testItemResults.append(testItemResult)
		pass
	    else:
    		self.config.Put('TestResult', "Failed") 
		self.log.Print("Test result unknow: %s" % test_oo.section_str)
		return 'FAIL'
	
	#recorde the test result in test log
        if self.errorCodeList == '':
	    self.config.Put('Sati_ErrorCode', '00000')
	    self.config.Put('Sati_TestResult', 'Passed')
	    #self.config.Put('Sati_TestResult', 'Passed')
	    return 'PASS'
	else:
	    return 'FAIL ErrorCode=%s' % self.errorCodeList 

    def End(self):
	print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	print self.config.Get('Sati_ErrorCode')[:-2]
	self.config.Put('EndTime', datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
	if self.config.Get('Sati_ErrorCode')[:-2] == '050':
	    pass
	elif self.config.Get('Sati_ErrorCode')[:-2] != '000':
            InvokeYesNoButton("Report Fail to Shop Floor?")
            try:
                open("REPLY_NO")
            except IOError:
                #self.shopFloorFail.Start()
	    	#f = FFSaveResult(self.config, self.log).Start()
	    	#if f[15:20] == '030':
		#    InvokeMessagePopup('FlexFlow: SaveResult Error, please check network!', 'Proceed')
		pass

	else:
	    #self.shopFloorPass.Start()
            #f = FFSaveResult(self.config, self.log).Start()
	    #if f[15:20] == '030':
	    #    InvokeMessagePopup('FlexFlow: SaveResult Error, please check network!', 'Proceed')

	    pass
	if self.config.Get('Sati_ErrorCode')[:-2] == '050':
	    pass
	elif self.config.Get('Sati_ErrorCode')[:-2] != '100' and \
	   self.config.Get('Sati_ErrorCode')[:-2] != '190' and \
	   self.config.Get('Sati_ErrorCode')[:-2] != '000':
	    self.DoPowerOFF()
	else:
	    try:
		pass
	    	#self.powerdown.TurnOff() 
	    except:
		pass
	#print "Power off"
	#self.powerdown.TurnOff() 
	#header_complete_str = 'LS BFT: '  + self.testResult 
	#self.log.AddHeader(header_complete_str)
	#to create header in test log
	header_complete_str=""
	header_complete_str+= ('Station : ' + self.hostname+"\n")
	header_complete_str+= ('Date    : ' + self.testDate+"\n") 
	header_complete_str+= (('Version : ' + self.config.Get('Version'))+"\n") 
	header_complete_str+= ('%s SFT: %s\n' %(self.dut_name, self.testResult)) 
	header_complete_str+="\n****************************************************************************************\n"
	for ti in self.testItemResults:
		str_testResults=ti.testName.ljust(70)+ti.testResult.rjust(10)+"\n"
		header_complete_str=header_complete_str+str_testResults
	header_complete_str +="****************************************************************************************\n"
	self.log.AddHeader_Long(header_complete_str,home_dir + '/FTLog/TMP/' + self.log_filename)
	self.log.Close()
	#self.log.Close2()
	#self.comm.close()

        moveTRIAL1 = 'mv ' + home_dir + '/FTLog/TMP/' + self.log_filename + \
                   ' ' + home_dir + '/FTLog/TRIAL/' + self.log_filename
        #moveTRIAL2 = 'mv ' + home_dir + '/FTLog/TMP/' + self.log_filename2 + \
        #           ' ' + home_dir + '/FTLog/TRIAL/' + self.log_filename2
        movePASS1 = 'mv ' + home_dir + '/FTLog/TMP/' + self.log_filename + \
                   ' ' + home_dir + '/FTLog/PASS/' + self.log_filename
        #movePASS2 = 'mv ' + home_dir + '/FTLog/TMP/' + self.log_filename2 + \
        #           ' ' + home_dir + '/FTLog/PASS/' + self.log_filename2
        moveFAIL1 = 'mv ' + home_dir + '/FTLog/TMP/' + self.log_filename + \
                   ' ' + home_dir + '/FTLog/FAIL/' + self.log_filename
        #moveFAIL2 = 'mv ' + home_dir + '/FTLog/TMP/' + self.log_filename2 + \
        #           ' ' + home_dir + '/FTLog/FAIL/' + self.log_filename2
        if self.config.Get('RUN_STATE') == 'TrialRun':
            print moveTRIAL1
            os.system(moveTRIAL1)
            #print moveTRIAL2
            #os.system(moveTRIAL2)
        elif self.testResult == 'PASS':
            print movePASS1
            os.system(movePASS1)
            #print movePASS2
            #os.system(movePASS2)
        elif self.testResult[0:4] == 'FAIL':
            print moveFAIL1
            os.system(moveFAIL1)
            #print moveFAIL2
            #os.system(moveFAIL2)

    def DoPowerOFF(self):
        InvokeYesNoButton("Click YES to start shutting down SATI")
        try:
            open("REPLY_NO")
        except IOError:
            self.powerdown.TurnOff()
        else:
            pass


if __name__ == '__main__':
    home_dir = os.environ['FT']
    config = Configure()
    #to read the station config file
    stationcfg=Configure()
    stationcfg.Load(home_dir + '/TestConfig/station.cfg')
    ScanBarCode(config)
    #GetBarcode(config).Start()
    #FFGetUnitInfo(config, eventManager, log, comm)
    #FFGetUnitInfo(config,None,None,None).Start()
    #print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    #print config.Get("CanisterPN")
    #print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    if sys.argv[1] == "SKU_Auto":
	sku_name = config.Get("CanisterPN") + ".sku"
    else:
	sku_name = sys.argv[1]
    print sku_name
    #InvokeMessagePopup("Turn Power ON to Start Badger System Test!", \
    #		'Proceed', True)	
    config.Load(home_dir + '/TestConfig/' + sku_name)
    #config.Put('DUT_Name', 'LS')
    config.Put('HOME_DIR', home_dir)
    print home_dir
   #*********************************
    #Date:2014-07-14
    #Author:Yong Tan
    #We will not load the port information form sku file. inorder to easy contorl the code, we make anoter station.cfg file to recorde the staiton iformation.one station will share one station.cfg. and station.cfg will not control by git.because every sation test program are same except the port information.
    #*********************************
    serialPort=stationcfg.Get('port')
    config.Put('port',serialPort)
    serialPort_UUT=stationcfg.Get('uut_port')
    config.Put('uut_port',serialPort_UUT)
    serialPort_Golden=stationcfg.Get('gold_port')
    config.Put('gold_port',serialPort_Golden)
    testMain = TestEngine(config, sku_name)
    result = testMain.Run()
    if result[0:4] == 'FAIL':
        InvokeMessagePopup(result, 'Exit',True)
    	testMain.End()
        #raw_input("Press any key to proceed!")
    elif result == 'PASS':
    	testMain.End()
        InvokeMessagePopup("Test Pass!!", 'Exit', True)
    else:
        print "Shouldn't reach here"
        raw_input() 
