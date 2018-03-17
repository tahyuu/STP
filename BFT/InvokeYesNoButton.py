#!/usr/bin/env python

from Tkinter import *
import os

class YesNoButton(Frame):
    def __init__( self, master, message ):
        Frame.__init__( self, master )
	self.master = master
	self.message = message
        self._createWidgets( )

    def _createWidgets ( self ):
	self._label = Label(self, text=self.message , \
		font="Times -24 bold")
	self._label.grid(row=0, column=0, columnspan=2)
	self.yesButton = Button( self, text="Yes",fg="yellow", \
		bg="blue", font="Times -24 bold", bd=4, relief="groove", \
		command=self.YesButton)
	self.yesButton.grid(row=1, column=0)
	self.noButton = Button( self, text="No",fg="yellow", \
		bg="red", font="Times -24 bold", bd=4, relief="groove", \
		command=self.NoButton)
	self.noButton.grid(row=1, column=1)
	os.system("rm -f REPLY_YES")
	os.system("rm -f REPLY_NO")

    def YesButton(self):
	    self.master.destroy()
	    os.system("touch REPLY_YES")
    def NoButton(self):
	    self.master.destroy()
	    os.system("touch REPLY_NO") 

class InvokeYesNoButton:
    def __init__(self, message, graphics_mode=True):
        if graphics_mode == False:
            self.TextModeYesNo(message)
            return
	self.root = Tk()
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+%d+%d" % (w/2, h/2, w/4, h/4))
	self.yes_no = YesNoButton(self.root, message)
	self.yes_no.place(relx=0.5, rely=0.5, anchor=CENTER)
	self.root.mainloop()

    def TextModeYesNo(self, message):
        os.system("rm -f REPLY_YES")
        os.system("rm -f REPLY_NO")

        while True:
            answer = raw_input(message + " (y/n)")
            if answer == 'y' or answer == 'Y':
                os.system("touch REPLY_YES")
                break
            elif answer == 'n' or answer == 'N':
                os.system("touch REPLY_NO")
                break
            else:
                print("type y or n only")


if __name__ == "__main__":
    InvokeYesNoButton("Are RTR and Fault LEDs flashing?")
