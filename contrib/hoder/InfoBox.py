#created with help from the following website: 
#http://effbot.org/tkinterbook/tkinter-dialog-windows.htm

# Chris Hoder
# 11/3/2012

from Tkinter import *
import os
import tkMessageBox


# This method will open an InfoBox that will allow the user to write data to
# the bus. NOTE: currently has a hack where the chip is reset to write new data.
# this should be fixed
class InfoBox(Toplevel):
    
    def __init__(self, parent, client, title = None, rate = float(125)):
        
        Toplevel.__init__(self, parent)
        self.transient(parent)
        #top = self.top = Toplevel(parent)
        if title:
            self.title(title)
        #set parent
        self.parent = parent
        #set data object and row number
        self.client = client;
        #save the write rate
        self.rate = rate;
        
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
        
        #why do i need to reset this?
        self.client.MCPsetrate(self.rate)
        self.client.MCPreqstatNormal();
        
    # this method will setup all of the options that will be used for 
    # graphing and the labels and buttons.
    def body(self,master):
        #create dialog body. return widget that should have
        #initial focus. this method should be overriden
        
        #i will store the row number
        i = 0;
        
        entryLabel = Label(master);
        entryLabel["text"] = "Hex to write out"
        entryLabel.grid(row=i,columnspan=3)
        i += 1
        
        #create entry points for each hex byte input location
        self.textBoxes =[];
        self.entries = []
        i +=1
        for j in range(0,13):
            entryLabel = Label(master)
            entryLabel["text"] = str(j)
            entryLabel.grid(row=i-1,column=j)
            var = StringVar();
            var.set('0x00');
            self.entries.append(var)
            entrywidget = Entry(master, textvariable = var );
            entrywidget["width"] = 10;
            entrywidget.grid(row=i,column=j)
            self.textBoxes.append( (j, entrywidget ))
            
        i+=1
        
        writeButton = Button(master,text="Write to board", command=self.handleWrite, width=20)
        writeButton.grid(row=i,columnspan=3)
        
        
        
    # This will write the data to the bus
    def handleWrite(self, event = None):
        self.client.MCPreset()
        self.client.MCPsetup()
        self.client.MCPreqstatNormal()
        packet = []
        #gather packet
        for item in self.entries:
            packet.append(int(item.get(),16))
        self.client.txpacket(packet);
        data = self.client.peek8(0x30)
        while(data & 0x08) == 0:
            print "waiting...";
            data = self.client.peek8(0x30)
        print "message successfully sent!"
        print "wrote message: ", packet
        self.client.MCPreset
    
    
    # This will create a button that will allow the user to exit the dialog
    # box
    def buttonbox(self):
        #add standard button box
        box = Frame(self)
        
        w = Button(box, text="CANCEL", width = 10, command = self.ok, default=ACTIVE)
        w.pack(side=LEFT,padx=5,pady=5)
       
        self.bind("<Return>",self.ok)
        self.bind("<Escape>",self.cancel)
      
        
        box.pack()
        
    def ok(self, event = None):
       
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
        return
    
    def cancel(self, event = None):
        self.parent.focus_set()
        self.destroy()
    
      
#        
#root = Tk()
#Button(root,text="Hello!").pack()
#root.update()
#d = MyDialog(root, dataHeader = {})
#root.wait_window(d.top)
