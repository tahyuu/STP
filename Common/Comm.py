#!/usr/bin/env python

from EventManager import *
from Configure import *
from Log import *
import os, serial, subprocess, time
from optparse import OptionParser

class Comm():
    def __init__(self, config, log, eventManager,):
	self.config = config	
	self.log = log
	self.PROMPT = self.config.Get('PROMPT')
	self.ssh=None
	self.status="CLOSED"

    def SendReturn(self, cmdAsciiStr):
	pass

    def RecvTerminatedBy(self, *prompt_ptr):
	pass

    def close(self):
        pass


if __name__ == "__main__":
    pass
