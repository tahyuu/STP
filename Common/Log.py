#!/usr/bin/env python

from datetime import datetime
import re
import sys
import os

GREY   = '\033[1;20m'
RED    = '\033[1;31m'
GREEN  = '\033[1;32m'
YELLOW = '\033[1;33m'
BLUE   = '\033[1;34m'
BLACK  = '\033[1;m'

class Log:
    def __init__(self):
	self.patt = re.compile(r'\r')
	#self.patt = re.compile(r'[\r\n]')
	self._fd = None
	self._fd2 = None
	self.filename=""

    def isOpen(self):
	if self._fd == None:
	    return False
	else:
	    return True

    def isOpen2(self):
	if self._fd2 == None:
	    return False
	else:
	    return True

    def Open(self, filename):
	self.filename=filename
	self._fd = open(filename, "w+")

    def Open2(self, filename):
	self._fd2 = open(filename, "w+")

    def FilterNonAscii(self, ch):
	if ord(ch) == 10:
	    return ch
	elif ord(ch) < 32 or ord(ch) > 127:
	    return
	else:
	    return ch

    def Print(self, line):
	now1 = datetime.now().isoformat()
	line2 = filter(self.FilterNonAscii, line)
	line3 = now1[11:-4] + " " + line2 + '\n'
	#sys.stdout.flush()
	self._fd.write( line3 )
	self._fd.flush()

    def Print2(self, line):
	now1 = datetime.now().isoformat()
	line2 = filter(self.FilterNonAscii, line)
	line3 = now1[11:-4] + " " + line2 + '\n'
	self._fd2.write( line3 )
	self._fd2.flush()

    def PrintNoTime(self, line):
	self._fd.write( line + '\n')
	self._fd.flush()

    def AddHeader(self, line):
	self._fd.seek(0,0)
	line2 = line.strip() + '\n'
	self._fd.write(line2)
	self._fd.flush()
	self._fd.seek(0,2)

    #to add long string to the head of the file.
    def AddHeader_Long(self, headerStr, logfile):
        os.system("(echo '0a'; echo '%s'; echo '.'; echo 'wq')|ed -s %s" %(headerStr,logfile))
	
    def Close(self):
	self._fd.close()

    def Close2(self):
	self._fd2.close()

if __name__ == "__main__":
    log = Log()
    log.Open("test.txt")
    log.Print("**************************************************************")
    log.Print("hello world")
    log.Print("good morning")
    log.AddHeader("LSI SI,SI-01,PN 12345678,SN 123456,WWID 11223344,PASS,00") 
    log.Close()
