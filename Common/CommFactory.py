#!/usr/bin/python 
from SSHParamiko import *
from SSHPexpect import *
from Subprocess import *

class CommFactory():
    @staticmethod
    def CreateComm(type,config, log, eventManager):
        if type == 'SSHParamiko':
            return SSHParamiko(config, log, eventManager)
        elif type == 'SSHPexpect':
            return SSHPexpect(config, log, eventManager)
	elif type =='Subprocess':
	    return Subprocess(config, log, eventManager)




if __name__=="__main__":
    home_dir = os.environ['FT']	    
    config = Configure(home_dir + '/FTConfig.txt')
    log = Log()
    log.Open('test.log')
    eventManager = EventManager()
    com=CommFactory.CreateComm("Subprocess",config, log, eventManager)
    com.SendReturn('lspci -vvn')
    com.RecvTerminatedBy()
    com=CommFactory.CreateComm("SSHPexpect",config, log, eventManager)
    com.SendReturn('lspci -vvn')
    com.RecvTerminatedBy()
    com=CommFactory.CreateComm("SSHParamiko",config, log, eventManager)
    com.SendReturn('lspci -vvn')
    com.RecvTerminatedBy()
     
	

