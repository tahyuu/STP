from Configure import *
from EventManager import *
from Log import Log
from Comm232 import Comm232 
import os
import time
import sys
from optparse import OptionParser
import re
import subprocess

class Error(Exception):
    pass

class TestBase:
    def __init__(self, config, eventManager, log, comm=None):
        self.config = config
        self.eventManager = eventManager 
        self.log = log
        if time is not None:
            self.comm = comm

        #self.errCodePath = self.config.Get('HOME_DIR') + '/SFT/ErrorCode.txt'
        self.errCodePath = os.environ['FT'] + '/SFT/ErrorCode.txt'
        self.errCode = {}
        self.BuildErrorTable()

    def BuildErrorTable(self):
        try:
            f = open(self.errCodePath, 'r')
        except IOError, exception:
            print "ErrorCode file not found", exception
            sys.exit(1)
        for l in f.readlines():
            ll = l.split('\t')
            ll2 = ll[1].split('.')
            #print l, ll
            #print ll2, self.__class__.__name__
            try:
                if ll2[0] == self.__class__.__name__:
                    self.errCode[ll2[1].strip()] = ll[0]
            except IndexError:
                pass
        #print self.errCode
        f.close()

    def __del__(self):
        #print "destructor called"
        #self.log.Close()
        #self.comm.close()
        pass

    def End(self):
        pass

    def Start(self):
        pass
