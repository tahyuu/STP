#!/usr/bin/env python

from TestBase import *
from WaitingTimer import WaitingTimer
from InvokeMessagePopup import *

class PowerDown(TestBase):
    section_str = "Section: Power Down"
    def __init__(self, config, eventManager, log, comm, num_of_cycle, \
		 graphic_mode):
	TestBase.__init__(self, config, eventManager, log, comm)
	self.num_of_cycle = int(num_of_cycle)
	self.graphic_mode = graphic_mode
	#self.comm.setTimeout(120)
	#self.comm.SetVerbose()

    def TurnOff(self): 
	self.comm.SendReturn('halt')
	#self.comm.RecvTerminatedBy('Power down')
	self.comm.RecvTerminatedBy('Halting')
	#self.comm.SendReturn('reboot')
	time.sleep(5)
	InvokeMessagePopup('Turn off Power', 'Proceed')
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])",
                          version="0.1")
    parser.add_option("-t", "--timeout", \
                      action="store", \
                      dest="timeout", \
                      default="5", \
                      help="timeout specifies how much time to wait for \
                            Badger message")
    parser.add_option("-n", "--power_cycle_num", \
                      action="store", \
                      dest="power_cycle_num", \
                      default="2", \
                      help="power_cycle_num specifies the number of power \
                            cycle for testing")
    parser.add_option("-g", "--graph_mode", \
                      action="store", \
                      dest="graph_mode", \
                      default=True, \
                      help="graph_mode specifies the waiting time is in\
                            window or CLI")
    (options, args) = parser.parse_args()

    home_dir = os.environ['SATI_FT']
    config = Configure(home_dir + '/BFTConfig.txt')

    if len( args ) != 0:
	sys.exit("Usage: PowerDown.py [options]")

    serial_port = config.Get('port')
    num_of_cycle = options.power_cycle_num
    graphic_mode = options.graph_mode

    eventManager = EventManager()
    log = Log()
    log.Open('test.log')
    comm = Comm232(config, log, eventManager, serial_port)

    test = PowerDown(config, eventManager, log, comm, num_of_cycle, \
		      graphic_mode)
    result = test.TurnOff()
    print result
