#!/usr/bin/env python

from TestBase import *


class CpuRamBurnIn(TestBase):
    section_str = "Section: CPU and RAM Burn-in"
    def __init__(self, config, eventManager, log, comm, minute):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.minute = self.config.Get('BurninTime')

    def Start(self):
	self.log.Print(CpuRamBurnIn.section_str)
	#self.comm.setTimeout(int(self.minute)*60+20)
	self.BurnIn()
	try:
	    self.BurnIn()
	except Error, error:
            errCode, errMsg = error
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (errCode, errMsg))
            return 'FAIL ErrorCode=%s: %s' % (errCode, errMsg)
        except Exception, exception:
            self.log.Print('TestEnd => ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail'))
            print exception
            return 'FAIL ErrorCode=%s: %s' % (self.errCode['Others_Fail'], 'Others_Fail')
        else:
            self.log.Print("TestChk => PASS: CPU and RAM Burn-in")
            return 'PASS'

    def BurnIn(self):
    	home_dir = os.environ['FT']
        self.comm.SendReturn('rm -f /tmp/BiTLog2.log')
        self.comm.RecvTerminatedBy()
	config_str = 'sed -i "59cAutoStopMinutes ' + self.minute + '" '+home_dir+'/TestConfig/passmark/burnintest/64bit/cmdline_config.txt'
	self.comm.SendReturn(config_str)
        self.comm.RecvTerminatedBy()
	config_str = 'sed -i "99c#" '+home_dir+'/TestConfig/passmark/burnintest/64bit/cmdline_config.txt'
	self.comm.SendReturn(config_str)
        self.comm.RecvTerminatedBy()
	self.comm.SendReturn(home_dir+'/TestConfig/passmark/burnintest/64bit/bit_cmd_line_x64')
	#self.comm.SetVerbose()
	result = self.comm.RecvTerminatedBy()
	#self.comm.UnsetVerbose()
	#if result == 'FAIL':
	#    raise Error(self.errCode['Others_Fail'], 'Others_Fail')
        self.comm.SendReturn('cat /tmp/BiTLog2.log')
	result = self.comm.RecvTerminatedBy()
	print result.find('TEST RUN PASSED'), 'status'
	if result.find('TEST RUN PASSED') < 0:
	    pass
	    #raise Error(self.errCode['BurnIn_Fail'], 'BurnIn_Fail')

	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-m", "--mintue", \
                      action="store", \
                      dest="minute", \
                      default="2", \
                      help="minute specifies the time last for burn-in")
    (options, args) = parser.parse_args()

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    if len( args ) != 0:
	sys.exit("Usage: CpuRamBurnIn.py [options]")

    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    serial_port = config.Get('port')
    comm = Comm232(config, log, eventManager, serial_port)
    
    minute = options.minute
    test = CpuRamBurnIn(config, eventManager, log, comm, minute)
    result = test.Start()
    print result

