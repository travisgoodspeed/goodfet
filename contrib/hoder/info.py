#import Tkinter
from Tkinter import *
import csv
import time
import sys;
import binascii;
import array;
import datetime
import os
import thread
from mainDisplay import *
import tkMessageBox


# create a shorthand object for Tkinter so we don't have to type it all the time
tk = Tkinter


class info(Toplevel):
    
    #constructor method
    def __init__(self, parent, title = None):
        
        Toplevel.__init__(self, parent)
        self.transient(parent)
        #top = self.top = Toplevel(parent)
        self.BOLDFONT = "Helvetica 16 bold italic"
        if title:
            self.title(title)
        #set parent
        self.parent = parent
        #set Data
        
        
        
        
        
        body = Frame(self)
        
        
        
        
        self.initial_focus = self.body(body)
        body.pack(padx=5,pady=5)
        
        self.buttonbox()
        
        self.grab_set()
        
        if not self.initial_focus:
            self.initial_focus = self
            
            
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        #positions the window relative to the parent
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        
        self.initial_focus.focus_set()
        
        self.wait_window(self)
        
    # This sets up the body of the popup dialog with all of the buttons and information
    def body(self,master):
        #add a frame for the id choice
        self.idframe = tk.Frame(master)
        self.idframe.pack(side=tk.TOP, padx=2, pady=2, fill=X)
        
        entryLabel = Tkinter.Label(self.idframe, text="ArbID: ")
        entryLabel.grid(row=0,column=0)
        self.options = ["INSERT","insert"]
        self.IDchoice = Tkinter.StringVar()
        self.IDchoice.set(self.options[0])
        self.IDchoice.trace('w',self.updateDisplay)
        #self.splitChoice = OptionMenu(self.canvas, self.splitValue, *keys)
        idChoiceOptions= OptionMenu(self.idframe,self.IDchoice, *tuple(self.options))
        idChoiceOptions.grid(row=0,column=1)
        
        
        
        # make a separator line
        sep = tk.Frame( master, height=2, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.TOP, padx = 2, pady = 2, fill=tk.X)
        # build the controls
        self.buildControls(master)
        
      
    def updateDisplay(self, name, index, mode):
        print "name: ", name
        print "index: ", index
        print "mode: ", mode
        print "change"  
        
    def buildControls(self, master):
        # make a control frame
        self.cntlframe = tk.Frame(master)
        self.cntlframe.pack(side=tk.TOP, padx=2, pady=2, fill=X)

        # make a separator line
        sep = tk.Frame( master, height=2, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.TOP, padx = 2, pady = 2, fill=tk.X)

        # make a cmd 1 button in the frame
        self.buttons = []
        #width should be in characters. stored in a touple with the first one being a tag
        self.buttons.append( ( 'cmd1', tk.Button( self.cntlframe, text="General Info", command=self.generalInfo, width=10 ) ) )
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ( 'cmd2', tk.Button( self.cntlframe, text="Data - bytes", command=self.data, width=10 ) ) )
        self.buttons[-1][1].pack(side=tk.LEFT)  # default side is top
        self.buttons.append( ('cmd3', tk.Button(self.cntlframe, text="Packets", command=self.packets, width=10)))
        self.buttons[-1][1].pack(side=tk.LEFT)
        return

    
    
    def generalInfo(self):
        pass
    
    def data(self):
        pass
    
    def packets(self):
        pass
    
    #This is the cancel / ok button
    def buttonbox(self):
        #add standard button box
        box = Frame(self)
        
        #ok button
        #w = Button(box, text="Apply", width = 10, command = self.ok, default=ACTIVE)
        #w.pack(side=LEFT,padx=5,pady=5)
        # cancel button
        w = Button(box,text="Cancel", width=10,command = self.ok)
        w.pack(side=LEFT,padx=5,pady=5)
        
        self.bind("<Return>",self.ok)
        self.bind("<Escape>",self.ok)
        
        box.pack()
        
    # ok button will first validate the choices (see validate method) and then exit the dialog
    # if everything is ok 
    def ok(self, event = None):
        
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.parent.focus_set()
        self.destroy()
        return 1
        
    # this is a cancel button which will just exit the dialog and should not plot anything
    def cancel(self, event = None):
    
        #put focus back on parent window
        self.parent.focus_set()
        self.destroy()
        return 0
       
    #this tests to make sure that there are inputs 
    def validate(self):
        #returns 1 if everything is ok
        return 1
    
    #this method is called right before exiting. it will set the input dictionary with the information for
    # the display method to grab the data and graph it
    def apply(self):
        
            
        return
