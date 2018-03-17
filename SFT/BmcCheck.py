#!/usr/bin/env python
from TestBase import *
class BmcCheck(TestBase):
    section_str = "Section: BMC Version Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.BmcCheck= \
		r'(?P<Version>\d+[.]\d{2})'
	self.pattern = self.BmcCheck
	self.p = re.compile(self.pattern)
	self.version = config.Get('BMC_Version')
    def Start(self):
	self.log.Print(BmcCheck.section_str)
	try:
            self.CheckVersion()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: BMC Version Check")
            return 'PASS'

    def CheckVersion(self):
	#self.comm.SendReturn('service ipmi start')
	#line = self.comm.RecvTerminatedBy()
	self.comm.SendReturn('ipmitool mc info')
	line = self.comm.RecvTerminatedBy()
	m = self.p.search(line)
        errCodeStr = 'Version_Fail'
        if m == None:
            raise Error(self.errCode[errCodeStr], errCodeStr)
	version = m.group('Version')
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	print version
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	if version != self.version: 
	    self.log.Print("Version number %s is not matched to %s" % \
			(self.version, version))
            raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.log.Print("Version number %s is matched to %s" % \
			(self.version, version))
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])",
                          version="0.1")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
	parse.error("wrong number of arguments")
	sys.exit(1)
    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = BmcCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
