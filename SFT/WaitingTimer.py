#!/usr/bin/env python

from Tkinter import *
import time

class CounterDownTimer( Frame ):
    def __init__( self, master ):
        Frame.__init__( self, master )
	self._waitingTime = 0 
        self._createWidgets( )
	self.master = master

    def _createWidgets ( self ):
	self._label = Label(self, text="Waiting Time", \
		font="Times -60 bold", bg="lightblue")
	self._label.pack()
	self._number = Label( self, text=self._waitingTime,fg="yellow", \
		bg="blue", font="Times -60 bold", width=4)
	self._number.pack(fill=X)

    def SetTimer(self, waitingTime):
	if waitingTime > 0 :
	    self._waitingTime = waitingTime
	else:
	    self._waitingTime = 0
	self._number['text'] = self._waitingTime

    # If leave Operation GUI might cause exception of self.after
    # Try to solve it
    def CountDown(self):
	if self._waitingTime != 0 :
	    self._waitingTime -= 1
	    self._number['text'] = self._waitingTime
	    self.after(1000, self.CountDown)
	else:
	    self.master.destroy()

class WaitingTimer:
    def __init__(self, wait_for_sec, graphics_mode=True):
	if graphics_mode == False:
	    for t in range(wait_for_sec):
		print "Wait for %d seconds" % (wait_for_sec - t)
		time.sleep(1)
	    return
	self.root = Tk()
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+%d+%d" % (w/2, h/2, w/4, h/4))
	self.d = CounterDownTimer(self.root)
	#self.d.pack()
	self.d.place(relx=0.5, rely=0.5, anchor=CENTER)
	self.d.SetTimer(wait_for_sec)
	self.d.CountDown()
	self.root.mainloop()

if __name__ == "__main__":
    #wt = WaitingTimer(15, False) 
    wt = WaitingTimer(15) 
