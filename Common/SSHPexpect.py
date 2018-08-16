#!/usr/bin/env python
#-*-coding:utf-8-*-
# date:2016-6-21
# author:root

from EventManager import *
from Configure import *
from Log import *
import pexpect
import optparse
from Comm import *


class SSHPexpect(Comm):
    def __init_(self,config,log,eventManager):
	Comm.__init__(self, config, log,eventManager)
	self.status="CLOSED"
    def connect(self,timeout):
	username= self.config.Get("username")
	password= self.config.Get("password")
	ipaddress= self.config.Get("ipaddress")
	self.child = pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' %(username,ipaddress), timeout=timeout)
	self.child.expect('password:')
	self.child.sendline(password)
	self.child.expect('ROOT>')
    def SendReturn(self, cmdAsciiStr):
	if self.status=="CLOSED":
		self.connect(5)
		self.status="OPEN"
	self.log.Print("ROOT> %s" %cmdAsciiStr+"\n")
	print "ROOT> %s" %cmdAsciiStr
	self.child.sendline(cmdAsciiStr)

    def setTimeout(self,timeout):
	print "will set timeout to %s s" %timeout
	if self.status=="OPEN":
	    self.close()
	self.connect(timeout)

    def RecvTerminatedBy(self, *prompt_ptr):
	self.child.expect('ROOT>')
	print self.child.before
	self.log.PrintNoTimeWithoutReturn(self.child.before)
    def close(self):
        pass
	


if __name__=="__main__":
    home_dir = os.environ['FT']	    
    config = Configure(home_dir + '/FTConfig.txt')
    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    sshtest = SSHPexpect(config, log, eventManager)
    sshtest.SendReturn('lspci -vvn')
    sshtest.RecvTerminatedBy()
    sshtest.setTimeout(60)
    sshtest.SendReturn('lspci -vvn')
    sshtest.RecvTerminatedBy()
    sshtest.SendReturn('cd ..')
    sshtest.RecvTerminatedBy()
    sshtest.SendReturn('pwd')
    sshtest.RecvTerminatedBy()


