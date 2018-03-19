#!/usr/bin/python

import sys
import os

class Configure:
    def __init__(self, fileName=None):
	self._setting = {} 
	if fileName == None:
	    return
	try:
	    self._file = open(fileName, "r")
	except IOError, exception:
	    print "Can't open the configuratin file: ", exception
	    sys.exit(1)
	    
	self.Read()

    def Load(self, fileName):
	try:
	    self._file = open(fileName, "r")
	except IOError, exception:
	    print "Can't open the configuratin file: ", exception
	    sys.exit(1)
	    
	self.Read()

    def IsNotNull(self, str):
	if len(str) != 0:
	    return 1
	else:
	    return 0
	
    def Read(self):
	line = self._file.readline()
	print line
	while line != '':
	    if line[0][0] != '#' and line != '\n':
		line2 = line.split('\t')
		line2 = filter(self.IsNotNull, line2)
		#print line2
		name = line2[0].strip()
		value = line2[1].strip()
		#comment = line2[2].strip()
		self._setting[name] = value
	    line = self._file.readline()

    def Get(self, key):
	if self._setting.has_key(key):
	    return self._setting[key]
	else:
	    return 'No_such_key'

    def Put(self, key, value):
	self._setting[key] = value

    def Delete(self, key):
	del self._setting[key]

    def Print(self):
	for name in self._setting.keys():
	    print name, self._setting[name]

    def Save(self, fileName):
	f = open(fileName,"w")
	for name in self._setting.keys():
	    f.write(name + '\t' + self._setting[name] + '\n')
	f.close()
	
if __name__ == "__main__":
    home_dir = os.environ['FT']
    config = Configure()
    config.Load(home_dir + "/SFTConfig.txt")
    config.Print()
    print '--------------------------------------------------------------'
    print config.Get('DUT_Name')
    print '--------------------------------------------------------------'
    config.Print()
    config.Save('SFTConfig2.txt')	
    while True:
	key = raw_input('Input key value: ')
	value = config.Get(key)
	if value != 'No_such_key':
	    print value
	else:
	    break
