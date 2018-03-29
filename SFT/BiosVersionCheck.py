#!/usr/bin/env python

from TestBase import *
class BiosVersionCheck(TestBase):
    section_str = "Section: BIOS Version Check"
    def __init__(self, config, eventManager, log, comm):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.BiosVersionCheck = \
		r'(?P<Version>\w+[.]\w+)'
	self.pattern = self.BiosVersionCheck
	self.p = re.compile(self.pattern)
	self.version = config.Get('BIOS_Version')

    def Start(self):
	self.log.Print(BiosVersionCheck.section_str)
	try:
            self.CheckVersion()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % \
                           (errCode, errMsg))
            return 'FAIL ErrorCode=%s' % errCode
        else:
            self.log.Print("Tester => OK: BIOS Version Check")
            return 'PASS'

    def CheckVersion(self):
	self.comm.SendReturn('dmidecode -s bios-version')
	line = self.comm.RecvTerminatedBy()
	m = self.p.search(line)
        errCodeStr = 'Version_Fail'
        if m == None:
            raise Error(self.errCode[errCodeStr], errCodeStr)
	version = m.group('Version')
	if version != self.version: 
	    self.log.Print("Version number %s is not matched to %s" % \
			(self.version, version))
            raise Error(self.errCode[errCodeStr], errCodeStr)
	else:
	    self.log.Print("Version number %s is matched to %s" % \
			(self.version, version))
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
	parser.error("wrong number of arguments")
	sys.exit(1)
    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    serial_port = config.Get('port')

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = BiosVersionCheck(config, eventManager, log, comm)
    result = test.Start()
    print result
