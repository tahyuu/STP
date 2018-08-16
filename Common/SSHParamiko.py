#!/usr/bin/python 
from EventManager import *
from Configure import *
from Log import *
import paramiko
import threading
from Comm import *

class SSHParamiko(Comm):
    def __init_(self,config,log,eventManager):
	Comm.__init__(self, config, log,eventManager)
	self.status="CLOSED"
	self.connect(5)
	#pass
    def connect(self,timeout):
	try:
	    username= self.config.Get("username")
	    password= self.config.Get("password")
	    ipaddress= self.config.Get("ipaddress")
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(ipaddress,22,username,password,timeout=timeout)
	    self.status="OPEN"
        except :
            print '\tError\n'
    def SendReturn(self, cmdAsciiStr):
	self.command=cmdAsciiStr
        print "ROOT> %s" %cmdAsciiStr
	self.log.Print("ROOT> %s" %cmdAsciiStr)
	#if True:
    def RecvTerminatedBy(self, *prompt_ptr):
	#if True:
        try:
	    if self.status=="CLOSED" or (not self.ssh):
		self.connect(5)
            stdin, stdout, stderr = self.ssh.exec_command(self.command)
            out = stdout.readlines()
            for o in out:
	    	self.log.PrintNoTimeWithoutReturn(o)
                print o,
	    pass
        except :
            print '\tError\n'
    def setTimeout(self,timeout):
	print "will set timeout to %s s" %timeout
	if self.status=="OPEN":
	    self.close()
	self.connect(timeout)
    def close(self):
        self.ssh.close()
	self.status="CLOSED"
    
if __name__=='__main__':

    home_dir = os.environ['FT']	    
    config = Configure(home_dir + '/FTConfig.txt')
    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    sshtest = SSHParamiko(config, log, eventManager)
    sshtest.SendReturn('lspci -vvn')
    sshtest.RecvTerminatedBy()
    sshtest.close()
    sshtest.SendReturn('pwd')
    sshtest.RecvTerminatedBy()
    sshtest.setTimeout(10)
    sshtest.SendReturn('cd ..')
    sshtest.RecvTerminatedBy()
    sshtest.close()
    sshtest.SendReturn('pwd')
    sshtest.RecvTerminatedBy()
