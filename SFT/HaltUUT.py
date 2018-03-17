#!/usr/bin/env python

from TestBase import *
from WaitingTimer import WaitingTimer
from InvokeMessagePopup import *

class HaltUUT(TestBase):
    section_str = "Section: Halt UUT"
    def __init__(self, config, eventManager, log, comm, graphic_mode,currentCycle):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.currentCycle=currentCycle
	self.graphic_mode = graphic_mode

    def Start(self):
	self.log.Print(HaltUUT.section_str)
	self.TurnOff()
        return 'PASS'

    def TurnOff(self): 
	# save current test status
	self.ongoingstatus = Log()
        self.ongoingstatus.Open(self.log.filename.replace(".log","").replace("BFTLog/TMP","OngoingTest"))
	self.ongoingstatus.PrintNoTime(self.currentCycle)
	#self.comm.RecvTerminatedBy('Power down')
	#self.comm.RecvTerminatedBy('Halting')
	time.sleep(5)
	#self.comm.SendReturn('reboot')
	if self.graphic_mode:
	    InvokeMessagePopup('Turn off Power', 'Proceed')
	else:
	    raw_input('Turn off Power then Press Enter to Proceed')
	self.comm.SendReturn('init 0')
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-t", "--timeout", \
                      action="store", \
                      dest="timeout", \
                      default="30", \
                      help="timeout specifies the waiting time for boot-up")
    parser.add_option("-g", "--graph_mode", \
                      action="store", \
                      dest="graph_mode", \
                      default=True, \
                      help="graph_mode specifies message in popup window or \
                            CLI")
    (options, args) = parser.parse_args()

    home_dir = os.environ['FT']
    config = Configure(home_dir + '/BFTConfig.txt')
    config.Put('HOME_DIR',home_dir)

    if len( args ) != 0:
	sys.exit("Usage: HaltUUT.py [options]")

    serial_port = config.Get('port')
    graphic_mode = options.graph_mode

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = HaltUUT(config, eventManager, log, comm, graphic_mode,"2")
    result = test.Start()
    print result
