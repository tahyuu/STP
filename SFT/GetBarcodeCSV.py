#!/usr/bin/env python
import csv
from TestBase import *
from Configure import *
from Log import *
import os,sys
import pexpect
import re
class GetBarcodeCSV(TestBase):
        section_str = "Section: Get Barcodes from ShopFloor"
        def __init__(self, config, eventManager, log, comm):
		TestBase.__init__(self, config, eventManager, log, comm)
		self.config = config
		self.log =log
		home_str = os.environ['HOME']
		self.map={
		   'PN':'1',\
		   'SN':'2',\
		   'CANISTER':'3',\
		   'BMC_MAC1':'4',\
		   'BMC_MAC2':'5',\
		   'ETH_MAC1':'6',\
		   'ETH_MAC2':'7',\
		   'ETH_MAC3':'8',\
		   'SAS_EXP_MAC':'9',\
		   'SAS_EXP_WWN':'10',\
		   'SAS_CONTR_WWN':'11',\
			}
		self.fileName="Laguna_Seca_SN_MAC_WWN_Matrix_DVT_0107.csv"
		self.findRow=[]
	def Start(self):
	    try:
		self.log.Print(GetBarcodeCSV.section_str)
		self.GetUUT()
	    except Error, error:
            	errCode, errMsg = error
            	self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            	return 'FAIL ErrorCode=%s' % errCode
            else:
           	self.log.Print("Tester => OK: GetBarcode OK")
            	return 'PASS'

	
	def GetUUT(self):
        	SN = self.config.Get('LS_Canister_SN')
		self.findRow=[]
		with open(self.fileName, 'rb') as csvfile:
			reader= csv.reader(csvfile, delimiter=',', quotechar='|')
			for row in reader:
				print row
				print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
				print SN
				print row[3]
				print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
				if  len(row)>2 and row[3]==SN:
					self.findRow=row
					break
		if self.findRow:
			print self.findRow
			self.config.Put("CanisterSN",self.findRow[int(self.map["CANISTER"])])
			self.config.Put("PcbaPN",self.findRow[int(self.map["PN"])])
			self.config.Put("PcbaSN",self.findRow[int(self.map["SN"])])
			self.config.Put("BmcMAC1",self.findRow[int(self.map["BMC_MAC1"])])
			self.config.Put("BmcMAC2",self.findRow[int(self.map["BMC_MAC2"])])
			self.config.Put("EthMAC1",self.findRow[int(self.map["ETH_MAC1"])])
			self.config.Put("EthMAC2",self.findRow[int(self.map["ETH_MAC2"])])
			self.config.Put("EthMAC3",self.findRow[int(self.map["ETH_MAC3"])])
			self.config.Put("SasCtlWWN",self.findRow[int(self.map["SAS_CONTR_WWN"])])
			self.config.Put("SasExpWWN",self.findRow[int(self.map["SAS_EXP_WWN"])])
			self.config.Put("SasExpMAC",self.findRow[int(self.map["SAS_EXP_MAC"])])
			if self.config.Get('CanisterPN')=="No such key":
				self.config.Put("CanisterPN",'1003612-02')
		        self.log.PrintNoTime('      PCBA SN: ' + \
		                self.config.Get('PcbaSN'))
		        self.log.PrintNoTime('      PCBA PN: ' + \
		                self.config.Get('PcbaPN'))
		        self.log.PrintNoTime('  Canister SN: ' + \
		                self.config.Get('CanisterSN'))
			#There is no Canister PN in Shop Floor
		        self.log.PrintNoTime('  Canister PN: ' + \
		                self.config.Get('CanisterPN'))
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
	
		else:
			print "Can't find the SN:%s in %s" %(SN,fileName)
	def CheckBarcode(self,barDic):
		errorFlag=False
		if len(barDic)!=10:
			errorFlag=True
			print "Shop floor get Barcode must >10 include SN,PN,BMA_MAC1,BMC_MAC1................SAS_CONTR_WWN"
			return
		if self.findRow[int(self.map["SN"])]!=barDic["SN"]:
			errorFlag=True
			print "Shop floor get Barcode SN:%s ar not equal to SN:%s in csv file" %(barDic["SN"],self.findRow[int(self.map["SN"])])
		if self.findRow[int(self.map["PN"])]!=barDic["PN"]:
			errorFlag=True
			print "Shop floor get Barcode PN:%s ar not equal to PN:%s in csv file" %(barDic["PN"],self.findRow[int(self.map["PN"])])
		if self.findRow[int(self.map["BMC_MAC1"])]!=barDic["BMC_MAC1"]:
			errorFlag=True
			print "Shop floor get Barcode BMC_MAC1:%s ar not equal to BMC_MAC1:%s in csv file" %(barDic["BMC_MAC1"],self.findRow[int(self.map["BMC_MAC1"])])
		if self.findRow[int(self.map["BMC_MAC2"])]!=barDic["BMC_MAC2"]:
			errorFlag=True
			print "Shop floor get Barcode BMC_MAC2:%s ar not equal to BMC_MAC2:%s in csv file" %(barDic["BMC_MAC2"],self.findRow[int(self.map["BMC_MAC2"])])
		if self.findRow[int(self.map["ETH_MAC1"])]!=barDic["ETH_MAC1"]:
			errorFlag=True
			print "Shop floor get Barcode ETH_MAC1:%s ar not equal to ETH_MAC1:%s in csv file" %(barDic["ETH_MAC1"],self.findRow[int(self.map["ETH_MAC1"])])
		if self.findRow[int(self.map["ETH_MAC2"])]!=barDic["ETH_MAC2"]:
			errorFlag=True
			print "Shop floor get Barcode ETH_MAC2:%s ar not equal to ETH_MAC1:%s in csv file" %(barDic["ETH_MAC1"],self.findRow[int(self.map["ETH_MAC1"])])
		if self.findRow[int(self.map["ETH_MAC3"])]!=barDic["ETH_MAC3"]:
			errorFlag=True
			print "Shop floor get Barcode ETH_MAC3:%s ar not equal to ETH_MAC3:%s in csv file" %(barDic["ETH_MAC3"],self.findRow[int(self.map["ETH_MAC3"])])
		if self.findRow[int(self.map["SAS_EXP_MAC"])]!=barDic["SAS_EXP_MAC"]:
			errorFlag=True
			print "Shop floor get Barcode :%s ar not equal to SAS_EXP_MAC:%s in csv file" %(barDic["SAS_EXP_MAC"],self.findRow[int(self.map["SAS_EXP_MAC"])])
		if self.findRow[int(self.map["SAS_EXP_WWN"])]!=barDic["SAS_EXP_WWN"]:
			errorFlag=True
			print "Shop floor get Barcode :%s ar not equal to SAS_EXP_WWN:%s in csv file" %(barDic["SAS_EXP_WWN"],self.findRow[int(self.map["SAS_EXP_WWN"])])
		if self.findRow[int(self.map["SAS_CONTR_WWN"])]!=barDic["SAS_CONTR_WWN"]:
			errorFlag=True
			print "Shop floor get Barcode :%s ar not equal to SAS_CONTR_WWN:%s in csv file" %(barDic["SAS_CONTR_WWN"],self.findRow[int(self.map["SAS_CONTR_WWN"])])
		if errorFlag:
			print "Error Barcode Check Fail"

		

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RMS1003612G006Y", \
                      help="serialNumber specifies the UUT SN")
                      # 00 -> RCS0976428G00X0
    (options, args) = parser.parse_args()
    home_dir = os.environ['SATI_FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    serial_port = config.Get('port')

    eventManager = EventManager()

    #config.Put('CanisterSN', options.serialNumber)
    config.Put('LS_Canister_SN', options.serialNumber)
    log = Log()
    log.Open('test.log')
    comm = None
    #comm = Comm232(config, log, eventManager, serial_port)
    test = GetBarcodeCSV(config, eventManager, log, comm)
    result = test.Start()
    #getbar.CheckBarcode(barCodeDic)
		
