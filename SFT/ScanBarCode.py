#!/usr/bin/env python

import time
import sys
import os
import re
import subprocess
from Tkinter import *
from Configure import Configure

class ScanBarCode:
    def __init__(self, config):
	#print threading.enumerate(), threading.activeCount()
	self.config = config
        #self.config.Put('Zuari_SN_Re', '\s{9}$')
        #self.config.Put('Zuari_BmcMac1_Re', '[0-9A-F]{12}$')
        #self.config.Put('Zuari_BmcMac2_Re', '[0-9A-F]{12}$')
	self.dut_name = self.config.Get('DUT_Name')
	print self.dut_name
	
	self.width = 30
	self.font = "Times -24 bold"
	title_str = 'Silk Road SFT Station: ' + self.FindHostName() + '      SW Version: ' + self.config.Get('Version')
	self.root = Tk()
	self.root.title(title_str)
	w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
	self.root.geometry("%dx%d+%d+%d" % (w, h, 0, 0))
        #self.root.geometry("%dx%d+%d+%d" % (w/2, h/2, w/4, h/4))
	self.root['bg'] = 'lightblue'

	self.frame = Frame(self.root)
	self.frame.place(relx=0.5, rely=0.5, anchor=CENTER)
	self.labelTitle = Label(self.frame, text = 'Scan ' + self.dut_name + ' Barcode', font = 'Times -40 bold')
	self.labelTitle.grid(row=0, column=0, columnspan=2)
	self.labeleg = Label(self.frame, text = 'Version: ' + self.config.Get('Version'), font = 'Times -32 bold')
	#self.scanItems = ['SN', 'BmcMac1', 'BmcMac2']
	self.scanItems = ['SN']
	self.labeleg.grid(row=0, column=2)
	self.CreateLabelWidget()
	self.CreateEntryWidget()
	self.CreateLabelExampleWidget()
        self.buttonExit = Button(self.root, fg = 'red', bg="yellow", \
                font=self.font, relief="groove", \
                text="Stop Testing and Exit", bd=4, \
                command=self.StopTesting)
	self.buttonExit.pack(side=BOTTOM)
	self.buttonSkip = Button(self.root, fg = 'black', bg="white", \
                font=self.font, relief="groove", \
                text="Use Default Barcode and Skip Scanning", bd=4, \
                command=self.SkipScanning)
	self.buttonSkip.pack(side=BOTTOM)

	self.root.mainloop()

    def SkipScanning(self):
	self.root.destroy()
    
    def StopTesting(self):
	self.root.destroy()
	sys.exit(0)

    def CreateLabelWidget(self):
	row = 0
	for la in self.scanItems:
	    row = row + 1
	    ll = Label(self.frame, font = self.font, text = la)
	    ll.grid(row=row, column=0, sticky=E, pady=5)

    def CreateEntryWidget(self):
	self.ScanSN()
	#self.ScanBmcMac1()
	#self.ScanBmcMac2()

    def CreateLabelExampleWidget(self):
	row = 0
	for la in self.scanItems:
	    row = row + 1
	    ll = Entry(self.frame, font = self.font, width=20, fg='grey')
	    ll.insert(0, self.config.Get(self.dut_name + '_' + la))
	    ll.grid(row=row, column=2, sticky=W, pady=5)

    def CheckFormat(self, pattern, barcode):
        #print pattern, barcode
        p = re.compile(pattern)
        #print p.match(barcode)
        if p.match(barcode):
            return True
        else:
            return False

    def ScanSN(self):
	self.SN_SV = StringVar()
        self.SN = Entry(self.frame, font=self.font, width=self.width)
        self.SN["textvariable"] = self.SN_SV
        self.SN.bind('<KeyPress-Return>', self.SNCheck)
	self.SN.focus_set()
        self.SN.grid(row=1, column=1, sticky=E, pady=5)

    def ScanBmcMac1(self):
        self.MAC1_SV = StringVar()
        self.MAC1 = Entry(self.frame, font=self.font, width=self.width)
        self.MAC1["textvariable"] = self.MAC1_SV
        self.MAC1.bind('<KeyPress-Return>', self.BmcMac1Check)
        self.MAC1.focus_set()
        self.MAC1.grid(row=2, column=1, sticky=E, pady=5)
        self.MAC1.configure(state="disabled")
            
    def ScanBmcMac2(self):
        self.MAC2_SV = StringVar()
        self.MAC2 = Entry(self.frame, font=self.font, width=self.width)
        self.MAC2["textvariable"] = self.MAC2_SV
        self.MAC2.bind('<KeyPress-Return>', self.BmcMac2Check)
        #self.MAC2.focus_set()
        self.MAC2.grid(row=3, column=1, sticky=E, pady=5)
        self.MAC2.configure(state="disabled")
    
    def SNCheck(self, event):
	barcode = self.SN_SV.get()
	#print self.config.Get( 'SN' + '_Re')
	#print barcode
	if self.CheckFormat(self.config.Get('SN' + '_Re'), barcode):
	    #self.config.Put('PcbaSN', barcode)
            #self.MAC1.configure(state="normal")
	    #self.MAC1.focus_set()
	    #self.root.destroy()
	    self.config.Put('CanisterSN', self.SN.get())
	    self.config.Put('PcbaSN', self.SN.get())
            self.root.destroy()
	else:
            self.SN.delete(0,END)

    def BmcMac1Check(self, event):
	barcode = self.MAC1_SV.get()
	#print self.config.Get('BmcMac1' + '_Re')
	#print barcode
        if self.CheckFormat(self.config.Get('BmcMac1' + '_Re'), barcode):
            #self.config.Put('BmcMAC1', barcode)
            self.MAC2.configure(state="normal")
            self.MAC2.focus_set()
            #self.root.destroy()
        else:
            self.MAC1.delete(0,END)
                                                                                    
    def BmcMac2Check(self, event):
        #get = self.MAC2_SV.get()
        #print get
	#barcode = re.findall('00:60:48:\w{2}:\w{2}:\w{2}$',get)[0].replace(':','')
	#print barcode
        barcode = self.MAC2_SV.get()
        if self.CheckFormat(self.config.Get('BmcMac2' + '_Re'), barcode):
            #self.config.Put('BmcMAC2', barcode)
	    print eval("0x"+self.MAC2.get()[-2:])-eval("0x"+self.MAC1.get()[-2:])
	    #if ord(self.MAC2.get()[-1:])-ord(self.MAC1.get()[-1:]) != 1 and ord(self.MAC2.get()[-1:])-ord(self.MAC1.get()[-1:]) != 8:
	    if  eval("0x"+self.MAC2.get()[:])-eval("0x"+self.MAC1.get()[:])==0:
		self.MAC1.delete(0,END)
		self.MAC2.delete(0,END)
		self.MAC1.focus_set()
	    else:
	    	self.config.Put('PcbaSN', self.SN.get())
	    	self.config.Put('CanisterSN', self.SN.get())
            	self.config.Put('BmcMAC1', self.MAC1.get())
           	self.config.Put('BmcMAC2', self.MAC2.get())
            	self.root.destroy()
        else:
            self.MAC2.delete(0,END)

    def FindHostName(self):
        cmdStr = '/bin/hostname'
        findHostName = subprocess.Popen(cmdStr, shell=True, \
                                      stdout=subprocess.PIPE, \
                                      stderr=subprocess.PIPE)
        findHostName.wait()
        hostname = findHostName.communicate()[0].strip()
        self.config.Put('StationName', hostname)
        return hostname

if __name__ == "__main__":
    home_dir = os.environ['FT']
    config = Configure(home_dir + '/SFTConfig.txt')
    ScanBarCode(config)
    print config.Get('CanisterSN')
    #print config.Get('PcbaSN')
    #print config.Get('BmcMAC1')
    #print config.Get('BmcMAC2')
