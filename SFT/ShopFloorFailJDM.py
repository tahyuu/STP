#!/usr/bin/env python

from InvokeMessagePopup import *
from InvokeYesNoButtonPicture import *
from Configure import *
from WaitingTimer import WaitingTimer
from optparse import OptionParser
import pexpect
import time
import re

class Error(Exception):
    pass

class ShopFloorFail():
    section_str = "Section: Shop Floor Fail Report Back"
    def __init__(self, config):
    #def __init__(self, config, eventManager, log, comm):
	#TestBase.__init__(self, config, eventManager, log, comm)
	self.config = config
	self.patternReturn = r'echo.+(?P<value>\d).+'
	self.pReturn = re.compile(self.patternReturn, re.DOTALL)

    def Connect(self):
	self.child = pexpect.spawn('ssh root@192.168.5.210', timeout=60)
	self.child.expect('cisuts:~ #')
	print self.child.before

    def Start(self):
	self.Connect()
	#InvokeMessagePopup('Operator -> Plug Ethernet Cable into Badger', \
	#		   'Proceed', self.graphic_mode)
	#WaitingTimer(5, self.graphic_mode)
	#self.comm.setTimeout(240)
        try:
	    self.QueryStatus()
        except Error, error:
            errCode, errMsg = error
            return 'FAIL ErrorCode=%s' % errCode
        except Exception, exception:
            #self.log.Print(exception)
            print exception
            #return 'FAIL ErrorCode=%s' % self.errCode['Others_Fail']
            return 'FAIL ErrorCode=%s' % '97099'
        else:
	    return 'PASS'

    def QueryStatus(self):
	promptStr = 'tin]#'
	sn = self.config.Get('PcbaSN')
	self.child.sendline('ssh stars@stars')
        self.child.expect(promptStr)
	print self.child.before
	self.child.sendline('pwd')
	self.child.expect(promptStr)
	print self.child.before 
	self.child.sendline('cd SFC')
	self.child.expect(promptStr)
	print self.child.before 
	self.child.sendline('cd BFT-JDM')
	self.child.expect(promptStr)
	print self.child.before 
	self.child.sendline('./StarsStdIntr F ' + sn)
	self.child.expect("Do you want to retest(Y/N)?")
        print self.child.before 
	self.child.sendline('N')
	self.child.expect(promptStr)
	print self.child.before
	self.child.sendline('echo $?')
	self.child.expect(promptStr)
	result = self.child.before
	print result
	result2 = result.split('\r\n')
	
	self.child.sendline('exit')
	self.child.expect('cisuts:~ #')
	print self.child.before
	self.child.close()
	#m = self.pReturn.search(result)
	#if m != None:
	#    print 'return value = ', m.group('value')
	if result2[1] != '0':
	    raise Error('97010', 'Report_Fail')

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    parser.add_option("-s", "--serial_number", \
                      action="store", \
                      dest="serialNumber", \
                      default="RCS0976428G00BM", \
                      help="serialNumber specifies the UUT SN")
    (options, args) = parser.parse_args()

    home_dir = os.environ['SATI_FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('SATI_II_SN', options.serialNumber)
    config.Put('PcbaSN', options.serialNumber)

    test = ShopFloorFail(config)
    result = test.Start()
    print result
