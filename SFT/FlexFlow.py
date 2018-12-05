#!/usr/bin/env python

from suds.client import Client
from suds.xsd.doctor import ImportDoctor,Import
from xml.etree import ElementTree as ET  
from optparse import OptionParser
import ConfigParser	

class FlexFlow:
    def __init__(self):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read("flexflow.ini")
        self.Element_Name       =self.cf.get("FlexFlow", "Element_Name")
        self.Element_Key_Name   =self.cf.get("FlexFlow", "Element_Key_Name")
        self.Element_Value_Name =self.cf.get("FlexFlow", "Element_Value_Name")
        self.flexFlowUrl= self.cf.get("FlexFlow", "FlexFlowUrl")
        self.stationName=self.cf.get("FlexFlow", "StationName")
        self.map_str = self.cf.get("FlexFlow", "datas_map")
        self.datas_map = eval(self.map_str)
        self.serilNumber="RMS1017521G0ML8"
        self.strRequestFormat="<GetUnitInfo xmlns='urn:GetUnitInfo-schema' SerialNumber='%s' />"
        self.dict={}
        self.config={}
    def GetUnitInfo(self,serialNumber):
        self.serialNumber=serialNumber
        strRequest=self.strRequestFormat %self.serilNumber
        client = Client(self.flexFlowUrl)
        results = client.service.GetUnitInfo(strRequest,"",self.stationName,"")
        if results[0]!="0":
            print results[1]
	    return
        self.reply_body = client.service.GetUnitInfo(strRequest,"",self.stationName,"")[1]
	self.reply_body = '''<UnitInfo><UnitData><Name>StationID</Name><Value>SGT-BFT</Value><UserID></UserID></UnitData><UnitData><Name>MAC1</Name><Value>0050CC35A2CE</Value><UserID></UserID></UnitData><UnitData><Name>MAC2</Name><Value>0050CC35A2CF</Value><UserID></UserID></UnitData><UnitData><Name>MAC3</Name><Value>0050CC35A2D0</Value><UserID></UserID></UnitData><UnitData><Name>MAC4</Name><Value>0050CC35A2D1</Value><UserID></UserID></UnitData><UnitData><Name>MAC5</Name><Value>0050CC35A2D2</Value><UserID></UserID></UnitData><UnitData><Name>MAC6</Name><Value>0050CC35A2D3</Value><UserID></UserID></UnitData><UnitData><Name>WWN1</Name><Value>50050CC1201B3300</Value><UserID></UserID></UnitData><UnitData><Name>WWN2</Name><Value>50050CC1201B3332</Value><UserID></UserID></UnitData><UnitData><Name>GUID1</Name><Value>Value_cannot_be_calculated</Value><UserID></UserID></UnitData><UnitData><Name>GUID2</Name><Value>Value_cannot_be_calculated</Value><UserID></UserID></UnitData><UnitData><Name>SerialNumber</Name><Value>MBS1003610G0ML8</Value><UserID></UserID></UnitData><UnitData><Name>Canister_PN</Name><Value>1017521-04</Value><UserID></UserID></UnitData><UnitData><Name>DELL_PPID</Name><Value>Value_cannot_be_calculated</Value><UserID></UserID></UnitData><UnitData><Name>HP_PPID</Name><Value>Value_cannot_be_calculated</Value><UserID></UserID></UnitData><UnitData><Name>PCBA_PN</Name><Value>1003610-06</Value><UserID></UserID></UnitData><UnitData><Name>HLASN</Name><Value>RMS1017521G0ML8</Value><UserID></UserID></UnitData><UnitData><Name>MAC7</Name><Value>Value_cannot_be_calculated</Value><UserID></UserID></UnitData><UnitData><Name>MAC8</Name><Value>Value_cannot_be_calculated</Value><UserID></UserID></UnitData></UnitInfo>'''
        #print self.reply_body
	
        self.ParserXML()
        self.MapData()
    def ParserXML(self):
        Name=""
        Value=""
        xml_unitdatas= ET.fromstring(self.reply_body)
        unitdatas = xml_unitdatas.getiterator(self.Element_Name)  
        for node in unitdatas:  
            for child in node.getchildren():
       	        if child.tag==self.Element_Key_Name:
       	            Name=child.text
                if child.tag==self.Element_Value_Name:
                    Value=child.text
                if Name:
                    self.dict[Name]=Value
        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        print "Before MapData"
        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        print self.dict
        print 
        print 

    def MapData(self):
        for key in self.datas_map.keys():
                if key:
                        Value=self.dict[key]
                if Value:
                        self.config[self.datas_map[key]]=Value
        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        print "After MapData"
        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        print self.config
  

if __name__=="__main__":
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RMS1017521G0ML8", \
                      help="serialNumber specifies the UUT SN")
    (options, args) = parser.parse_args()
    flexflow=FlexFlow()
    flexflow.GetUnitInfo(options.serialNumber)
