# reCAN library
# (C) 2013 Chris Hoder    <chrishoder at gmail.com>
#          Ted Sumers     <ted.sumers at gmail.com>
#          Grayson Zulauf <grayson.d.zulauf at gmail.com>
#
# This code is being rewritten and refactored.  You've been warned!

import Tkinter
import Queue
import thread
import tkMessageBox
import tkSimpleDialog
tk = Tkinter



class FordExperimentsFrame:
    """
        This class is a module for our car specific demonstrations of hacks. It is specific
        to our Ford taurus 2004. This will build our window on the GUI to display the hacks that
        can be run. 
        
        @type frame: Tkinter Canvas or Frame
        @param frame: This will be the canvas or frame on which this constructor will
                      build all of the capabilities of the car module. 
                      
        @type communicationLink: class file
        @param communicationLink: This is the class that the user set for the other part of the 
                                  car specific module. This is expected to be a subclass of the 
                                  experiments class. This will contain the experiment methods that
                                  this class will create GUI widgets to run.
    """

    def __init__(self, frame, communicationLink, mainDisplay):
        """
        This constructor will create all the widgets for the display
        as well as set all the bindings for the various hacks that can be
        done.
        
        """
        i = 0
        self.comm = communicationLink
        self.mainDisplay = mainDisplay
        entryLabel = tk.Label(frame, text="Ford Focus 2004 -- High Speed CAN demonstrations", font = "Helvetica 16 bold italic")
        entryLabel.grid(row=i,column=0,columnspan=5,sticky=tk.W)
        
        #######################
        ### SET SPEEDOMETER ###
        #######################
        
        i += 1
        entryLabel = tk.Label(frame, text="Set Speedometer:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.speedVar = tk.StringVar()
        self.speedVar.set("")
        entryWidget = tk.Entry(frame, textvariable=self.speedVar,width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.setSpeedometer, text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
        
        
        ##########################
        #### FAKE SPEEDOMETER ####
        ##########################
        i+= 1
        entryLabel = tk.Label(frame, text="Move MPH Up:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.speedIncrementVar = tk.StringVar()
        self.speedIncrementVar.set("")
        entryWidget = tk.Entry(frame,textvariable=self.speedIncrementVar,width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.speedIncremement,text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
        
        ###############
        ### SET RPM ###
        ###############
        i += 1
        
        entryLabel = tk.Label(frame, text="Set RPMs:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.rpmVar = tk.StringVar()
        self.rpmVar.set("100")
        entryWidget = tk.Entry(frame, textvariable= self.rpmVar, width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.setRPM, text = "Run")
        b.grid(row=i,column=2,sticky=tk.W)
        
        ##################
        #### FAKE RPM ####
        ##################
        i += 1
        entryLabel = tk.Label(frame, text="Fake RPM:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.rpmVarIncrement = tk.StringVar()
        self.rpmVarIncrement.set("")
        entryWidget = tk.Entry(frame, textvariable=self.rpmVarIncrement, width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.rpmIncrement, text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
   
        
        #######################
        ### SET TEMPERATURE ###
        #######################
        
        i += 1
        
        entryLabel = tk.Label(frame, text="Set Temp:")
        entryLabel.grid(row=i,column=0, sticky=tk.W)
        self.engineTempVar = tk.StringVar()
        self.engineTempVar.set("")
        entryWidget = tk.Entry(frame, textvariable=self.engineTempVar, width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command = self.setEngineTemp, text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
    
        
        ############################
        #### SET WARNING LIGHTS ####
        ############################
        i += 1
        self.breakLight = tk.IntVar()
        self.breakLight.set(0)
        ch = tk.Checkbutton(frame, text="Break Light",variable =self.breakLight)
        ch.grid(row=i,column=0,sticky=tk.W)
        
        self.batteryLight = tk.IntVar()
        self.batteryLight.set(0)
        ch = tk.Checkbutton(frame, text="Battery Light", variable=self.batteryLight)
        ch.grid(row=i,column=1,sticky=tk.W)
        
        self.checkTransmissionLight = tk.IntVar()
        self.checkTransmissionLight.set(0)
        ch = tk.Checkbutton(frame, text="Check Transmission", variable = self.checkTransmissionLight)
        ch.grid(row=i,column=2,sticky=tk.W)
        
        self.transmissionOverheated = tk.IntVar()
        self.transmissionOverheated.set(0)
        ch = tk.Checkbutton(frame, text="Transmission Overheated",variable = self.transmissionOverheated)
        ch.grid(row=i,column=3,sticky=tk.W)
        
        i += 1
        self.engineLight = tk.IntVar()
        self.engineLight.set(0)
        ch = tk.Checkbutton(frame, text="Engine Light", variable=self.engineLight)
        ch.grid(row=i,column=0,sticky=tk.W)
        
        self.checkEngine = tk.IntVar()
        self.checkEngine.set(0)
        ch = tk.Checkbutton(frame, text="Check Engine", variable = self.checkEngine)
        ch.grid(row=i,column=1,sticky=tk.W)
        
        
        self.checkFuelCapLight = tk.IntVar()
        self.checkFuelCapLight.set(0)
        ch = tk.Checkbutton(frame, text="Fuel Cap Light", variable =self.checkFuelCapLight)
        ch.grid(row=i,column=2,sticky=tk.W)
        
        self.dashBoardErrors = tk.IntVar()
        self.dashBoardErrors.set(0)
        ch = tk.Checkbutton(frame, text="-- dashboard", variable=self.dashBoardErrors)
        ch.grid(row=i,column=3,sticky=tk.W)
        
        i += 1
        
        self.checkBreakSystem = tk.IntVar()
        self.checkBreakSystem.set(0)
        ch = tk.Checkbutton(frame, text="Check Breaks", variable = self.checkBreakSystem)
        ch.grid(row=i,column=0,sticky=tk.W)
        
        self.ABSLight = tk.IntVar()
        self.ABSLight.set(0)
        ch = tk.Checkbutton(frame, text="ABS Light", variable = self.ABSLight)
        ch.grid(row=i,column=1,sticky=tk.W)
        
        i +=1
        b = tk.Button(frame, command=self.warningLights,text="Warning Lights")
        b.grid(row=i,column=0,columnspan=2,sticky=tk.W)
        
        
        #########################
        #### OVERHEAT ENGINE ####
        #########################
        i += 1
        b = tk.Button(frame, command=self.oscillateTemp, text="Oscillate Temp")
        b.grid(row=i,column=0,sticky=tk.W)
        
        b = tk.Button(frame, command=self.oscillateRPM, text="Oscillate RPM")
        b.grid(row=i,column=1,sticky=tk.W)
        
        b = tk.Button(frame, command=self.oscillateMPH, text="Oscillate MPH")
        b.grid(row=i,column=2,sticky=tk.W)
        
        i +=1
        
        b = tk.Button(frame, command = self.overHeatEngine, text="Overheat Engine")
        b.grid(row=i,column=0,columnspan=1,sticky=tk.W)
        
        b = tk.Button(frame, command = self.LockDoors, text="Lock Doors")
        b.grid(row=i,column=1,sticky=tk.W)
        
        #######################
        ### RUN UP ODOMETER ###
        #######################
        
        b = tk.Button(frame, command = self.runOdometer, text="Increment Odometer")
        b.grid(row=i,column=2,columnspan = 2,sticky=tk.W)
        
        ########################
        #### FAKE SCAN TOOL ####
        ########################
        i+=1
        entryLabel = tk.Label(frame, text="Fake Scan tool")
        entryLabel.grid(row=i,column=0)
    
        i+=1
        entryLabel = tk.Label(frame, text="fuel %:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.fuelLevel = tk.StringVar()
        entryWidget= tk.Entry(frame, textvariable=self.fuelLevel, width=5)
        entryWidget.grid(row=i,column=1, sticky=tk.W)
        
        b = tk.Button(frame,command=self.fakeFuelLevel,text="Start")
        b.grid(row=i,column=2,sticky=tk.W)
        
        i += 1
        
        entryLabel = tk.Label(frame, text="Fake OutsideTemp")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.outsideTemp = tk.StringVar()
        entryWidget= tk.Entry(frame, textvariable=self.outsideTemp,width=5)
        entryWidget.grid(row=i,column=1, sticky=tk.W)
        
        b = tk.Button(frame,command=self.fakeOutsideTemp,text="Start")
        b.grid(row=i,column=2,sticky=tk.W)
        
        ########################### 
        #### GET ENGINE STATUS ####
        ###########################
        i += 1
        b = tk.Button(frame,command=self.getEngineStatus,text="Read Engine Status")
        b.grid(row=i,column=0,columnspan=2,sticky=tk.W)
        
        
        
        
    def getEngineStatus(self):
        if( not self.mainDisplay.checkComm() ):
            return
        self.data = Queue.Queue()
        self.mainDisplay.setRunning()
        self.statusID = self.mainDisplay.root.after(50,self.updateEngineStatus2)
        #self.getEngineStatusControl()
        thread.start_new_thread(self.getEngineStatusControl, ())
        
    def getEngineStatusControl(self, data = None):
        self.mainDisplay.setRunning()
        self.mainDisplay.dataText.config(state=tk.NORMAL) 
        self.mainDisplay.dataText.delete(1.0, tk.END) # clear the text box for the data
        #self.statusID = self.mainDisplay.root.after(50,self.updateEngineStatus2)
        self.mainDisplay.dataText.config(state=tk.DISABLED)
        self.comm.engineDiagnostic(self.data)
        #self.statusID = self.mainDisplay.root.after(50,self.updateEngineStatus2)
        self.mainDisplay.unsetRunning()
        #call engine status method
        

    def updateEngineStatus2(self):
        print "called upate method"
        while( not self.data.empty()):
            try:
                line = self.data.get_nowait()
                print line
            except:
                print "no packet"
            else:
                #self.mainDisplay.addtextToScreen(line)
                self.mainDisplay.dataText.config(state = tk.NORMAL)
                self.mainDisplay.dataText.insert(tk.END, line)
                self.mainDisplay.dataText.config(state=tk.DISABLED)
        print "called"
        if( self.mainDisplay.running.get() == 1):
            self.statusID = self.mainDisplay.root.after(50,self.updateEngineStatus2)
            
    def fakeOutsideTemp(self):
        try:
            level = float(self.outsideTemp.get())
            if( level > 100):
                return
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an number')
            return
        self.comm.fakeOutsideTemp(level)
        
    
    def fakeFuelLevel(self):
        try:
            level = float(self.fuelLevel.get())
            if( level > 100):
                return
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an number')
            return   
        self.comm.fakeScanToolFuelLevel(level)
        
    def LockDoors(self):
        pass
    def oscillateMPH(self):
        self.comm.oscillateMPH(20)
    def oscillateRPM(self):
        pass
    def oscillateTemp(self):
        self.comm.oscillateTemperature(20)
    
    def overHeatEngine(self):
        """
        This method will run the hack that sets the heat dashboard indicator to 
        show that the engine is overheated. This triggers an alarm
        """
        self.comm.overHeatEngine()
        
    def warningLights(self):
        """
        This method will call the hack that sets the warning lights on the display   
        """
        
        self.comm.warningLightsOn(self.checkEngine.get(),self.checkTransmissionLight.get(), \
        self.transmissionOverheated.get(), self.engineLight.get(), self.batteryLight.get(), \
        self.checkFuelCapLight.get(), self.checkBreakSystem.get(), self.ABSLight.get(),self.dashBoardErrors.get())              

    def runOdometer(self):
        """
        This method will call the hack that runs the odometer up
        """
        self.comm.runOdometer()
        
    def setSpeedometer(self):
        """
        This method will call the hack that sets the speedometer
        """
        try:
            setValue = int(self.speedVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        self.comm.setMPH(setValue)
        
        
    def speedIncremement(self):
        """
        This method will increment the speedometer by the given amount
        """
        try:
            setValue = int(self.speedIncrementVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        self.comm.speedometerHack([setValue])
        
    
    def setRPM(self):
        """
        This method will call the hack that sets the RPM
        """
        try:
            print self.rpmVar.get()
            rpmVal = int(self.rpmVar.get())
            #rpmVal = int(self.rpmVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
            return
        #CALL METHOD 
        self.comm.setRPM(rpmVal)   
        
    def rpmIncrement(self):
        """
        This method will call the hack that sets the RPM
        a given amount above what it actually is.
        """
        try:
            rpmVal = int(self.rpmVarIncrement.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
            return
        #CALL METHOD 
        self.comm.rpmHack([rpmVal]) 
        
    def setEngineTemp(self):
        """
        This method will call the hack that sets the engine temp
        """
        try:
            engineTemp = int(self.engineTempVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        #CALL METHOD    
        return
