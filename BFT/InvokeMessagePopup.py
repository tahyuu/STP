#!/usr/bin/env python

from Tkinter import *
import os

class MessagePopup(Frame):
    def __init__( self, master, message_txt, button_txt ):
        Frame.__init__( self, master )
	self.message_txt = message_txt
	self.button_txt = button_txt
	self.master = master
	self.font = "Times -24 bold"
        self._createWidgets( )

    def _createWidgets ( self ):
	self._label = Label(self, text=self.message_txt, \
		font=self.font, fg='yellow', bg='blue')
	self._label.pack()
	self.exit_button = Button( self, text=self.button_txt, \
		font=self.font, bd=4, relief="groove", \
		command=self.ExitButton)
	self.exit_button.pack(fill=X)

    def ExitButton(self):
	    self.master.destroy()

class InvokeMessagePopup:
    def __init__(self, msg_txt, button_txt='Exit', graphics_mode=True):
        if graphics_mode == False:
            self.TextModeMessage(msg_txt, button_txt)
            return

	self.root = Tk()
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+%d+%d" % (w/2, h/2, w/4, h/4))
	if msg_txt.find('FAIL') >= 0:
	    self.root['bg'] = 'red'
	else:
	    self.root['bg'] = 'lightgreen'
	self.message = MessagePopup(self.root, msg_txt, button_txt)
	#self.message.pack(anchor=CENTER)
	self.message.place(relx=0.5, rely=0.5, anchor=CENTER)
	self.root.mainloop()

    def TextModeMessage(self, msg_txt, button_txt):
	print msg_txt 
	print button_txt
	print "Please type any key to proceed"
	raw_input()

if __name__ == "__main__":
    #InvokeMessagePopup('Turn off Power Supply Unit 1', 'Proceed', False)
    #InvokeMessagePopup('Test PASS!!', 'Exit', False)
    #InvokeMessagePopup('Test FAIL!!: Error Code 40 Hard Drive Fail', 'Exit', False)
    InvokeMessagePopup('Turn off Power Supply Unit 1', 'Proceed')
    InvokeMessagePopup('Test PASS!!', 'Exit')
    InvokeMessagePopup('Test FAIL!!: Error Code 40 Hard Drive Fail', 'Exit')
