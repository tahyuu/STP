#!/usr/bin/env python

from EventManager import *
from Configure import *
from Log import *
import os, serial, subprocess, time
from optparse import OptionParser

class Comm232(serial.Serial):
    def __init__(self, config, log, eventManager, serial_port):
	self.config = config	
	self.log = log
	self.PROMPT = self.config.Get('PROMPT')

    def SendReturn(self, cmdAsciiStr):
        self.f = subprocess.Popen(cmdAsciiStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	tmp = "Send = "+cmdAsciiStr
	print tmp
	self.log.Print(tmp)

    def RecvTerminatedBy(self, *prompt_ptr):
	if len(prompt_ptr) == 0:
	    prompt = self.PROMPT
	else:
	    prompt = prompt_ptr[0]

	print 'Rece = '
	self.log.Print("Rece = ")
	stdout = ''
	while self.f.poll() == None:
	    stdout_line = self.f.stdout.readline()
	    stdout = stdout + stdout_line
	    if stdout_line != '':
		print stdout_line,
		self.log.PrintNoTime(stdout_line.rstrip())
	else:
	    stdout_lines = self.f.stdout.read()
	    stdout = stdout + stdout_lines
	    if stdout_lines != '':
		print stdout_lines,
		self.log.PrintNoTime(stdout_lines[0:-1])

	if stdout != '':
	    return stdout
	    print stdout_lines,
	else:
	    stderr = self.f.stderr.read()
	    #if stderr != '':
	    #    print stderr
	    print stderr,
	    self.log.PrintNoTime(stderr.rstrip())
	    return stderr

    def close(self):
        pass


if __name__ == "__main__":
    home_dir = os.environ['Zuari_BFT']	    
    config = Configure(home_dir + '/BFTConfig.txt')
    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    serial_port = '/dev/ttyS0'
    Comm = Comm232(config, log, eventManager, serial_port)
    #Comm.SendReturn('dd if=/dev/urandom of=/dev/shm/TestDataIn.dat bs=1M count=500')
    #Comm.RecvTerminatedBy()
    #Comm.SendReturn('dd if=/dev/urandom of=/dev/shm/TestDataIn.dat bs=1M count=500')
    #Comm.RecvTerminatedBy()
    #Comm.SendReturn('ping -c 10 10.194.148.150')
    #print Comm.RecvTerminatedBy(),
    #Comm.SendReturn('/root/Zuari-EVT/TestConfig/passmark/burnintest/64bit/bit_cmd_line_x64')
    #print Comm.RecvTerminatedBy(),
    Comm.SendReturn('lspci -vvns 04:00.0')
    Comm.RecvTerminatedBy()
    Comm.SendReturn('lspci -vvns 04:00.0')
    Comm.RecvTerminatedBy()
    Comm.close()
    log.Close()
