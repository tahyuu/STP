#!/usr/bin/env python
import sys
import os
import subprocess
from datetime import datetime
from InvokeMessagePopup import *
from InvokeYesNoButton import *
#from PowerControl import *
#from RelayControl import *
#from FtpUpload import *
from ScanBarCode import *
from Log import *
from EventManager import *
from Comm232 import * 


class TestEngine:
    def __init__(self, config, sku):
	self.config = config
	self.sequence = self.config.Get('TestSequence')
	self.log = Log()
        self.eventManager = EventManager()
	port = self.config.Get('port')
        self.comm = Comm232(self.config, self.log, self.eventManager, port)
	#self.comm.setTimeout(1)
	self.PrepareForInit()
	self.BuildTestItems()
	#self.powercontrol = PowerControl(self.config)
	#RelayControl(self.config).Set('Fan','ON')

    def PrepareForInit(self):
	cmdStr = '/bin/hostname'
        lsopenfile = subprocess.Popen(cmdStr, shell=True, \
                                      stdout=subprocess.PIPE, \
                                      stderr=subprocess.PIPE)
        lsopenfile.wait()
        self.hostname = lsopenfile.communicate()[0].split()[0]
	
        self.log_filename = self.config.Get('PcbaSN') + '-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
        #self.log_filename2 = self.config.Get('PcbaSN') + '-' + datetime.now().strftime("%Y%m%d%H%M%S") + '-boot.log'
	#self.config.Put('BootLogFileName', self.log_filename2)
	print self.log_filename
	#print self.log_filename2
        self.log.Open(self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename)
        #self.log.Open2(self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename2)
        self.log.PrintNoTime('                                ')
        self.log.PrintNoTime('                                ')
	self.log.PrintNoTime('Station: ' + self.hostname)
	self.config.Put('StartTime', datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
	self.log.PrintNoTime('Date   : ' + self.config.Get('StartTime')) 
	self.log.PrintNoTime('Version: ' + self.config.Get('Version')) 
        self.log.PrintNoTime('                                ')

    def BuildTestItems(self):
	self.testItems = []
	
	if self.config.Get('FlexFlow_Status') == 'On':
	    from FFGetUnitInfo import *
	    self.testItems.append(eval('FFGetUnitInfo(self.config, self.log)'))

	f = open(self.config.Get('HOME_DIR') + '/TestConfig/' + self.sequence ,'r')
        lines = f.readlines()
        for index,line in enumerate(lines):
	    print index, line
            if line[0] == '#':
                continue
	    item = line[:line.find('(')]
	    cmdstr = 'from '+ item + ' import *'
	    exec cmdstr
            self.testItems.append(eval(line))

    def Run(self):
	self.testResult = ''
        errorCodeList = '' 
	flexflow_group = []

	for index, test_oo in enumerate(self.testItems):
	    flexflow_tmp = ['start','duration','name','']
	    flexflow_tmp[0] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	    flexflow_tmp[2] = test_oo.__class__.__name__
	    self.log.Print('##############################################################')
            self.testResult = test_oo.Start()
	    self.config.Put('EndTime', datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
	    flexflow_tmp[1] = str(datetime.now() - datetime.strptime(flexflow_tmp[0], ("%Y-%m-%d %H:%M:%S"))).split('.')[0]
	    if self.testResult[0:4] == 'FAIL':
		flexflow_tmp[3] = self.testResult[15:20] #ErrorCode
	    if index == 0:
		pass
	    else:
	    	flexflow_group.append(flexflow_tmp)
	    self.config.Put('flexflow_group', flexflow_group)
	    print self.config.Get('flexflow_group'), type(self.config.Get('flexflow_group'))

	    if self.testResult[0:4] == 'FAIL':
		self.config.Put('Zuari_TestResult', 'FAIL')
		# FAIL ErrorCode=40014: CPU_ID_Fail
		self.config.Put('Zuari_ErrorCode', self.testResult[15:20])
        	#errorCodeList = errorCodeList + self.testResult[15:20] + ', '
        	errorCodeList = errorCodeList + self.testResult[15:20]
		self.log.Print("Tester => Test Fail: %s" % test_oo.section_str)
                return self.testResult 
	    elif self.testResult == 'PASS':
		pass
	    else:
		self.log.Print("Tester => Test Result Unknow: %s" % test_oo.section_str)
		return 'FAIL'
	self.config.Put('Zuari_TestResult', 'PASS')
	self.config.Put('Zuari_ErrorCode', '00000')
	return 'PASS'

    def End(self):
	self.log.Print('##############################################################')

	if self.config.Get('FlexFlow_Status') == 'On':
	    from FFSaveResult import *
	    if self.config.Get('Zuari_ErrorCode')[:-2] == '020':
            	InvokeMessagePopup('FlexFlow: GetUnitInfo Error, please check process!', 'Proceed')
	    else:		
	    	f = FFSaveResult(self.config, self.log).Start()
	    	if f[15:20] == '030':
		    InvokeMessagePopup('FlexFlow: SaveResult Error, please check network!', 'Proceed')
            
	print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
	print self.testResult
	print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

	header_complete_str = 'Zuari SFT: '  + self.testResult 
	self.log.AddHeader(header_complete_str)
	#self.log.Close()
	#self.log.Close2()
	#self.comm.close()

	if self.config.Get('FlexFlow_Status') == 'On':
	    ftpLocalPath = self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename
	    ftpRemotePath = 'Zuari/SFT/ROCDIB/' + self.log_filename
	    FtpUpload(ftpLocalPath,ftpRemotePath)

        moveTRIAL1 = 'mv ' + self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename + \
                   ' ' + self.config.Get('HOME_DIR') + '/SFTLog/TRIAL/' + self.log_filename
        #moveTRIAL2 = 'mv ' + self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename2 + \
        #           ' ' + self.config.Get('HOME_DIR') + '/SFTLog/TRIAL/' + self.log_filename2
        movePASS1 = 'mv ' + self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename + \
                   ' ' + self.config.Get('HOME_DIR') + '/SFTLog/PASS/' + self.log_filename
        #movePASS2 = 'mv ' + self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename2 + \
        #           ' ' + self.config.Get('HOME_DIR') + '/SFTLog/PASS/' + self.log_filename2
        moveFAIL1 = 'mv ' + self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename + \
                   ' ' + self.config.Get('HOME_DIR') + '/SFTLog/FAIL/' + self.log_filename
        #moveFAIL2 = 'mv ' + self.config.Get('HOME_DIR') + '/SFTLog/TMP/' + self.log_filename2 + \
        #           ' ' + self.config.Get('HOME_DIR') + '/SFTLog/FAIL/' + self.log_filename2

        if self.config.Get('RUN_STATE') == 'TrialRun':
            print moveTRIAL1
            os.system(moveTRIAL1)
            #print moveTRIAL2
            #os.system(moveTRIAL2)
	    logpath = self.config.Get('HOME_DIR') + '/SFTLog/TRAIL/' + datetime.now().strftime("%Y-%m-%d")+'/'
	    if not os.path.exists(logpath):
	 	os.system('mkdir '+logpath)
	    cmdstr = 'cp ' + self.config.Get('HOME_DIR') + '/SFTLog/TRAIL/' + self.log_filename + ' ' + logpath + self.log_filename
	    print cmdstr
	    os.system(cmdstr)
	    #cmdstr = 'cp ' + self.config.Get('HOME_DIR') + '/SFTLog/TRAIL/' + self.log_filename2 + ' ' + logpath + self.log_filename2
	    #print cmdstr
	    #os.system(cmdstr)
        elif self.testResult == 'PASS':
            print movePASS1
            os.system(movePASS1)
            #print movePASS2
            #os.system(movePASS2)
	    logpath = self.config.Get('HOME_DIR') + '/SFTLog/PASS/' + datetime.now().strftime("%Y-%m-%d")+'/'
	    if not os.path.exists(logpath):
	 	os.system('mkdir '+logpath)
	    cmdstr = 'cp ' + self.config.Get('HOME_DIR') + '/SFTLog/PASS/' + self.log_filename + ' ' + logpath + self.log_filename
	    print cmdstr
	    os.system(cmdstr)
	    #cmdstr = 'cp ' + self.config.Get('HOME_DIR') + '/SFTLog/PASS/' + self.log_filename2 + ' ' + logpath + self.log_filename2
	    #print cmdstr
	    #os.system(cmdstr)
        elif self.testResult[0:4] == 'FAIL':
            print moveFAIL1
            os.system(moveFAIL1)
            #print moveFAIL2
            #os.system(moveFAIL2)
	    logpath = self.config.Get('HOME_DIR') + '/SFTLog/FAIL/' + datetime.now().strftime("%Y-%m-%d")+'/'
	    if not os.path.exists(logpath):
	 	os.system('mkdir '+logpath)
	    cmdstr = 'cp ' + self.config.Get('HOME_DIR') + '/SFTLog/FAIL/' + self.log_filename + ' ' + logpath + self.log_filename
	    print cmdstr
	    os.system(cmdstr)
	    #cmdstr = 'cp ' + self.config.Get('HOME_DIR') + '/SFTLog/FAIL/' + self.log_filename2 + ' ' + logpath + self.log_filename2
	    #print cmdstr
	    #os.system(cmdstr)

        if self.config.Get('Zuari_ErrorCode')[:-2] == '020':
	    self.comm.close()
        elif self.config.Get('Zuari_ErrorCode')[:-2] == '030':
            self.comm.SendReturn('halt')
            self.comm.RecvTerminatedBy('Power down')
	    self.comm.close()
	    InvokeMessagePopup('\xe5\x85\xb3\xe9\x97\xad\xe7\x94\xb5\xe6\xba\x90\nTurn off Power', '\xe7\xbb\xa7\xe7\xbb\xad\nProceed')
            #self.powercontrol.PowerOff()
        elif self.config.Get('Zuari_ErrorCode')[:-2] == '100' or self.config.Get('Zuari_ErrorCode')[:-2] == '110':
	    self.comm.close()
	    InvokeMessagePopup('\xe5\x85\xb3\xe9\x97\xad\xe7\x94\xb5\xe6\xba\x90\nTurn off Power', '\xe7\xbb\xa7\xe7\xbb\xad\nProceed')
	    #self.powercontrol.PowerOff()    
        else:
            InvokeYesNoButton("\xe7\x82\xb9\xe5\x87\xbbYES\xe5\x85\xb3\xe9\x97\xad\xe7\x94\xb5\xe6\xba\x90\nClick YES to start shutting down Zuari")
            try:
            	open("REPLY_NO")
            except IOError:
            	os.system('rm -rf REPLY_YES')
            	#self.comm.SendReturn('halt')
            	self.comm.SendReturn('shutdown now')
            	self.comm.RecvTerminatedBy('Power down')
		self.comm.close()
		InvokeMessagePopup('\xe5\x85\xb3\xe9\x97\xad\xe7\x94\xb5\xe6\xba\x90\nTurn off Power', '\xe7\xbb\xa7\xe7\xbb\xad\nProceed')
	    	#self.powercontrol.PowerOff()    
            else:
            	os.system('rm -rf REPLY_NO')
		self.comm.close()
            	#InvokeMessagePopup("\xe4\xb8\x8d\xe8\xa6\x81\xe5\x85\xb3\xe9\x97\xad\xe6\xad\xa4\xe7\xaa\x97\xe5\x8f\xa3\xef\xbc\x8c\xe8\xaf\xb7\xe6\x89\x93\xe5\xbc\x80\xe5\x8f\xa6\xe4\xb8\x80\xe7\xbb\x88\xe7\xab\xaf\xe8\xbf\x9b\xe8\xa1\x8c\xe8\xb0\x83\xe8\xaf\x95\nDon't close this window, please open another terminal to debug", 'Exit', True)
	    	#self.powercontrol.PowerOff()

	self.log.Close()
	#self.log.Close2()
 

if __name__ == '__main__':
    home_dir = os.environ['FT']
    config = Configure()
    config.Put('HOME_DIR', home_dir)

    if len( sys.argv ) == 1:
	sku_name = "silk_road_s1.sku"
    elif len( sys.argv ) == 2:
	sku_name = sys.argv[1]
    else:
	sys.exit('Usage: TestEngine.py sku_name')

    config.Load(home_dir + '/TestConfig/' + sku_name)
    ScanBarCode(config)
    InvokeMessagePopup("'\xe8\xaf\xb7\xe7\xa1\xae\xe4\xbf\x9d\xe6\x89\x80\xe6\x9c\x89\xe7\xbb\x84\xe4\xbb\xb6\xe5\xae\x89\xe8\xa3\x85\xe5\x88\xb0\xe4\xbd\x8d\nPlease make sure all components connected properly", '\xe7\xbb\xa7\xe7\xbb\xad\nProceed')
    testMain = TestEngine(config, sku_name)
    result = testMain.Run()
    if result[0:4] == 'FAIL':
        InvokeMessagePopup(result, 'Exit', True)
    elif result == 'PASS':
        InvokeMessagePopup("Test Pass!!", 'Exit', True)
    else:
        print "Shouldn't reach here"
    testMain.End()
