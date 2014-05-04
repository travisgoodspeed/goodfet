# reCAN library
# (C) 2013 Chris Hoder    <chrishoder at gmail.com>
#          Ted Sumers     <ted.sumers at gmail.com>
#          Grayson Zulauf <grayson.d.zulauf at gmail.com>
#
# This code is being rewritten and refactored.  You've been warned!


import Tkinter
import csv
import string
import time
import sys;
import binascii;
import array;
from DataManage import DataManage
from tkFileDialog import askopenfilename
import tkSimpleDialog
import tkMessageBox
import tkHyperlinkManager
import datetime
import os
import thread
import ConfigParser
from Tkinter import *

try:
    import MySQLdb
    MYSQL_INSTALL = True
except ImportError:
   
    MYSQL_INSTALL = False

###############################
#### GOODTHOPTER 10 FILES #####
###############################
sys.path.insert(0,'../../trunk/client/')
from GoodFETMCPCANCommunication import *
from GoodFETMCPCAN import GoodFETMCPCAN;
from experiments import experiments
#from FordExperiments import FordExperiments
from intelhex import IntelHex;



# create a shorthand object for Tkinter so we don't have to type it all the time
tk = Tkinter 
""" Shortcut for Tkinter """


class DisplayApp:
    """ 
    This is the main display for the graphical user interface (GUI). This GUI is designed to aid 
    the user in their work listening to CAN traffic via the GOODTHOPTER10 board, U{http://goodfet.sourceforge.net/hardware/goodthopter10/}.
    There are no inputs to this class but all default data is loaded from the settings file.
    
    """   

    # init function
    def __init__(self):
        self.BOLDFONT = "Helvetica 16 bold italic"
        """ Bold font that all headers will use """
        self.SETTINGS_FILE = "./Settings.ini"
        """ This stores the location of the file where settings are saved"""
        Config = ConfigParser.ConfigParser()
        try:
            fileObj = open(self.SETTINGS_FILE)
            results = Config.read(self.SETTINGS_FILE)
        except Error, msg:
            print "Error Parsing Config File."
            print msg
        else:
            if( results == []):
                print "Could not load config file %s"%self.SETTINGS_FILE
        
        # Initialize the data manager
        self.DATA_LOCATION = self.ConfigSectionMap(Config, "FileLocations")['data_location']
        """ Stores the location where sniffing information and injection information will be stored"""
        
        dmData = self.ConfigSectionMap(Config,"DataManager")
        
        
        self.SQL_NAME = dmData['sql_name']
        """ Holds SQL name"""
        self.SQL_HOST = dmData['sql_host']
        """ holds SQL host name"""
        self.SQL_USERNAME = dmData['sql_username']
        """ holds SQL username"""
        self.SQL_PASSWORD = dmData['sql_password']
        """ holds SQL password"""
        self.SQL_DATABASE = dmData['sql_database']
        """ holds SQL database name"""
        self.SQL_TABLE = dmData['sql_table']
        """ holds SQL table name"""
        self.dm = DataManage(host=self.SQL_HOST, db=self.SQL_DATABASE, \
                             username=self.SQL_USERNAME,password=self.SQL_PASSWORD,table=self.SQL_TABLE,\
                             dataLocation = self.DATA_LOCATION)
        """ Data Manager class. This can do all the data manipulation/storage/retrieval"""
        windowInfo = self.ConfigSectionMap(Config, "WindowSize")
        # width and height of the window
        self.initDx = int(windowInfo['width'])
        """ Total window width """
        self.initDy = int(windowInfo['height'])
        """ Total window height """
        self.dataDx =80;
        """ Data window width"""
        #self.dataDx = (self.initDx/2-350);
       
        self.dataDy = self.initDy;
        """ Data window Height"""
        #self.ControlsDx = (self.initDx - 80);
        self.ControlsDx = 400;
        """ Controls window width. This is the right side"""
        
        self.ControlsDy = self.initDy;
        """ Controls window height """
        
        #configure information
        #Initialize communication class
        
        
        self.freq = float(self.ConfigSectionMap(Config, "BusInfo")['frequency']) 
        """ Bus frequency """
        
        
        experimentInfo = self.ConfigSectionMap(Config, "experimentInfo")
        self.packetInformationFile = experimentInfo.get("packetinformation")
        """ This file stores the user's known information about the packets. This is a json file"""  
        self.experimentFile = experimentInfo.get("experimentfile")
        """ This is the experiment file that is car specific. this is for adding a car specific module"""
        self.experimentGUIFile = experimentInfo.get("experiment_gui_file")
        """ This is the GUI file that is needed to add the car specific module to the CAN Reader"""
        self.CarExtention = False
        """ This is false when there is no car extension, true otherwise"""
        
        
        
        self.loadJson()
        """ This loads the json file with our packet information"""
        
        
        self.verbose = True 
        

        # create a tk object, which is the root window
        self.root = tk.Tk() 
        """ Stores the tk object for the window """ 
        self.root.bind_class("Text","<Command-a>", self.selectall) # rebinds the select all feature
        
        
        
       
        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )
        
        # set the title of the window
        self.root.title("CAN Data Reader")

        # set the maximum size of the window for resizing
        #self.root.maxsize( 1024, 768 )

        # bring the window to the front
        self.root.lift()
        
        
        # setup the menus
        self.buildMenus()

        # build the controls
        self.buildControls()
        
        self.setBindings()
        
        self.buildDataCanvas()
        
        self.RightSideCanvas = tk.Canvas( self.root, width=self.ControlsDx, height=self.ControlsDy)
        """ Canvas for the entire right side (all tabs are inside of this canvas, in the grid format)"""
        # build the objects on the Canvas
        self.blankCanvas = tk.Canvas(self.RightSideCanvas,width=self.ControlsDx*10,height=self.ControlsDy*10)
        """ This is a blank canvas to cover hidden layers """
        self.blankCanvas.grid(row=0,column=0)
        
        ##################################
        ### BUILD RIGHT HAND SIDE TABS ###
        ##################################
        self.buildCanvas()
        self.buildExperimentCanvas()
        self.buildSQLCanvas()
        self.buildInfoFrame()
        self.buildCarFrame()
        
        self.RightSideCanvas.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.BOTH)
        
        # LIFT THE SNIFF FRAME TO TOP
        self.sniffFrameLift()
        
        self.running = Tkinter.IntVar()
        """ 
        This is a boolean value which when false tells you that there is a 
        thread communicating with the bus at the moment
        """
        self.running.set(0)
        self.running.trace('w',self.updateStatus)
        
        ### CONNECT TO GOODTHOPTER 10 BOARD ###
        self.connectBus()
        #self.testConnect()
        
        if( MYSQL_INSTALL == False):
            tkMessageBox.showwarning('MySQLdb not installed. MYSQL disabled','MySQLdb not installed. MYSQL disabled')
            
            for bt in self.buttons:
                print bt[0]
                if( bt[0] is "SQL"):
                    print "here"
                    bt[1].config(state=tk.DISABLED)
                
        
  
    def writeiniFile(self, filename, section, option, value):
        """ 
        Writes the given settings to the given settings filename. If the section does not exist in the 
        settings file then it will be created. The file is assumed to be a .ini file. This method is
        a modified version of the one found on the following website: 
        U{http://bytes.com/topic/python/answers/627791-writing-file-using-configparser}
        
        @type filename: string
        @param filename: path to the settings file
        @type section: string
        @param section: section heading in the settings file
        @param option: string
        @param option: The option in the given section in the settings file that will be set
        @param value: The value of the option we are saving. 
        """
        Config = None
        Config = ConfigParser.ConfigParser()
        Config.read(filename)
        if not Config.has_section( section ): #create the section
            Config.add_section(section)
        Config.set(section, option, value)
        Config.write(open(filename,'w'))
        
    #modified from the following example:
    # http://wiki.python.org/moin/ConfigParserExamples
    def ConfigSectionMap(self, Config, section):
        """
        This method has been implemented based on the following exmaple, 
        U{http://wiki.python.org/moin/ConfigParserExamples}.
        
        @param Config: ConfigParser instance that has already read the given settings filename.
        @type section: string
        @param section: Section that you want to get all of the elements of from the settings 
                        file that has been read by the Config parser and passed in as Config.
        @rtype: Dictionary
        @return: Dictionary where they keys are the options in the given section and the values 
                 are the corresponding settings value.
        """
        dict1 = {}
        options = Config.options(section)
        for option in options:
            try:
                dict1[option] = Config.get(section,option)
                if( dict1[option] == 1):
                    print "Skipped loading option: %s" %option
            except:
                print "Cannot load settings file. Crash on %s"%option
                dict1[option] = None
        return dict1
         
    def buildMenus(self):
        """
        This method will build the menu bars
        """
        
        # create a new menu
        self.menu = tk.Menu(self.root)

        # set the root menu to our new menu
        self.root.config(menu = self.menu)

        # create a variable to hold the individual menus
        self.menulist = []

        # create a file menu
        filemenu = tk.Menu( self.menu )
        self.menu.add_cascade( label = "File", menu = filemenu )
        self.menulist.append(filemenu)

        # create another menu for kicks
        cmdmenu = tk.Menu( self.menu )
        self.menu.add_cascade( label = "Command", menu = cmdmenu )
        self.menulist.append(cmdmenu)

        # menu text for the elements
        menutext = [ [ 'Quit  \xE2\x8C\x98-Q', 'Settings ^. ' ],
                     [ '-', '-', '-' ] ]

        # menu callback functions
        menucmd = [ [ self.handleQuit, self.handleSettings],
                    [self.handleCmd1, self.handleCmd2, self.handleCmd3] ]
        
        # build the menu elements and callbacks
        for i in range( len( self.menulist ) ):
            for j in range( len( menutext[i]) ):
                if menutext[i][j] != '-':
                    self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    self.menulist[i].add_separator()
    
    
    def selectall(self, event):
        """ 
        This method is called when the user wishes to select the entire text box.
        """
        event.widget.tag_add("sel","1.0","end")


    def buildExperimentCanvas(self):
        """ 
        This method will build out the experiment frame which will display to the user the 
        various experiments that can be run. This will be a list of experiments with input 
        values and is kept inside the L{self.RightSideCanvas} and is one of the tabs that
        will be created but buried from view until the user selects the experiments button
        """
        self.experimentFrame = Tkinter.Frame(self.RightSideCanvas, width=self.ControlsDx,\
                                                                 height=self.ControlsDy)
        """ Experiment frame """
        
        i=0 # i will store the row number
        
        j = 0 # stores the collumn number
        
        ########################################
        #### SWEEP ALL IDS EXPERIMENT SETUP ####
        ########################################
        
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Sweep Std IDs:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j += 3
        sweepButton = Button(self.experimentFrame, text="Start", width=3, command=self.sweepID)
        sweepButton.grid(row=i, column=j,sticky=tk.W)
        i+=1
        j = 0
        entryLabel=Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.sniffTime = Tkinter.StringVar();
        self.sniffTime.set("2")
        """ length of sniff for sweep exeriments """
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.sniffTime)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j, sticky=tk.W)
        j+=1
        #align with lower exp
        j += 2
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "From: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.lowSweep = Tkinter.StringVar();
        """ Low bound for the sweep range """
        self.lowSweep.set("0")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.lowSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+=1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "To "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.HighSweep = Tkinter.StringVar();
        """ High bound for sweep range """
        self.HighSweep.set("4095")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.HighSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        
        
        ########################################
        #### SWEEP RTR IDS EXPERIMENT SETUP ####
        ########################################
        
        # note that these two sweep methods share the same variables for the time, 
        # low and high bound values
        
        i += 1
        j = 0
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "RTR Sweep Response:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j += 3
        sweepButton = Button(self.experimentFrame, text="Start", width=3, command=self.RTRsweepID)
        sweepButton.grid(row=i, column=j,sticky=tk.W)
        i+=1
        j = 0 
        entryLabel=Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.sniffTime)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j, sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame, text = "Attempts: ")
        entryLabel.grid(row=i, column = j, sticky=tk.W)
        j += 1
        
        self.attempts = Tkinter.StringVar();
        """ 
        This is the number of times an rtr will be sent to the BUS before 
        moving onto the next one in the RTR sweep method
        """
        self.attempts.set("1")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable = self.attempts)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "From:"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.lowSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "To "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        #self.HighSweep = Tkinter.StringVar();
        #self.HighSweep.set("4095")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.HighSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        
        j += 1
        i+= 1
        j = 0
        
        
        #############################################
        ##### FUZZ ALL PACkETS EXPERIMENT SETUP #####
        #############################################
        
        
        entryLabel = Tkinter.Label(self.experimentFrame,font=self.BOLDFONT)
        entryLabel["text"] = "Fuzz all possible packets"
        entryLabel.grid(row=i,column=j,columnspan=3,stick=tk.W)
        j+=3
        startButton = Tkinter.Button(self.experimentFrame,text="Start",width=3,command=self.generalFuzz)
        startButton.grid(row=i,column=j,sticky=tk.W)
        j+=1
        
        i+=1
        j=0
        self.generalFuzzData = {}
        """ 
        This is a dictionary that will store all the information needed to run the general fuzz method.
        keys: period, writesPerFuzz, Fuzzes. All the values are Tkinter.StringVar() and contained the information
        input by the user
        """
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Period (ms): "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        period = Tkinter.StringVar()
        period.set("")
        self.generalFuzzData['period'] = period
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=period)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Writes:"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        writesPerFuzz = Tkinter.StringVar()
        writesPerFuzz.set("")
        self.generalFuzzData['writesPerFuzz'] = writesPerFuzz
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=writesPerFuzz)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
     
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Fuzzes:"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        Fuzzes = Tkinter.StringVar()
        Fuzzes.set("")
        self.generalFuzzData['Fuzzes'] = Fuzzes
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=Fuzzes)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        
        
        
        #######################################################
        ##### GENERATION FUZZING PACkETS EXPERIMENT SETUP #####
        #######################################################
        
        
        j = 0
        i += 1
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Generation Fuzzing:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j +=3
        startButton = Tkinter.Button(self.experimentFrame,text="Start",width=3,command=self.GenerationFuzz)
        startButton.grid(row=i,column=j,sticky=tk.W)
        i+=1
        self.fuzzData = {}
        """ This is a dictionary that will store all the information needed to run the generation fuzz method.
        keys: sIDs (string of all sIDs to fuzz on), period, writes, writesPerFuzz, Fuzzes, dB0,db1,..,db7 
        (stores the limits as a list [low, high]. All the values are 
        Tkinter.StringVar() and contained the information input by the user
        """
        j = 0 
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "sID: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        sID = Tkinter.StringVar()
        sID.set("")
        self.fuzzData['sIDs'] = sID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=sID)
        entryWidget["width"] = 40
        entryWidget.grid(row=i,column=j,columnspan=8,sticky=tk.W)
        j += 1
        i += 1
        j = 0
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Period (ms): "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        period = Tkinter.StringVar()
        period.set("")
        self.fuzzData['period'] = period
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=period)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Writes: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        writesPerFuzz = Tkinter.StringVar()
        writesPerFuzz.set("")
        self.fuzzData['writesPerFuzz'] = writesPerFuzz
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=writesPerFuzz)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
     
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Fuzzes:"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        Fuzzes = Tkinter.StringVar()
        Fuzzes.set("")
        self.fuzzData['Fuzzes'] = Fuzzes
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=Fuzzes)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        
        i+=1 
        j = 0
        
        # This is putting the limits options for the user to set low and high ranges 
        # for each databyte during
        # the fuzzing. It is split up into 3 rows plus a header on the top and bottom
        for k in range(1,10,3):
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "Low"
            entryLabel.grid(row=i,column=k,sticky=tk.W)
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "High"
            entryLabel.grid(row=i,column=k+1,sticky=tk.W)
        i += 1
        j = 0
        k = 0 #data byte we are on at the moment
        for j in range (0, 7, 3):
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "db%d:" %k
            entryLabel.grid(row=i,column=j, sticky= tk.W)
            varTempLow = Tkinter.StringVar()
            varTempLow.set("")
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varTempLow)
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            varTempHigh = Tkinter.StringVar()
            self.fuzzData['db%d'%(k)] = [varTempLow, varTempHigh]
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable = varTempHigh)
            entryWidget["width"] = 5
            entryWidget.grid(row=i,column=j+2,sticky=tk.W)
            k += 1
            print k
        
        for j in range(0,7,3):
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "db%d:" %((k))
            entryLabel.grid(row=i+1,column=j, sticky= tk.W)
            varTempLow = Tkinter.StringVar()
            varTempLow.set("")
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varTempLow)
            entryWidget.grid(row=i+1,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            varTempHigh = Tkinter.StringVar()
            self.fuzzData['db%d'%(k)] = [varTempLow, varTempHigh]
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable = varTempHigh)
            entryWidget["width"] = 5
            entryWidget.grid(row=i+1,column=j+2,sticky=tk.W)
            k +=1
        
        for j in range(0,4,3):
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "db%d:" %((k))
            entryLabel.grid(row=i+2,column=j, sticky= tk.W)
            varTempLow = Tkinter.StringVar()
            varTempLow.set("")
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varTempLow)
            entryWidget.grid(row=i+2,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            varTempHigh = Tkinter.StringVar()
            self.fuzzData['db%d'%(k)] = [varTempLow, varTempHigh]
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable = varTempHigh)
            entryWidget["width"] = 5
            entryWidget.grid(row=i+2,column=j+2,sticky=tk.W)
            k +=1
    
    
        ######################################################
        ##### RE-INJECT FUZZED PACKETS EXPERIMENT SETUP #####
        #####################################################
        
        
    
        i += 3
        j=0
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Re-inject Fuzzed Packets:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j +=3
        startButton = Tkinter.Button(self.experimentFrame,text="Start",width=3,\
                                                    command=self.reInjectFuzzed)
        startButton.grid(row=i,column=j,sticky=tk.W)
        i+=1
        j = 0
        self.reInjectData = {}
        """ 
        This is a dictionary that will store all the information needed to run the
        re-injecting of fuzzed data experiment.
        keys: sID, date, startTime, endTime. All the values are 
        Tkinter.StringVar() and contained the information input by the user
        """
        entryLabel = Tkinter.Label(self.experimentFrame,text="sID:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        varID = Tkinter.StringVar()
        varID.set("")
        self.reInjectData['sID'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+=1
        # The injection files are all saved by date
        entryLabel = Tkinter.Label(self.experimentFrame,text="Date:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        varID = Tkinter.StringVar()
        now = datetime.datetime.now()
        varID.set(now.strftime("%Y%m%d")) # automatically fill with today's date
        self.reInjectData['date'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varID,width=10)
        entryWidget.grid(row=i,column=j,columnspan=2,sticky=tk.W)
        j+= 2
        i += 1
        j = 0
        # The injection files are all saved by date
        entryLabel = Tkinter.Label(self.experimentFrame,text="Start(HHMM):")
        entryLabel.grid(row=i,column=j,columnspan=1,sticky=tk.W)
        j+= 1
        varID = Tkinter.StringVar()
       
        varID.set("") # automatically fill with today's date
        self.reInjectData['startTime'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        # The injection files are all saved by date
        entryLabel = Tkinter.Label(self.experimentFrame,text="END(HHMM):")
        entryLabel.grid(row=i,column=j,columnspan = 1, sticky=tk.W)
        j+= 1
        varID = Tkinter.StringVar()
       
        varID.set("") # automatically fill with today's date
        self.reInjectData['endTime'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        
        i+= 1
        j = 0
        
        
        ############################################
        ##### PACKET RESPONSE EXPERIMENT SETUP #####
        ############################################
    
        
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Packet Response:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j +=3
        startButton = Tkinter.Button(self.experimentFrame,text="Start",width=3,\
                                                    command=self.packetResponse)
        startButton.grid(row=i,column=j,sticky=tk.W)
        i+=1
        self.packetResponseData = {}
        """
        This is a dictionary that will store all the information needed to run packet 
        response experiment.
        
        keys: time, repeats, period, listenID, listen_db0,...,listen_db7,responseID, 
        Response_db0,...,Response_db7. All the values are 
        Tkinter.StringVar() and contained the information input by the user
        """
        j = 0 
        entryLabel = Tkinter.Label(self.experimentFrame,text="Time:")
        entryLabel.grid(row=i,column=j,sticky = tk.W)
        j += 1
        varID = Tkinter.StringVar()
        varID.set("30")
        self.packetResponseData['time'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame,text="repeats:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        varID = Tkinter.StringVar()
        varID.set("100")
        self.packetResponseData["repeats"] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame,text="period:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        varID = Tkinter.StringVar()
        varID.set("1")
        self.packetResponseData["period"] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        i+=1
        j = 0
        entryLabel = Tkinter.Label(self.experimentFrame,text="listenID: ")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        varID = Tkinter.StringVar()
        varID.set("")
        self.packetResponseData['listenID'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID, width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j +=1
        entryLabel = tk.Label(self.experimentFrame,text="data:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        for k in range(0,8): ## for all 8 data bytes
            varID = tk.StringVar()
            varID.set("")
            idx = 'Listen_db%d'%k
            self.packetResponseData[idx] = varID
            entryWidget = tk.Entry(self.experimentFrame,textvariable=varID,width=5)
            entryWidget.grid(row=i,column=j,sticky=tk.W)
            j += 1
        i += 1
        j = 0
        entryLabel = tk.Label(self.experimentFrame,text="Res.ID:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        varID = tk.StringVar()
        varID.set("")
        self.packetResponseData["responseID"] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+=1
        entryLabel = tk.Label(self.experimentFrame,text="data:")
        entryLabel.grid(row=i,column=j,stick=tk.W)
        j += 1
        for k in range(0,8): # for all 8 data bytes
            varID = tk.StringVar()
            varID.set("")
            idx = 'Response_db%d'%k
            self.packetResponseData[idx] = varID
            entryWidget = tk.Entry(self.experimentFrame,textvariable=varID,width=5)
            entryWidget.grid(row=i,column=j,sticky=tk.W)
            j+=1
       
        self.experimentFrame.grid(row=0,column=0,sticky=tk.W+tk.N,pady=0)

    def buildInfoFrame(self):
        """
        This builds the tab that displays our information about the
        arbitration ids and any known information about the packets at the moment.
        This will itself have 3 sub tabs: General Information, Bytes, Packets. These are
        rebuilt for each arbitration id chosen.
        """
        i = 0 # row num
        self.infoFrame = tk.Frame(self.RightSideCanvas, width=self.ControlsDx, height=self.ControlsDy)
        """ Frame the holds the display widgets for our packet information"""
        entryLabel = Tkinter.Label(self.infoFrame, text="ArbID: ")
        entryLabel.grid(row=i,column=0)
        
        
        
        ####################################
        #### ARBITRATION ID OPTION MENU ####
        ####################################
        
        
        # get all the arbIDS
        ids = (self.packetInformationFileData['Arbitration Ids']).keys()
        intIds = []
        #convert to integer to sort so that they are in order
        for element in ids:
            intIds.append(int(element))
        intIds = sorted(intIds)
        ids = []
        #need to convert back to strings
        for element in intIds:
            ids.append(str(element))
            
        self.options = ids
        """ These are the known arbitration ids"""
        self.IDchoice = Tkinter.StringVar()
        self.IDchoice.set(self.options[0])
        self.IDchoice.trace('w',self.updateInfo)
        
        
        self.idChoiceOptions= OptionMenu(self.infoFrame,self.IDchoice, *tuple(self.options))
        self.idChoiceOptions.grid(row=i,column=1)
        i += 1
        
        #############################
        ##### CREATE TAB BUTTONS ####
        #############################
        
        button = tk.Button(self.infoFrame, text="General Info", command=self.liftGeneralInfo)
        button.grid(row=i,column=0)
        
        button = tk.Button(self.infoFrame,text="Byte Info", command=self.liftBytesInfo)
        button.grid(row=i,column=1)
        
        button = tk.Button(self.infoFrame,text="Packets", command=self.liftPackets)
        button.grid(row=i,column=2)
        
        button = tk.Button(self.infoFrame,text="Add ID", command=self.addArbID)
        button.grid(row=i,column=3)
        
        button = tk.Button(self.infoFrame,text="Save", command=self.saveJsonInfo)
        button.grid(row=i,column=4)
        
        i += 1
        ###################
        ### CREATE TABS ###
        ###################
        self.buildGeneralInfoFrame(i)
        self.buildPacketInfoFrame(i)
        self.buildByteInfoFrame(i)
        self.blankCanvasInfoFrame = tk.Canvas(self.infoFrame,width=self.ControlsDx, height = self.ControlsDy)
        """ This is a blank canvas to hide frames when they are not on top"""
        self.blankCanvasInfoFrame.grid(row=i, column = 0, columnspan=20,sticky=tk.N+tk.W+tk.E+tk.S)
        self.infoFrame.grid(row=0,column=0,sticky=tk.N+tk.W)
        
        self.updateInfo() #load first set of data
        self.liftGeneralInfo() #put the general info on the top
    
    def buttonTest(self):
        print 'asdfa'
        
    def deleteArbID(self):
        """
        This method will delete an ID from the JSON file that stores packet
        information. The user will first be prompted to ask if they really
        want to. If they say yes then the another dialog box will open for 
        the user to input the id they want to delete. This will delete the 
        ID, save the new JSON document, and update the ID drop down menu.
        """
        msg = "Are you sure you want to delete an Arbitration ID? This cannot be"\
            + " undone"
        #double check that the user wants to upload
        response = tkMessageBox.askyesno(title = "Delete ID", message = msg)
        
        if(response):
           id = tkSimpleDialog.askstring('Delete Arbitration ID', 'Enter ID to delete') 
           if( id == None or id == ""):
               return
           iterationNum = 0
           for existingID in self.options:
               if( existingID == id):
                   self.packetInformationFileData['Arbitration Ids'].pop(id)
                   self.options.pop(iterationNum)
               iterationNum += 1
               
           self._reset_option_menu(self.idChoiceOptions,self.options,self.IDchoice)
           self.dm.saveJson(self.packetInformationFile,self.packetInformationFileData)
            
    def addArbID(self):
        """
        This method will add a new arbitration id to the json file. It will first prompt the user
        as to what id it wants to add. Then the new database entry will be created, added to the 
        structure, saved and updated on the GUI. 
        """
        id = tkSimpleDialog.askstring('New Arbitration ID', 'What is the id you wish to add?')
        if( id == None):
            return
        try:
            int(id)
        except:
            tkMessageBox.showwarning('Not a correct Arbitration ID', \
                'Arbitration ID must be an integer!')
            return
        
        try:
            for existingID in self.options:
                if( existingID == id):
                    raise Exception
        except:
            tkMessageBox.showwarning('Arbitration ID already exists', \
                'Arbitration ID %s, is already in the system'%id)
            return
        GeneralInfo = {}
        GeneralInfo['CANspeed'] = 0
        GeneralInfo['frequency'] = 0
        GeneralInfo['correlations'] = []
        GeneralInfo['comment tags'] = []
        GeneralInfo['comments'] = []
        
        ByteInfo = {}
        for i in range(0,8):
            dbVar = {}
            dbVar['Continuous'] = 0
            dbVar['Changes'] = 0
            dbVar['Correlations'] =[]
            dbVar['Comments'] = []
            ByteInfo['db%d'%i] = dbVar
        
        PacketInfo = {}
        
        self.packetInformationFileData['Arbitration Ids'][id] = {'GeneralInfo':GeneralInfo, 'Bytes':ByteInfo, 'Packets':PacketInfo}
        self.options.append(id)
        self.options.sort(key=lambda x:[int(y) for y in x.split('.')])
        
        self._reset_option_menu(self.idChoiceOptions,self.options,self.IDchoice)
        #self.idChoiceOptions= OptionMenu(self.infoFrame,self.IDchoice, *tuple(self.options))
        self.dm.saveJson(self.packetInformationFile,self.packetInformationFileData)
    
    def _reset_option_menu(self,om, options, variable, index=None):
        '''reset the values in the option menu

        if index is given, set the value of the menu to
        the option at the given index. This code was modified from code found on stack overflow question:
        U{http://stackoverflow.com/questions/7393430/how-can-i-dynamic-populate-an-option-widget-in-tkinter-depending-on-a-choice-fro}
        
        @type om: option menu widget
        @param om: Option menu to be edited
        
        @type options: List
        @param options: List of the options that the option menu will have. This is expected to be a list of strings
        
        @type variable: Tkinter.StringVar
        @param variable: The string variable that is associated with the option menu
        '''
        menu = om["menu"]
        menu.delete(0, "end")
        for string in options:
            menu.add_command(label=string, 
                             command=lambda value=string:
                                    variable.set(value))
        if index is not None:
            variable.set(options[index])
    
    def buildByteInfoFrame(self,i):
        """
        This method will build the frame that will display our information about the specific
        bytes of an arbitration ID. 
        
        @type i: Integer
        @param i: This is the row to add our Frame to. This is for the grid formation 
        """
        self.byteInfoFrame = tk.Frame(self.infoFrame,width=self.ControlsDx,height = self.ControlsDy)
        """ Byte info frame """
        self.byteInfoFrame.grid(row=i,column=0,columnspan=20, sticky=tk.N+tk.W+tk.E+tk.S)
        k = 0
        entryLabel  = tk.Label(self.byteInfoFrame,text="Byte Information: ", font=self.BOLDFONT)
        entryLabel.grid(row=k,column=0,sticky=tk.W+tk.N)
        k+=1
        self.byteInfoSubCanvas = tk.Canvas(self.byteInfoFrame,width=self.ControlsDx+180,height=self.ControlsDy-150)
        self.byteInfoSubCanvas.grid(row=k,column=0,columnspan=4,rowspan=1,sticky=tk.N+tk.E+tk.W+tk.S)
        xscroll = tk.Scrollbar(self.byteInfoFrame,orient=tk.HORIZONTAL)
        xscroll.grid(row=k+1,column=0,columnspan=4,sticky=tk.E+tk.W)
        yscroll = tk.Scrollbar(self.byteInfoFrame)
        yscroll.grid(row=k,column=4,sticky=tk.N+tk.S)
        yscroll.config(command=self.byteInfoSubCanvas.yview)
        xscroll.config(command=self.byteInfoSubCanvas.xview)
        self.byteInfoSubCanvas.config(yscrollcommand=yscroll.set,xscrollcommand=xscroll.set)
        #self.byteInfoFrame.grid_rowconfigure(0,weight=1)
        #self.byteInfoFrame.grid_columnconfigure(0,weight=1)
        
        self.byteInfoSubFrame = tk.Frame(self.byteInfoSubCanvas)
        self.byteInfoSubFrame.rowconfigure(1,weight=1)
        self.byteInfoSubFrame.columnconfigure(1,weight=1)
        
        #entryLabel = tk.Label(self.byteInfoFrame,text="Changes:")
        #entryLabe.grid(row=k,column=0,sticky=tk.W)
        self.byteInfoData = {}
        q = -1
        for i in range(0,8):
            q += 1
            entryLabel = tk.Label(self.byteInfoSubFrame,text="Data Byte %d"%i)
            entryLabel.grid(row=q,column=0,sticky=tk.W)
            q += 1
            dbByte = {}
            var = tk.IntVar()
            var.set(0)
            c = tk.Checkbutton(self.byteInfoSubFrame,text="Changes", variable = var)
            c.grid(row=q,column=0,sticky=tk.W)
            dbByte['changes'] = var
            
            var = tk.IntVar()
            var.set(0)
            c = tk.Checkbutton(self.byteInfoSubFrame,text="Continuous", variable = var)
            c.grid(row=q,column=1,sticky=tk.W)
            dbByte['continuous'] = var
            
            q +=1
            entryLabel = tk.Label(self.byteInfoSubFrame,text="Correlations")
            entryLabel.grid(row=q,column=0,sticky=tk.W)
            var = tk.StringVar()
            dbByte['correlations'] = var
            entryWidget = tk.Entry(self.byteInfoSubFrame,textvariable = var,width=40)
            entryWidget.grid(row=q,column=1,columnspan=4)
            
            q+=1
            entryLabel = tk.Label(self.byteInfoSubFrame,text="Comments")
            entryLabel.grid(row=q,column=0,sticky=tk.W)
            
            q+= 1
            textBox = tk.Text(self.byteInfoSubFrame,width=80,height=2,wrap=tk.WORD,borderwidth=3)
            #textBox.insert(END,'asdflkafjlksdfjadl;kfjadfklafjadslkfdjasf;lkadjfdlkfjadslkfjadsfl;kajdf;lkfdj\naskfjdasfkajdskdl;fjadklfjdkl;fjafl;kdjkalsj\nakjfdlkasfjadkljdlfk;ajdflkadjfldas;kjdfkljdf\n')
            scroll = tk.Scrollbar(self.byteInfoSubFrame)
            scroll.grid(row = q, column = 3, sticky=tk.N+tk.S)
            
            #xscroll = tk.Scrollbar(self.byteInfoSubFrame,orient=tk.HORIZONTAL)
            #xscroll.grid(row=q+1, column=0,columnspan=3,sticky=tk.W+tk.E)
            #textBox.config(yscrollcommand=scroll.set, xscrollcommand=xscroll.set)
            textBox.config(yscrollcommand=scroll.set)
            scroll.config(command=textBox.yview)
            #xscroll.config(command=textBox.xview)
            
            textBox.grid(row=q,column=0,columnspan=3,sticky=tk.W+tk.N+tk.E+tk.S)
            #textBox.config(state=tk.DISABLED)
            q += 1
            dbByte['comments'] = textBox
            self.byteInfoData['db%d'%i] = dbByte
            
#            
#        self.byteInfoSubCanvas.grid(row=k,column=0,columnspan=4,sticky=tk.N+tk.E+tk.W+tk.S)
#        xscroll = tk.Scrollbar(self.byteInfoFrame,orient=tk.HORIZONTAL)
#        xscroll.grid(row=k+1,column=0,columnspan=4,sticky=tk.E+tk.W)
#        yscroll = tk.Scrollbar(self.byteInfoFrame)
#        yscroll.grid(row=k,column=4,sticky=tk.N+tk.S)
#        self.byteInfoSubCanvas.config(yscrollcommand=xscroll.set, xscrollcommand=yscroll.set)
#        xscroll.config(command=self.byteInfoSubCanvas.xview)
#        yscroll.config(command=self.byteInfoSubCanvas.yview)
#        self.byteInfoSubFrame.grid(row=k,column=0,columnspan =4, sticky=tk.E+tk.W)
#        self.byteInfoSubCanvas.create_window(0,0,anchor=NW,window=self.byteInfoFrame)
#        self.byteInfoSubFrame.config(width=30,height=3)
#        self.byteInfoSubCanvas.config(scrollregion=self.byteInfoSubFrame.bbox("all"))
#        
        
#        #byteInfoSubFrame.grid(row=0,column=0,sticky=tk.N+tk.W)
#        rows = 5
#        for i in range(1,rows):
#            for j in range(1,10):
#                button = Button(byteInfoSubFrame, text="[%d,%d]" % (i,j))
#                button.grid(row=i, column=j, sticky='news')
        self.byteInfoSubCanvas.create_window(0,0,anchor=tk.NW,window=self.byteInfoSubFrame)
        self.byteInfoSubCanvas.update_idletasks()
        self.byteInfoSubCanvas.config(scrollregion=self.byteInfoSubCanvas.bbox(tk.ALL))
        
        
        
    def buildPacketInfoFrame(self,i):
        """
        This method will build the frame that will display our information about the specific
        packets of an arbitration ID. These are packets that we know what they are telling us or
        broadcasting to the bus. Each packet description will be click-able. This will fill the 
        write options under the sniff tab and then change focus to this tab. This will allow for
        easy injection of these packets.
        
        @type i: Integer
        @param i: This is the row to add our Frame to. This is for the grid formation 
        """
        self.packetInfoFrame = tk.Canvas(self.infoFrame,width=self.ControlsDx, height = self.ControlsDy)
        """ Packet Info tab"""
        self.packetInfoFrame.grid(row=i,column=0,columnspan=20, sticky=tk.N+tk.W+tk.E+tk.S)
        self.packetInfoFrame.config(selectborderwidth=0)
        
        k = 0
        entryLabel = tk.Label(self.packetInfoFrame, text = "Known Packets", font = self.BOLDFONT)
        entryLabel.grid(row = k, column = 0, sticky=tk.W)
        k+=1
        self.packetInfoText = tk.Text(self.packetInfoFrame, width=80, height=30,wrap=tk.WORD,borderwidth=3)
        """ This is the text widget where all the packets will be displayed to """
        
        scroll = tk.Scrollbar(self.packetInfoFrame)
        scroll.grid(row = k, column = 3, sticky=tk.N+tk.S)
        
        xscroll = tk.Scrollbar(self.packetInfoFrame,orient=tk.HORIZONTAL)
        xscroll.grid(row=k+1, column=0,columnspan=3,sticky=tk.W+tk.E)
        self.packetInfoText.config(yscrollcommand=scroll.set, xscrollcommand=xscroll.set)
        scroll.config(command=self.packetInfoText.yview)
        xscroll.config(command=self.packetInfoText.xview)
        
        self.packetInfoText.grid(row=k,column=0,columnspan=3,sticky=tk.W+tk.N+tk.E+tk.S)
        #self.packetInfoText.config(state=tk.DISABLED)
        self.packetHyperlink = tkHyperlinkManager.HyperlinkManager(self.packetInfoText) 
        """ 
        This contains the links so that we can inject packets in this list by clicking on the
        the provided description
        """
        
    def buildGeneralInfoFrame(self,i):
        """
        This method will build the frame that will display our information about our
        general knowledge of an arbitration ID.
        
        @type i: Integer
        @param i: This is the row to add our Frame to. This is for the grid formation 
        """
        self.generalInfoFrame = tk.Frame(self.infoFrame, width=self.ControlsDx, height = self.ControlsDy)   
        """ general information tab"""
        self.generalInfoFrame.grid(row=i, column = 0, columnspan = 20, sticky=tk.N+tk.W + tk.E+tk.S)
       
        k = 0; #row num
        entryLabel = Tkinter.Label(self.generalInfoFrame,text="General Information:",font = self.BOLDFONT)
        entryLabel.grid(row = k, column = 0, sticky = tk.W, columnspan = 2)
       
       
        k += 1;
        self.generalInfoVars = {}
        """ This will store all of the variables for resetting the General Info's page"""
        
        # arbitration id frequency
        varId = tk.StringVar()
        self.generalInfoVars['frequency'] = varId
        entryLabel = Tkinter.Label(self.generalInfoFrame, text="Frequency: ")
        entryLabel.grid(row = k, column = 0, sticky=tk.W)
        entryLabel = Tkinter.Entry(self.generalInfoFrame, textvariable = varId)
        entryLabel.grid(row = k, column = 1, sticky=tk.W)
        
        k +=1 
        
        
        #########################
        ### CAN BUS FREQUENCY ###
        #########################
        
        # bus speed that it is on
        varId = tk.StringVar()
        self.generalInfoVars['canbus'] = varId
        entryLabel = Tkinter.Label(self.generalInfoFrame, text="CAN Bus: ")
        entryLabel.grid(row = k, column = 0, sticky=tk.W)
        entryLabel = Tkinter.Entry(self.generalInfoFrame, textvariable = varId)
        entryLabel.grid(row = k, column = 1, sticky=tk.W)
        
        k += 1
        
        
        ##################################
        ### KNOWN CORRELATIONS TEXTBOX ###
        ##################################
        
        #known correlations to the arbitration id
        entryLabel = Tkinter.Label(self.generalInfoFrame,text="Correlations: ")
        entryLabel.grid(row = k, column = 0, sticky=tk.W)
        
        k += 1
        correlationsText = tk.Text(self.generalInfoFrame,width=60, height = 4, wrap=tk.WORD, borderwidth=3)
        
        scroll = tk.Scrollbar(self.generalInfoFrame)
        scroll.grid(row = k, column=3,sticky=tk.N+tk.S)
        
        xscroll = tk.Scrollbar(self.generalInfoFrame, orient=tk.HORIZONTAL)
        xscroll.grid(row=k+1,column=0,columnspan=3,sticky=tk.W+tk.E)        
        correlationsText.config(yscrollcommand=scroll.set, xscrollcommand=xscroll.set)
        scroll.config(command=correlationsText.yview)
        xscroll.config(command=correlationsText.xview)
        correlationsText.grid(row=k,column=0,columnspan=3,sticky=tk.W+tk.N+tk.E+tk.S)
        #correlationsText.config(state=tk.DISABLED)
        
        self.generalInfoVars['correlations'] = correlationsText
        
        k +=2
        # Commment tags, this relates to our SQL database and the comment field
        
        ###########################
        ### COMMENT TAG TEXTBOX ###
        ###########################
        
        entryLabel = Tkinter.Label(self.generalInfoFrame, text="Comment Tags:")
        entryLabel.grid(row=k,column=0,sticky=tk.W)
        
        k += 1
        commentTags = tk.Text(self.generalInfoFrame,width=60, height = 4, wrap=tk.WORD, borderwidth=3)
        
        scroll = tk.Scrollbar(self.generalInfoFrame)
        scroll.grid(row = k, column=3,sticky=tk.N+tk.S)
        
        xscroll = tk.Scrollbar(self.generalInfoFrame, orient=tk.HORIZONTAL)
        xscroll.grid(row=k+1,column=0,columnspan=3,sticky=tk.W+tk.E)        
        commentTags.config(yscrollcommand=scroll.set, xscrollcommand=xscroll.set)
        scroll.config(command=commentTags.yview)
        xscroll.config(command=commentTags.xview)
        commentTags.grid(row=k,column=0,columnspan=3,sticky=tk.W+tk.N+tk.E+tk.S)
        #commentTags.config(state=tk.DISABLED)
        self.generalInfoVars['commentTags'] = commentTags
        
        self.generalInfoFrame.grid(row=i, column = 0, columnspan = 20, sticky=tk.N+tk.W)

        k += 2
        
        ################################
        ### GENERAL COMMENTS TEXTBOX ###
        ################################
        
        entryLabel = Tkinter.Label(self.generalInfoFrame, text="General Comments: ")
        entryLabel.grid(row=k,column=0,sticky=tk.W)
        k += 1
        
        comments = tk.Text(self.generalInfoFrame,width=60, height = 4, wrap=tk.WORD, borderwidth=3)
        
        scroll = tk.Scrollbar(self.generalInfoFrame)
        scroll.grid(row = k, column=3,sticky=tk.N+tk.S)
        
        xscroll = tk.Scrollbar(self.generalInfoFrame, orient=tk.HORIZONTAL)
        xscroll.grid(row=k+1,column=0,columnspan=3,sticky=tk.W+tk.E)        
        comments.config(yscrollcommand=scroll.set, xscrollcommand=xscroll.set)
        scroll.config(command=comments.yview)
        xscroll.config(command=comments.xview)
        comments.grid(row=k,column=0,columnspan=3,sticky=tk.W+tk.N+tk.E+tk.S)
        #comments.config(state=tk.DISABLED)
        self.generalInfoVars['comments'] = comments
    
    
    def liftGeneralInfo(self):
        """
        This method lifts the General information tab to the top and 
        makes it viewable to the screen.
        """
        tk.Misc.lift(self.blankCanvasInfoFrame,aboveThis = None)
        tk.Misc.lift(self.generalInfoFrame, aboveThis=None)
        
    def liftBytesInfo(self):
        """
        This method lifts the Bytes information tab to the top and 
        makes it viewable to the screen.
        """
        tk.Misc.lift(self.blankCanvasInfoFrame,aboveThis = None)
        tk.Misc.lift(self.byteInfoFrame,aboveThis = None)
        
    def liftPackets(self):
        """
        This method lifts the Packets information tab to the top and 
        makes it viewable to the screen.
        """
        tk.Misc.lift(self.blankCanvasInfoFrame, aboveThis = None)
        tk.Misc.lift(self.packetInfoFrame, aboveThis = None)
    
    def updateQueryInfo(self,name, index, mode):
        """
        This method will update the query tab so that it is correct and so that the user does not
        try to save a .pcap file to .csv or vice versa. 
        It will also update the beginning of the MYSQL command for the .pcap.
        This is because of how the write to .pcap method is written. 
        See L{DataManage.writetoPcapfromSQL}.
        """
        choice = self.sqlChoice.get()
        filename = self.queryFilename.get()
        if( choice == 'csv'):
            self.sqlQueryInfo.set("")
            self.queryFilename.set(filename[:-3] + "csv") #change filename ending
        else:
            self.sqlQueryInfo.set("Select msg from %s where"%self.SQL_TABLE)
            self.queryFilename.set(filename[:-3] + "pcap") #change filename ending
            
            
    def saveJsonInfo(self, event = None):
        """
        This file will save all of the user's information to the json file specified in settings.
        The data will be saved to json data structure in memory and then dumped to the file via the
        DataManager method, L{DataManage.saveJson}.
        """
        
        idChoice = self.IDchoice.get()
    
        ##########################
        #### GET GENERAL INFO ####
        ##########################
        
        #can bus frequency
        GeneralInfo = self.packetInformationFileData['Arbitration Ids'][idChoice]['GeneralInfo']
        try:
            GeneralInfo['CANspeed']=float(self.generalInfoVars['canbus'].get())
        except:
            tkMessageBox.showwarning('Can speed not a number', \
                'Incorrect input for CAN speed')
            return
        
        # frequency of id 
        try:
            GeneralInfo['frequency']=float(self.generalInfoVars['frequency'].get())
        except:
            tkMessageBox.showwarning('Frequency not a number', \
                'Incorrect input for frequency')
            return
        
        # correlations to the id
        try: 
            correlations = self.generalInfoVars['correlations'].get(1.0,END)
            corr = correlations.split('\n')
            GeneralInfo['correlations'] = corr
        except:
            tkMessageBox.showwarning('Unable to save correlations', \
                'Unable to save information in correlations')
            return
        #comment tags on the id   
        try:
            comments = self.generalInfoVars['commentTags'].get(1.0,END)
            comm = comments.split('\n')
            GeneralInfo['comments tags'] = comm
        except:
            tkMessageBox.showwarning('Unable to save comment tags', \
                'Unable to save information in comment tags text box')
            return
        
        #######################################
        #### GET BYTE SPECIFIC INFORMATION ####
        #######################################
        
        ByteInfo = self.packetInformationFileData['Arbitration Ids'][idChoice]['Bytes']
        ByteData = self.byteInfoData
        dbVars = ByteData['db0']
        
        try:
            for i in range(0,8):
                dbInfo = ByteInfo['db%d'%i]
                dbVars = ByteData['db%d'%i]
                print dbVars['changes'].get()
                temp =  dbVars['changes'].get()
            
                if( temp == ""):
                    temp = 0
                dbInfo['Changes'] = str(temp)
                
                temp = dbVars['continuous']
                if( temp == ""):
                    temp = 0
                print dbVars['continuous'].get()
                dbInfo['Continuous'] = dbVars['continuous'].get()
                
                dbInfo['Correlations'] = dbVars['correlations'].get().split(',')
                
                dbInfo['Comments'] = (dbVars['comments'].get(1.0,END)).split('\n')
                
        except:
            tkMessageBox.showwarning('Unable to save data bytes', \
                'Unable to save information in data byte %d'%i)
            return
            
        #############################
        #### GET EXAMPLE PACKETS ####
        #############################
        
        packets = self.packetInfoText.get(1.0,END).split('\n')
        packetdb = {}
        try:
            for packet in packets:
                print packet
                elements = packet.split(':')
                if(len(elements) == 0 or len(elements) == 1):
                    continue
                print elements
                print elements[0].lstrip()
                packetdb[elements[0].lstrip()] = elements[1].lstrip()
                print elements[1].lstrip()
            self.packetInformationFileData['Arbitration Ids'][idChoice]['Packets'] = packetdb
        except:
           tkMessageBox.showwarning('Unable to save known packets section', \
                'Unable to save information on the known packets')         
        
           return
            
            
        
        ### SAVE INFO
        self.dm.saveJson(self.packetInformationFile,self.packetInformationFileData)
           
            
    def updateInfo(self, name = None, index = None, mode = None):
        """
        This method is called when the user changes the option menu for arbitration IDs under our
        packetInformation tab. This will update these packet information tabs with our knowledge of
        the new ID. If the set ID does not exist (was set when the user clicked on the id from sniffed
        data) then a warning dialog will appear. 
        """
        idChoice = self.IDchoice.get() # get arbitration id we want to know about
        found = False
        # make sure that the element exists
        for element in self.options:
            if( element == idChoice):
                found = True
                break
        # the element does not exist -- throw a warning dialog
        if( found == False):
            tkMessageBox.showwarning('Unknown ID', \
                'There is no information on the id, ' + idChoice)
            return
        
        
        ###############################
        ### UPDATE GENERAL INFO TAB ###
        ###############################
        
        GeneralInfo = self.packetInformationFileData['Arbitration Ids'][idChoice]['GeneralInfo']
        # CAN BUS FREQUENCY
        self.generalInfoVars['canbus'].set(GeneralInfo['CANspeed'])
        # FREQUENCY OF PACKET
        self.generalInfoVars['frequency'].set(GeneralInfo['frequency'])
        
        ### KNOWN CORRELATIONS ###
        correlations = GeneralInfo['correlations']
        corrText = ""
        for corr in correlations:
            corrText += corr + "\n"
        correlationsText = self.generalInfoVars['correlations']
        #correlationsText.config(state=tk.NORMAL) 
        correlationsText.delete(1.0, END) # clear the text box for the data
        correlationsText.insert(END,corrText)
        #correlationsText.config(state=tk.DISABLED)
        
        
        ### COMMENT TAGS ###
        commentTags = GeneralInfo['comment tags']
        commentT = ""
        for comm in commentTags:
            commentT += comm + "\n"
        commentText = self.generalInfoVars['commentTags']
        #commentText.config(state=tk.NORMAL)
        commentText.delete(1.0,END)
        commentText.insert(END,commentT)
        #commentText.config(state=tk.DISABLED)
        
        ### COMMENTS ###
        commentList = GeneralInfo['comments']
        comment = ""
        for comm in commentList:
            comment += comm + "\n"
        
        commentText = self.generalInfoVars['comments']
        #commentText.config(state=tk.NORMAL)
        commentText.delete(1.0,END)
        commentText.insert(END,comment)
        #commentText.config(state=tk.DISABLED)
        
        ##########################
        #### BYTE INFORMATION ####
        ##########################
        PacketInfo = self.packetInformationFileData['Arbitration Ids'][idChoice]['Bytes']
        for i in range(0,8):
            dbVars = self.byteInfoData['db%d'%i]
            dbInfo = PacketInfo['db%d'%i]
            dbCont = dbInfo['Continuous']
            if( dbCont != '0' or dbCont != '1' or dbCont != 0 or dbCont != 1):
                dbCont = 0
            dbVars['continuous'].set(dbCont)
            #dbVars['changes'].set(dbInfo['Changes'])
            dbcorr = dbInfo['Changes']
            if( dbcorr != '0' or dbcorr !='1' or dbcorr != 0 or dbcorr !=1):
                dbcorr = 0
            dbVars['changes'].set(dbcorr)
            dbVars['correlations'].set(', '.join(dbInfo['Correlations']))
            textBox = dbVars['comments']
            #textBox.config(state=tk.NORMAL)
            textBox.delete(1.0,END)
            textBox.insert(END,'\n'.join(dbInfo['Comments']))
            #textBox.config(state=tk.DISABLED)
            #.set('\n'.join(dbInfo['Comments']))
            
        
        
        
        
        ##########################
        ### PACKET INFORMATION ###
        ##########################
        self.packetHyperlink.reset() #remove all hyperlinks
        #self.packetInfoText.config(state=tk.NORMAL)
        self.packetInfoText.delete(1.0,END)
        packetDict =self.packetInformationFileData['Arbitration Ids'][idChoice]['Packets']
        keys = packetDict.keys()
        for key in keys:
            packet = packetDict[key]
            # add a hyperlink to the description
            self.packetInfoText.insert(END, key + ":", self.packetHyperlink.add(self.injectPacket,[idChoice, packet]))
            self.packetInfoText.insert(END,"\t\t\t " + packet + " \n")
        #self.packetInfoText.config(state=tk.DISABLED)
        
        self.infoFrameLift()
        
        
    def injectPacket(self, data):
        """
        This method will take the data that is given and fill the write method section
        in the sniff tab. It will also switch the view to this tab so that the user
        can easily inject this packet. This method does not inject the packet onto the
        CAN bus. It simple makes the entry ready for the user to do so.
        
        @type data: List
        @param data: This is a list that contains the data packet that we want to inject.
               data[0] contains the arbitration id as a string. data[1] contains the 
               data bytes as a string. The format of the data within the string is assumed
               to be in decimal form with spaces between the bytes.
        """
        #
        
        self.writeData['sID'].set(data[0])
        self.writeData['rtr'].set(0)
        self.writeData['fromFile'].set(0)
        packet = data[1]
        packetData = packet.split(" ")
        # fill the data byte section
        for i in range(0,8):
            self.writeData['db%d'%i].set(packetData[i])
        # lift the sniff tab to view 
        self.sniffFrameLift()
    
    
    def buildCarFrame(self):
        """
        This method will build the car module tab. It will build the frame but will only build the module
        if one has been set in the settings file. This allows users to create their own module that is car
        specific but can still be run from the GUI. See L{connectBus} for information on the module connection.
        """
        self.carFrame = tk.Frame(self.RightSideCanvas,width=self.ControlsDx, height=self.ControlsDy)
        """ Car module frame """
        
        # Only build the car module if there is a file that has been set to do it ( indicated by the boolean).
        if( self.CarExtention == True):
            self.buildCarModule()
            
        
        self.carFrame.grid(row=0,column=0,sticky=tk.N+tk.W+tk.S+tk.E)
        
    def buildCarModule(self):
        """
        This will build the car module. This is specific to a car and the class method to do this
        can be set by the user. The user's class should take in the frame where it will write all
        of it's components as well as a reference to the experiment file that must also be specified
        in the settings file. This experiment file class is a sub class of experiments which is a sub
        class of GoodFETMCPCANCommunication. 
        """
        self.carMod = self.ourCarGuiClass(self.carFrame,self.comm,self)
        
    def buildSQLCanvas(self):
        """
        This method will build the SQL tab frame where some of the database information is stored. 
        It will contain the upload to db method as well as a way to download data from the database
        and convert to .pcap
        """
        self.sqlFrame = tk.Frame(self.RightSideCanvas, width = self.ControlsDx, \
                                                            height=self.ControlsDy)
        i = 0;
        sqlButton = tk.Button(self.sqlFrame,text="Upload Sniffed Packets to Database", \
                                                         command=self.uploaddb, width=30)
        sqlButton.grid(row=i,column=0,columnspan=3,sticky=tk.W)
        i+=1;

        entryLabel = Tkinter.Label(self.sqlFrame,  font = self.BOLDFONT)
        entryLabel["text"] = "MYSQL:"
        entryLabel.grid(row=i,column=0, sticky = tk.W)
        sqlButton = tk.Button( self.sqlFrame, text="Query", command=self.sqlQuery, width=4)
        sqlButton.grid(row=i,column=1,sticky=tk.W)
        
        
        options = ['csv','pcap']
        self.sqlChoice = Tkinter.StringVar()
        self.sqlChoice.set(options[1])
        self.sqlChoice.trace('w',self.updateQueryInfo)
        optionsSniff = OptionMenu(self.sqlFrame, self.sqlChoice,*tuple(options)) #put an options menu for type
        optionsSniff.grid(row=i,column=2,columnspan=1,sticky=tk.W)
    
        i += 1
        self.sqlQueryInfo = tk.StringVar()
        self.sqlQueryInfo.set("Select msg from %s where"%self.SQL_TABLE)
        label = Tkinter.Label(self.sqlFrame,textvariable=self.sqlQueryInfo)
        label.grid(row=i,column=0,columnspan=3,sticky=tk.W)
        i +=1
        #text query box
        self.text = Tkinter.Text(self.sqlFrame,borderwidth=10,insertborderwidth=10,padx=5,pady=2,\
                                                    width=50,height=5, highlightbackground="black")
        self.text.grid(row=i,column=0, columnspan=10,rowspan=2)
        i += 9
        
        i +=1
        #relative filename input
        entryLabel = Tkinter.Label(self.sqlFrame)
        entryLabel["text"] = "Filename:"
        entryLabel.grid(row=i, column = 0,columnspan=1,stick=tk.W)
        self.queryFilename = Tkinter.StringVar()
        self.queryFilename.set("1.pcap")
        entryWidget = Tkinter.Entry(self.sqlFrame, textvariable=self.queryFilename)
        entryWidget.grid(row=i,column=1,columnspan=4,sticky=tk.W)
        
        
        i += 1
        self.sqlFrame.grid(row=0,column=0,sticky=tk.W+tk.N,pady=0)

    def buildCanvas(self):
        """
        This builds the Frame that controls the sniffing and writing with the CAN bus. 
        It is contained within the L{self.RightSideCanvas} and is 
        in the same grid layout as the SQL, EXPERIMENTS tabs. 
        """
        
        # this makes the canvas the same size as the window, but it could be smaller
        self.sniffFrame = tk.Frame( self.RightSideCanvas, width=self.ControlsDx, height=self.ControlsDy)
        i = 0
    
        
        #########################
        ##### FILTERS SETUP #####
        #########################
        
        
        entryLabel = Tkinter.Label(self.sniffFrame,  font = self.BOLDFONT)
        entryLabel["text"] = "Filters:"
        entryLabel.grid(row=i,column=0, sticky=tk.W)
        
        
        
        i += 1
        self.filterIDs = []
        """ 
        This contains a list of the Tkinter.StringVar's 
        that hold the filters that the user inputs 
        """
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "Buffer 0:" # there are 2 buffers on the MC2515 and you can set them individually
        entryLabel.grid(row=i,column =0, sticky=tk.W )
        for j in range(0,2):
            stdID = Tkinter.StringVar()
            stdID.set("")
            entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=stdID)
            self.filterIDs.append(stdID)
            entryWidget["width"] = 5
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
            
        i += 1
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "Buffer 1:"
        entryLabel.grid(row=i,column =0 ,sticky=tk.W)
        for j in range( 0,4):
            stdID = Tkinter.StringVar()
            stdID.set("")
            entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=stdID)
            self.filterIDs.append(stdID)
            entryWidget["width"] = 5
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
        clearButton = tk.Button( self.sniffFrame, text="Clear", command=self.clearFilters, width=5)
        clearButton.grid(row=i,column=j+2,sticky=tk.W)
        i += 1
        
        #################################
        ######### SNIFF SETUP ###########
        #################################
        
        
        #sniff button
        i += 1
        entryLabel = Tkinter.Label(self.sniffFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Sniff: "
        entryLabel.grid(row=i, column=0, sticky = tk.W)
        sniffButton = tk.Button( self.sniffFrame, text="Start", command=self.sniff, width=3 )
        sniffButton.grid(row=i,column=1, sticky= tk.W)
       
        options = ['Rolling','Fixed']
        self.SniffChoice = Tkinter.StringVar()
        """ 
        Type of sniff to display. Rolling will print a new line for each packet.
        Fixed will keep each packet on it's own individual line
        """
        self.SniffChoice.set(options[0])
        optionsSniff = OptionMenu(self.sniffFrame, self.SniffChoice,*tuple(options)) #put an options menu for type
        optionsSniff.grid(row=i,column=2,columnspan=2,sticky=tk.W)
        self.fixedView = False
    
        self.saveInfo = tk.IntVar()
        """
        Boolean to let the user decide if they want to save the sniff data or not
        """
        self.saveInfo.set(1)
        c = Checkbutton(self.sniffFrame, variable=self.saveInfo, text="Save Data")
        c.grid(row=i,column=4,columnspan = 2, sticky=tk.W)
        i += 1
        
        #time to sniff for
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=0, sticky=tk.W)
        self.time = Tkinter.StringVar();
        """ Length of time to sniff the bus for"""
        self.time.set("10")
        entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=self.time)
        entryWidget.grid(row=i,column=1, sticky=tk.W)
        entryWidget["width"] = 5
        i += 1
        
        #comment
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "Comment:"
        entryLabel.grid(row=i,column=0, sticky = tk.W)
        self.comment = Tkinter.StringVar();
        """ Comment tag that will be kept in the sql database with each packet"""
        self.comment.set("")
        entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=self.comment)
        entryWidget.grid(row=i,column=1, columnspan = 7, sticky=tk.W)
        entryWidget["width"] = 30
        i += 1
        
        
        #################################
        ######### WRITE SETUP ###########
        #################################
        
        
        #writing
        i += 1
        entryLabel = Tkinter.Label(self.sniffFrame,  font = self.BOLDFONT)
        entryLabel["text"] = "Write:"
        entryLabel.grid(row=i,column=0, sticky = tk.W)
        
        writeButton = tk.Button( self.sniffFrame, text="Start", command=self.write, width=3 )
        writeButton.grid(row=i,column=1, sticky= tk.W)
        
        # This will hold the data options for writing 
        self.writeData = {}
        """ This is a dictionary containing all of the data for writing onto the bus """
        rtr = IntVar()
        rtr.set(0)
        self.writeData["rtr"] = rtr
        c = Checkbutton(self.sniffFrame,variable=rtr, text="rtr")
        c.grid(row=i,column=2, sticky = tk.W)
        
        fromFile = tk.IntVar()
        fromFile.set(0)
        self.writeData['fromFile'] = fromFile
        c = Checkbutton(self.sniffFrame, variable=fromFile, text="Write from File")
        c.grid(row=i,column=3,columnspan = 2, stick=tk.W)
        
        i += 1
        
        entryLabel = Tkinter.Label(self.sniffFrame, text="Period (ms): ")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        varTemp = Tkinter.StringVar()
        self.writeData["period"] = varTemp
        varTemp.set(100);
        entryWidget = Tkinter.Entry(self.sniffFrame,width=5,textvariable=varTemp)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        
        entryLabel = Tkinter.Label(self.sniffFrame, text="Writes: ")
        entryLabel.grid(row=i,column=2,sticky=tk.W)
        
        varTemp = Tkinter.StringVar()
        self.writeData["writes"] = varTemp
        varTemp.set(10)
        entryWidget = Tkinter.Entry(self.sniffFrame, width=5, textvariable=varTemp)
        entryWidget.grid(row=i, column=3, sticky=tk.W)
        
        
        
        
        i += 1
        
        
        
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "sID:"
        entryLabel.grid(row=i,column=0, sticky= tk.W)
        varTemp = Tkinter.StringVar()
        self.writeData['sID'] = varTemp
        varTemp.set("")
        entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=varTemp)
        entryWidget.grid(row=i,column=1, sticky=tk.W)
        entryWidget["width"] = 5
        i += 1
        
        ###################################
        ######### BYTEs TO WRITE ##########
        ###################################
        
        k = 0
        for j in range (0, 8, 2):
            entryLabel = Tkinter.Label(self.sniffFrame)
            entryLabel["text"] = "db%d:" %k
            entryLabel.grid(row=i,column=j, sticky= tk.W)
            varTemp = Tkinter.StringVar()
            self.writeData['db%d'%(k)] = varTemp
            varTemp.set("")
            entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=varTemp)
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            k += 1
            print k
            
        for j in range(0,8,2):
            entryLabel = Tkinter.Label(self.sniffFrame)
            entryLabel["text"] = "db%d:" %((k))
            entryLabel.grid(row=i+1,column=j, sticky= tk.W)
            varTemp = Tkinter.StringVar()
            self.writeData['db%d'%((k))] = varTemp
            varTemp.set("")
            entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=varTemp)
            entryWidget.grid(row=i+1,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            k +=1
    
        i += 2
       
        
        
        self.sniffFrame.grid(row=0,column=0,sticky=tk.W+tk.N,pady=0)
        return

    def buildDataCanvas(self):
        """ 
        This methods will build the left frame that contains a 
        display for information pulled off of the bus.
        """
        self.dataFrame = tk.Canvas(self.root, width=self.dataDx, height=self.dataDy)
        """ This is the frame that has all the data display on it"""
        self.dataFrame.pack(side=tk.LEFT,padx=2,pady=2,fill=tk.Y)
        
        
        #separator line
        sep = tk.Frame(self.root, height=self.dataDy,width=2,bd=1,relief=tk.SUNKEN)
        sep.pack(side=tk.LEFT,padx=2,pady=2,fill=tk.Y)
        
        self.infoFrame = tk.Frame(self.dataFrame,width=self.dataDx,height=20)
        self.infoFrame.pack(side=tk.BOTTOM, padx=2,pady=2,fill=tk.X)
        
        sep = tk.Frame(self.dataFrame,height=2,width=self.dataDx,bd=1,relief=tk.SUNKEN)
        sep.pack(side=tk.BOTTOM,padx=2,pady=2,fill=tk.X)
        
        self.statusString = tk.StringVar()
        """ This is a status update to alert the user if the GOODTHOPTER 10 is connected, in use or ready."""
        self.statusString.set("Not Connected")
        label = tk.Label(self.infoFrame,text="Status: ")
        label.grid(row=0,column=0,sticky=tk.W)
        self.statusLabel = tk.Label(self.infoFrame,textvariable=self.statusString, bg="red")
        """ The label that contains the status"""
        self.statusLabel.grid(row=0,column=1,sticky=tk.W)
        self.msgCount = tk.StringVar()
        """ This counts the number of messages received in a sniff run"""
        self.msgCount.set("0")
        self.msgPrev = time.time()
        """ This is the time received for the previous message so that we can compute the time between messaages"""
        label = tk.Label(self.infoFrame,text="Count: ")
        label.grid(row=0,column=2, sticky=tk.W)
        label = tk.Label(self.infoFrame,textvariable=self.msgCount, width=5)
        label.grid(row=0,column=3,sticky=tk.W)
        
        self.msgDelta = tk.StringVar()
        """ This Displays the time difference between the last 2 packets sniffed off the bus"""
        self.msgDelta.set("0")
        label = tk.Label(self.infoFrame,text='Delta T: ')
        label.grid(row=0,column=4,sticky=tk.W)
        label = tk.Label(self.infoFrame, textvariable=self.msgDelta)
        label.grid(row=0,column=5, sticky=tk.W)
    
        
        self.topFrame = tk.Frame(self.dataFrame,width=self.dataDx,height=4)
        """ This frame is just to provide a visual so the user knows what bytes are which in the stream of data """
        self.topFrame.pack(side=tk.TOP, padx=2,pady=2,fill=tk.X)
        label = tk.Label(self.topFrame)
        label["text"] = "\t\t\t    db0 db1 db2 db3 db4 db5 db6 db7  deltaT"; #label
        
        label.pack(side=tk.LEFT)
        
        
        
        
        
        self.dataText = tk.Text(self.dataFrame,background='white', width=self.dataDx, wrap=Tkinter.WORD)
        """ This is the actual textbox that all the packets are written to """
        self.dataText.config(state=DISABLED) # don't want the user to be able to change the data in the textbox
        self.scroll = Scrollbar(self.dataFrame)
        self.scroll.pack(side=tk.RIGHT,fill=tk.Y)
        self.dataText.configure(yscrollcommand=self.scroll.set)
        
        self.scroll.config(command=self.dataText.yview)
        self.dataText.pack(side=tk.LEFT,fill=tk.Y)
        
        # this will allow us to link to our information about our arbitration IDS
        self.hyperlink = tkHyperlinkManager.HyperlinkManager(self.dataText) 
    def addtextToScreen(self,text):
        self.dataText.config(state=NORMAL)
        self.dataText.insert(END,text);
        self.dataText.config(state=DISABLED)
    # build a frame and put controls in it
    def buildControls(self):
        """
        This method builds out the top frame bar which allows the user to switch tabs between the 
        experiments, sniff/write, MYSQL and Arbitration id tabs
        """

        # make a control frame
        self.cntlframe = tk.Frame(self.root)
        self.cntlframe.pack(side=tk.TOP, padx=2, pady=2, fill=X)

        # make a separator line
        sep = tk.Frame( self.root, height=2, width=self.initDx, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.TOP, padx = 2, pady = 2, fill=tk.Y)

        # make a cmd 1 button in the frame
        self.buttons = []
        #width should be in characters. stored in a touple with the first one being a tag
        self.buttons.append( ( 'sniff', tk.Button(self.cntlframe, \
                                    text="Sniff", command=self.sniffFrameLift,width=10)))
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ( 'experiments', tk.Button( self.cntlframe, text="Experiments", \
                                          command=self.experimentFrameLift, width=10 ) ) )
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ('Info', tk.Button(self.cntlframe, text="ID Information",\
                                                 command=self.infoFrameLift, width=15)))
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ( 'SQL', tk.Button( self.cntlframe, text="MySQL", \
                                                    command=self.sqlFrameLift, width=10)))
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ('Car Module', tk.Button(self.cntlframe, text="Car Module", \
                                                    command=self.ourCarFrameLift, width=10)))
        self.buttons[-1][1].pack(side=tk.LEFT)
        
        return

    #Bind callbacks with the keyboard/keys
    def setBindings(self):
        """
        This method will set bindings on the window. This includes mouse clicks and key presses
        """
        #self.root.bind( '<Button-1>', self.handleButton1 )
        #self.root.bind( '<Button-2>', self.handleButton2 )
        #self.root.bind( '<Button-3>', self.handleButton3 )
        #self.root.bind( '<B1-Motion>', self.handleButton1Motion )
        self.root.bind( '<Command-q>', self.handleModQ )
        self.root.bind( '<Command-s>', self.saveJsonInfo)
        self.root.bind( '<Control-z>', self.handleSettings)
        #self.root.bind( '<Command-o>', self.handleModO )
        self.root.bind( '<Control-q>', self.handleQuit )
        self.root.bind( '<Control-s>', self.sniffFrameLift)
        self.root.bind( '<Control-e>', self.experimentFrameLift)
        #only bind if MySQL is installed
        if( MYSQL_INSTALL == True):
            self.root.bind( '<Control-u>', self.sqlFrameLift)
        self.root.bind( '<Control-i>', self.infoFrameLift)
        #self.root.bind('<Return>',self.handleStim )
        #self.root.bind('<Key>',self.handleKeys)

    # this method handles inputs when the user presses a key
    def handleKeys(self,event):
        """
        This will handle an event for when a key is pressed
        """
        print event.char
    
    #quits the GUI
    def handleQuit(self, event=None):
        """ 
        This method is called when the user quits the program. It terminates the display and exits
        """
        print 'Terminating'
        self.root.destroy()
        
    def setCarModule(self,experimentFileLocation, experimentGUILocation):
        """
        This method will save the new car module file locations that can be set in the
        settings dialog box. They will be saved to the settings ini file but will not update
        the current window. The program must be restarted for changes to take effect. A warning
        will appear to indicate this.
        
        @type experimentFileLocation: String
        @param experimentFileLocation: path to the experiment file that will be part of the car module. This should be a 
                                       file that contains a class of the same name. The class is assumed to be a sub class
                                       of the experiments class. 
                                       
        @type experimentGUILocation: String
        @param experimentGUILocation: path to the experiment gui module addition. This will be a file that contains a class
                                      of the same name. This class will print the module's addition to the GUI for the user to 
                                      run the experiments included in the experimentFileLocation class.
        """
        print "here"
        print experimentFileLocation
        self.experimentFile = experimentFileLocation;
        self.experimentGUIFile = experimentGUILocation;
        self.writeiniFile(self.SETTINGS_FILE, "experimentInfo", "experimentfile", experimentFileLocation)
        self.writeiniFile(self.SETTINGS_FILE, "experimentInfo", 'experiment_gui_file', experimentGUILocation)
        tkMessageBox.showwarning('Settings Changed', \
                'Please restart to use new car module')
        
        
    def setDataManage(self,table, name, host, username, password, database):
        """
        This method will update the stored information for accessing the MYSQL database. 
        The settings will be saved to the settings file.
        
        @type table: string
        @param table: SQL table to add data to
        @type name: string
        @param name: Name for SQL account
        @type host: string
        @param host: Host for MYSQL table
        @type username: string
        @param username: MYSQL username
        @type password: string
        @param password: MYSQL username password
        @type database: string
        @type database: database we want to use
        
        """
        print "Updating MYSQL database information"
        
        self.SQL_NAME = name
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_name", name)
        self.SQL_HOST = host
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_host", host)
        self.SQL_USERNAME = username
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_username", username)
        self.SQL_PASSWORD = password
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_password", password)
        self.SQL_DATABASE = database
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_database", database)
        self.SQL_TABLE = table
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_table", table)
        self.dm = DataManage(host=self.SQL_HOST,\
                             db=self.SQL_DATABASE, \
                             username=self.SQL_USERNAME, \
                             password=self.SQL_PASSWORD,\
                             table=self.SQL_TABLE,\
                             dataLocation=self.DATA_LOCATION)


    def handleSettings(self, event=None):
        """
        This method will open the settings dialog box for the user to change various components of the GUI.
        """
        data = {}
        dialogBox =  settingsDialog(parent = self.root, dClass = self, data=data, title = "Settings")
        
    #quits
    def handleModQ(self, event):
        """ 
        This method will quit the GUI
        """
        self.handleQuit()
    
    def setRunning(self):
        """
        This method sets the running boolean when a method is communicating with the bus
        """
        self.running.set(1)
    
    def unsetRunning(self):
        """
        This method unsets the running boolean when a method is done communicating with the bus
        """
        self.running.set(0)

    def getRate(self):
        """
        This method returns the rate that the GOODTHOPTER10 is set to
        """
        return self.freq
    
    def testConnect(self):
        """ this is to test module files """
        if( self.experimentFile != None):
            
            pathInd = string.rfind(self.experimentFile,"/")
            path = self.experimentFile[:pathInd+1]
            #do not want the / and don't wan the .py
            sys.path.insert(0, path) #add path to file
            classFile = self.experimentFile[pathInd+1:-3]
                
            guipathInd = string.rfind(self.experimentGUIFile,"/")
            path = self.experimentGUIFile[:guipathInd+1]
            classFileName = self.experimentGUIFile[guipathInd+1:-3]
            sys.path.insert(0,path)
            importClasses = [classFile, classFileName]
                
                 
            self.mod = map(__import__, importClasses)
            print self.mod
            # need to get class name
            fn = getattr(self.mod[0],classFile)
            assert callable(fn), "Class is not the same name as file given!"
            #get class for GUI addition
            self.ourCarGuiClass = getattr(self.mod[1],classFileName)
            assert callable(self.ourCarGuiClass), "Class is not the same as file given!"
            #self.comm = self.mod[0].FordExperimennts(self.DATA_LOCATION)
            print fn
            self.comm = fn(self.DATA_LOCATION)
                
            print "connected"
            self.statusLabel.config(bg="green")
            self.statusString.set("Ready")
            self.CarExtention = True
            self.buildCarModule() #build the frame
            for bt in self.buttons:
                if( bt[0] == 'Car Module'):
                    bt[1].config(state=tk.NORMAL)
                
            
        
        try:
            #self.comm = GoodFETMCPCANCommunication()
            self.comm = FordExperiments(self.DATA_LOCATION)
            #self.comm = experiments(self.DATA_LOCATION)
            """ Stores the communication with the CAN class methods """
            self.statusLabel.config(bg="green")
            self.statusString.set("Ready")
        except:
            print "Board not properly connected. please connect and reset"
            self.comm = None
            self.statusLabel.config(bg="red")
            self.statusString.set("Not Connected")

    def connectBus(self):
        """ 
        This method will try to reconnect with the GOODTHOPTER10. 
        It will first check to make sure that no
        method is currently communicating with the bus. 
        """
        if( self.experimentFile != None and self.experimentFile != ""):
            try:
                pathInd = string.rfind(self.experimentFile,"/")
                path = self.experimentFile[:pathInd+1]
                #do not want the / and don't wan the .py
                sys.path.insert(0, path) #add path to file
                classFile = self.experimentFile[pathInd+1:-3]
                    
                guipathInd = string.rfind(self.experimentGUIFile,"/")
                path = self.experimentGUIFile[:guipathInd+1]
                classFileName = self.experimentGUIFile[guipathInd+1:-3]
                sys.path.insert(0,path)
                importClasses = [classFile, classFileName]
                    
                     
                self.mod = map(__import__, importClasses)
                print self.mod
                # need to get class name
                fn = getattr(self.mod[0],classFile)
                assert callable(fn), "Class is not the same name as file given!"
                #get class for GUI addition
                self.ourCarGuiClass = getattr(self.mod[1],classFileName)
                assert callable(self.ourCarGuiClass), "Class is not the same as file given!"
                #self.comm = self.mod[0].FordExperimennts(self.DATA_LOCATION)
                print fn
                self.comm = fn(self.DATA_LOCATION)
                    
                print "connected"
                self.statusLabel.config(bg="green")
                self.statusString.set("Ready")
                self.CarExtention = True
                self.buildCarModule() #build the frame
                for bt in self.buttons:
                    if( bt[0] == 'Car Module'):
                        bt[1].config(state=tk.NORMAL)
                
            except:
                tkMessageBox.showwarning('Unable to import Car Specific Module', \
                'Unable to import the following modules included in settings:\n %s \n and\n %s'%(self.experimentFile, self.experimentGUIFile))
                for bt in self.buttons:
                    if( bt[0] == 'Car Module'):
                        bt[1].config(state=tk.DISABLED)
            else:
                return
        
        try:
            #self.comm = GoodFETMCPCANCommunication()
            self.comm = FordExperiments(self.DATA_LOCATION)
            #self.comm = experiments(self.DATA_LOCATION)
            """ Stores the communication with the CAN class methods """
            self.statusLabel.config(bg="green")
            self.statusString.set("Ready")
        except:
            print "Board not properly connected. please connect and reset"
            self.comm = None
            self.statusLabel.config(bg="red")
            self.statusString.set("Not Connected")
        

    def checkComm(self):
        """
        This method check to see if the program is able to begin 
        communication with the GOODTHOPTER10 board. This method
        should be called before anything begins to try and communicate. 
        It will check first to see if the board is connected
        and will then check to see if the self.running boolean is set or not.
        
        @rtype: Boolean
        @return: False if the board is either not connected or if there is 
                 currently a script communicating with the board. True otherwise
        """
        if(not self.isConnected() ):
            print "GoodThopter10 not connected. Please connect board"
            return False
        
        elif( self.running.get() == 1 ):
            print  "There is a current script running. Please wait until it has finished"
            return False
        
        return True
    
    def getExperimentFileLocations(self):
        return [self.experimentFile, self.experimentGUIFile]
    
    def getDataLocation(self):
        """
        Returns the path to the data location
        @rtype: string
        @return: Data location path
        """
        return self.DATA_LOCATION
    
    def setDataLocation(self, location):
        """
        Sets the data location path in the program as well as saved to the settings file.
        @type location: string
        @param location: path to new location to save data to
        """
        print "Updating Data Location"
        self.writeiniFile(self.SETTINGS_FILE, "FileLocations", "data_location", location)
        self.DATA_LOCATION = location
        
    
    #set the rate on the MC2515
    def setRate(self,freq):
        """
        This method will set the rate that the board communicates with  the CAN Bus on. 
        @type freq: number
        @param freq: Frequency of CAN communication
        """
        print "Updating Bus Rate"
        if( not self.checkComm()):
            return
        self.writeiniFile(self.SETTINGS_FILE, "BusInfo", "frequency", freq)
        self.comm.setRate(freq)
        self.freq = freq
        
    # This method will clear all the filter inputs for the user
    def clearFilters(self):
        """
        This method will clear the filters that the user has input into the dialog spots. 
        It does not reset the chip and clear them on the board.
        """
        for element in self.filterIDs:
            element.set("")
    
    
    def sniff(self):
        """ 
        This method will sniff the CAN bus. It will take in the input 
        arguments from the GUI and pass them onto the sniff method in the 
        L{GoodFETMCPCANCommunication.sniff} file. The method will take in any 
        filters that have been set on the GUI, as well as the sniff length and 
        comment off the display. This method will call L{sniffControl} which
        will be run as a thread.
        """
        if( not self.checkComm() ):
            return
        # get time and check that it is correct
        try:
            time = int(self.time.get())
        except:
            print "time in seconds as an integer"
        comments = self.comment.get()
        description = comments
        standardid = []
        # Get the filter IDs and check to see if they are correctly an integer
        for element in self.filterIDs:
            if(element.get()==""):
                continue
            try:
                standardid.append(int(element.get()))
            except:
                tkMessageBox.showwarning('Invalid Input', \
                'Incorrectly formatted input. Values are not Integers')
                print "Incorrectly formatted filters!"
                return
        if( len(standardid) == 0): # if there are no filters
            standardid = None
        
        #figure out if the data gathered will be saved
        if( self.saveInfo.get() == 1):
            writeToFile = True
        else:
            writeToFile = False
        
        self.data = Queue.Queue()
    
        self.deltas = {}
        #sniff thread
        thread.start_new_thread(self.sniffControl, (self.freq, time, description, \
                                                    False, comments, None, standardid, \
                                                    False, False, True, self.data, writeToFile )) 
        
        
        
    def sniffControl(self,freq,duration,description, verbose=False, comment=None, \
                     filename=None, standardid=None, debug=False, faster=False, \
                     parsed=True, data = None, writeToFile = True):
        """
        This method will actively do the sniffing on the bus. It will call 
        L{GoodFETMCPCANCommunication.sniff}. This method will be called by the L{sniff}
        method when started by the user in the GUI. It will set up the display for the
        incoming sniffed data as well as reset the counters. The input parameters to 
        this method are the same as to the sniff method in the GoodFETMCPCANCommunication class.
        
        @type freq: number
        @param freq: Frequency of the CAN communication
        
        @type description: string
        @param description: This is the description that will be put in the csv file. 
                            This gui will set this to be equal to the comments string
                            
        @type verbose: Boolean
        @param verbose: This will trigger the sniff method to print out to the terminal. 
                        This is false by default since information is printed to the GUI. 
                        
        @type comment: string
        @param comment: This is the comment tag for the observation. This will be saved 
                        with every sniffed packet and included in the data uploaded to the SQL database
                        
        @type filename: String
        @param filename: filename with path to save the csv file to of the sniffed data. 
                         By default the sniff method in the GoodFETMCPCANCommunication file will 
                         automatically deal with the file management and this can be left as None.
                         
        @type standardid: List of integers
        @param standardid: This will be a list of the standard ids that the method will filter for. 
                           This can be a list of up to 6 ids.
        @type debug: Boolean
        @param debug: 
        
        """
        
        #reset msg count
        self.msgCount.set("0") # reset the count
        self.msgDelta.set("0") # reset the delta time
        self.msgPrev = time.time() # reset the previous for the delta time
        self.dataText.config(state=tk.NORMAL) 
        self.dataText.delete(1.0, END) # clear the text box for the data
        self.dataText.config(state=tk.DISABLED)
        self.setRunning() # we are now communicating with the bus
        self.updateID = self.root.after(50,self.updateCanvas) # set the event to update the canvas every 50 ms
        #call the actual sniff method in 
        count = self.comm.sniff(self.freq, duration, description, verbose, comment, \
                                filename, standardid, debug, faster, parsed, data, writeToFile)
        self.unsetRunning()
        #self.root.after_cancel(self.updateID)
     
    def updateStatus(self,name,index,mode):
        """
        This method will update the status indicator for the user in the bottom 
        of of the data Frame. This will tell the user whether
        the bus is actively being communicated with, if the board is disconnected, 
        or if it is ready to go. There is no checking for if somebody
        disconnects the board after it has been connected.
        """
        runningVal = self.running.get()
        if( runningVal == 1): # we are communicating
            self.statusString.set("Running")
            self.statusLabel.config(bg = "yellow")
        if( runningVal == 0): # board is connected and ready to run
            if( self.comm != None):
                self.statusString.set("Ready")
                self.statusLabel.config(bg="green")
        
    
    def updateCanvas(self):
        """
        This method will update the data to be displayed on the screen (in the text box)
        to the user. It will get the data form the queue that the L{GoodFETMCPCANCommunication.sniff}
        method was passed. These packets are then printed to the screen in either
        a fixed or rolling viewpoint. Rolling meaning that each packet is given it's own 
        line while fixed means that each ID has it's own
        line and that line is updated with each new packet. These can be changed during a sniff run.
        """
        choice = self.SniffChoice.get()
         # we have changed views. delete the text box content and start reading
        if( choice == 'Rolling' and self.fixedView == True):
            self.fixedView = False
            self.delta = {}
            self.dataText.config(state=tk.NORMAL)
            self.dataText.delete(1.0,END)
            self.dataText.config(state=tk.DISABLED)
        elif( choice == 'Fixed' and self.fixedView ==False):
            self.fixedView = True
            self.delta = {}
            self.dataText.config(state=tk.NORMAL)
            self.dataText.delete(1.0,END)
            self.dataText.config(state=tk.DISABLED)
        
        # while there are still data packets in the Queue:
        while(not self.data.empty()):
            #get the packet
            try:
                packet = self.data.get_nowait()
            except Queue.Empty: #if the packet is empty, just continue and exit.
                pass
            else: # we have grabbed a packet, now update the displays
                sID = packet.get('sID')
                #check to see if we have seen this before
                if( self.deltas.get(sID) == None): 
                    #we have not seen this ID before
                    print "cannot find id"
                    #create a new dictionary for the arb id
                    self.deltas[sID] = {'time':packet.get("time")} 
                    sIDDic = self.deltas.get(sID)
                    delta = -1
                else:
                    #we have seen this id before, update the delta time
                    sIDDic = self.deltas.get(sID);
                    
                    delta = packet['time'] - sIDDic['time'] #get the delta time
                    sIDDic['time'] = packet['time']
                    
                #parse and display the packet
                rtr = packet.get('rtr')
                length = packet.get('length')
                data = ""
                for i in range(0,length):
                    dbidx = 'db%d'%i
                    data += " %03d"%packet[dbidx]
                    
                #get position of the scrollbar
                position = self.scroll.get()[1]
                positionT = self.dataText.yview()[0]
                
                if( self.fixedView == True):
                    #we need to add the arbID (doesn't already exist)
                    lineNum = sIDDic.get('lineNum')
                    if( lineNum == None):
                        # The packet doesn't already have a line, add it to the end
                        numlines = self.dataText.index('end - 1 line').split('.')[0] #get number of lines
                        print numlines
                        sIDDic['lineNum'] = float(numlines)
                        lineNum = float(numlines)
                    else:
                        # The packet has already been added before,
                        # we need to delete the line that was the old packet
                        self.dataText.config(yscrollcommand=None, state=NORMAL)
                        self.dataText.delete(lineNum, lineNum+1) #delete the previous entry for this id
                    self.dataText.config(yscrollcommand=None, state=NORMAL)
                    self.dataText.insert(lineNum, (" Length: %d rtr: %d "%(length,rtr)) + \
                                                           data + (" DeltaT: %04f\n"%delta))
                    #this provides a link for the user to click
                    self.dataText.insert(lineNum, "%04d"%sID, self.hyperlink.add(self.arbIDInfo,sID)) 
                    self.dataText.insert(lineNum,"arbID: ");
                        
                else:
                    #rolling view, add the packet to the end
                    self.dataText.config(yscrollcommand=None, state=NORMAL)
                    self.dataText.insert(END,"arbID: ")
                    self.dataText.insert(END, "%04d"%sID, self.hyperlink.add(self.arbIDInfo,sID))
                    self.dataText.insert(END, (" Length: %d rtr: %d "%(length,rtr)) + data + \
                                                                    (" DeltaT: %04f\n"%delta))
                #self.text.yview(END)
                self.dataText.config(yscrollcommand=self.scroll.set, state=DISABLED)
                #if the position was at the end, update it now now be at the end again
                if (position ==1.0):
                    self.dataText.yview(END)
                #set the delta time and packet count
                self.msgDelta.set("%04f"%(packet['time']-self.msgPrev))
                self.msgPrev = packet['time']
                self.msgCount.set("%d"%(int(self.msgCount.get())+1))
        #if we are still gathering data call this method again in 50ms
        if(self.running.get() == 1):
           self.updateID = self.root.after(50,self.updateCanvas)
        
  
            
  #  def callback(self):
  #      self.arbIDInfo(id)
            
    def arbIDInfo(self,id):
        """ 
        This method is called when the user clicks on an arbID in the data textboxes. 
        It will open up the data information frame (on the RightSideFrame) and display
        our knowledge of this arbitration ID to the user
        """
        print "Request for information on %d" %id
        
        self.IDchoice.set("%d"%id)
        
        
        
        
        
    def loadJson(self):
        """
        This method will load our packet informtion from the 
        Json file specified in the settings.
        """
        #self.packetInformationFileData = self.dm.loadJson(self.packetInformationFile)['Arbitration Ids']
        self.packetInformationFileData = self.dm.loadJson(self.packetInformationFile)

        
        
        
    def write(self):
        """
        This method handles injecting packets onto the bus. It will load the user 
        inputs with very basic error checking. It will then call writeControl in a thread.
        This method will call L{GoodFETMCPCANCommunication.spit} if not writing from a file
        and will call L{GoodFETMCPCANCommunication.writeData} if we are reading in data from
        a file first.
        """
        #check to see if anything is running on the bus
        if( not self.checkComm()):
            return
        packet = []
        #if we are writing from a file we take no user inputs
        if(self.writeData["fromFile"].get() == 1):
            # ping the user to choose the file for writing
            filename = askopenfilename(title="Choose a File to Load Packet Data")
            data = self.dm.readWriteFileDEC(filename)
            #check that we have data
            if( data == None):
                print "Failed to load file"
                return
            #write the data
            self.comm.writeData(data,self.freq)
            return
        #otherwise gather data from the GUI for writing
        else:
            #attempt to get user input
            try:
                sID = int(self.writeData["sID"].get())
                print "here1"
                writes = int(self.writeData["writes"].get())
                if(writes == 0):
                    repeat = False
                else:
                    repeat = True
                #print "sid"
                periodStr = self.writeData["period"].get()
                if( periodStr == ""):
                    period = None
                else:
                    period = float(periodStr)
                   
                if( self.writeData["rtr"].get() == 1):
                    packet = None
                else:
                    for j in range(0,8):
                        #print "db%d"%j
                        var = self.writeData.get("db%d"%j)
                        packet.append(int(var.get()))
            except:            
                tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input. Values are not Integers')
                print "Invalid input!"
                return
            
            thread.start_new_thread( self.writeControl, (self.freq,[sID], repeat, writes, period, False, packet))
     
     
     # This is the method that will be called as a thread to write to the bus
    def writeControl(self, freq, sID, repeat, writes, period, debug=False, packet=None): 
         """ 
        This method will spit a single message onto the bus. If there is no packet information 
        provided then the message will be sent as a remote transmission request (RTR). 
        The packet length is assumed to be 8 bytes The message can be repeated a given number of times with
        a gap of period (milliseconds) between each message. This will continue for the the 
        number of times specified in the writes input. This method does not include bus setup, it must be 
        done before the method call. This method will do this by calling L{GoodFETMCPCANCommunication.spit} to 
        inject the message onto the bus.
        
        
        @type freq: number
        @param freq: The frequency of the bus
        
        @type sID: list of integer
        @param sID: This is a single length list with one integer elment that corresponds to the 
                    standard id you wish to write to
        
        @type repeat: Boolean
        @param repeat: If true the message will be repeatedly injected. if not the message will 
                       only be injected 1 time
        
        @type writes: Integer
        @param writes: Number of writes of the packet
        
        @type period: Integer
        @param period: Time delay between injections of the packet in Milliseconds
        
        @type debug: Boolean
        @param debug: When true debug status messages will be printed to the terminal
        
        @type packet: List
        @param packet: Contains the data bytes for the packet which is assumed to be of length 8. 
                       Each byte is stored as an integer and can range from 0 to 255 (8 bits). 
                       If packet == None then an RTR will be sent on the given standard id.
        
        """
         self.comm.spitSetup(self.freq)
         self.setRunning()
         self.comm.spit(self.freq,sID,repeat, writes, period=period, debug=False, packet=packet)
         self.unsetRunning()
              


        
    def uploaddb(self):
        """
        This method will upload all files that have been sniffed to the designated folder 
        L{self.DATA_LOCATION} to the MYSQL data base that was specified in the settins.
        See L{DataManage.uploadFiles} for more information.
        
        """
        msg = "Upload data to table: %s, \n you are at frequency: %.2f"%(self.SQL_TABLE,self.freq)
        #double check that the user wants to upload
        response = tkMessageBox.askyesno(title = "Upload Data", message = msg)
        
        if(response):
            print "Uploading all files"
            self.dm.uploadFiles()
    
    def infoFrameLift(self, event=None):
        """
        This method is used in the tabbing of the right side frames. 
        This will lift the arbitration id info frame to the top
        for the user to see. It will also move all the other frames 
        form visability by moving the blank canvas up to the second
        to top frame.
        
        """
        tk.Misc.lift(self.blankCanvas,aboveThis=None)
        tk.Misc.lift(self.infoFrame,aboveThis=None)
            
    def sqlFrameLift(self, event=None):
        """
        This method is used in the tabbing of the right side frames. This will lift the MYSQL frame to the top
        for the user to see. It will also move all the other frames form visability by moving the blank canvas up to the second
        to top frame.
        
        """
        tk.Misc.lift(self.blankCanvas,aboveThis=None)
        tk.Misc.lift(self.sqlFrame,aboveThis=None)
        
    def sniffFrameLift(self, event=None):
        """
        This method is used in the tabbing of the right side frames. This will lift the SNIFF/WRITE frame to the top
        for the user to see. It will also move all the other frames form visability by moving the blank canvas up to the second
        to top frame.
        
        """
        tk.Misc.lift(self.blankCanvas,aboveThis=None)
        tk.Misc.lift(self.sniffFrame, aboveThis=None)
        
        
    def experimentFrameLift(self, event=None):
        """
        This method is used in the tabbing of the right side frames. This will lift the experiment frame to the top
        for the user to see. It will also move all the other frames form visability by moving the blank canvas up to the second
        to top frame.
        
        """
        tk.Misc.lift(self.blankCanvas,aboveThis=None)
        tk.Misc.lift(self.experimentFrame,aboveThis=None)
        
    def ourCarFrameLift(self, event = None):
        tk.Misc.lift(self.blankCanvas, aboveThis = None)
        tk.Misc.lift(self.carFrame,aboveThis = None) 
    
    def idInfo(self):
        """ This method will open an info box for the user
            to gain information on a known arbID"""
        infoBox = info(parent=self.root, title="Information Gathered")
        pass
        
    def sqlQuery(self):
        """
        This method will take in the user's inputed MYSQL query and query the database for it. 
        When the user is saving to a .pcap the user must get the full message and therefore 
        can only specify the second half of the MYSQL query and the first part::
        
            SELECT msg FROM table where 
        
        will be added automatically. This does not happen with the csv option where the user 
        can query whatever they want. BE CAREFUL there is no
        error checking or prevention from querying something bad that could delete information. 
        Data will be saved to the MYSQL location
        specified by the DataManage class, L{self.dm}. This is self.DATA_LOCATION/SQLData/.
        """
        cmd = self.text.get(1.0,END)
        #check to see if there was any input
        if (cmd == chr(10)):
            print "No query input!"
            return
        
        filename = self.queryFilename.get()
        #make sure there is a directory for the file
        DATALOCATION = self.dm.getSQLLocation()
        now = datetime.datetime.now()
        datestr = now.strftime("%Y%m%d")
        path = DATALOCATION + datestr
        if(not os.path.exists(path)): 
            #folder does not exists, create it
            os.mkdir(DATALOCATION+datestr)
        #create full path relative to this folder
        filename = path + "/" + filename
        #The two different choices are different number of letters
        #but we want to ensure that we remove just the .file extention
        if( choice == 'csv'):
            filenameL = filename[:-4]
            filenameR = filename[-4:]
        else:
            filenameL = filename[:-5]
            filenameR = filename[-5:]
        if( os.path.exists(filename)):
            filename2 = filenameL+"_1"+filenameR
            i=2
            #find the first unused filename
            while( os.path.exists(filename2)):
                filename2=filenameL+("_%d" %i)+filenameR
                i+=1
            filename=filename2
            print "file already exists name changed to %s" % filename
        choice = self.sqlChoice.get()
        #different queries based on filetype
        if( choice == 'csv'):
            data = self.dm.getData(cmd)
            self.dm.writeDataCsv(data,filename)
        else:
            cmd = ("Select msg from %s where "%self.SQL_TABLE) + cmd
            data = self.dm.getData(cmd)
            self.dm.writetoPcapfromSQL(filenameWriteto=filename,results=data)
          
    def isConnected(self):
        """
        This method checks to see if the GOODTHOPTER10 is connected
        """
        return self.comm != None

    def handleCmd1(self):
        print "handling cmd1"
        return
    def handleCmd2(self):
        print "handling cmd2"
        return
    def handleCmd3(self):
        print "handling cmd3"
        return
    
    def generalFuzz(self):
        """
        This method grabs user input to perform a general fuzz. Loose error checking 
        is performed to ensure that the data
        is of the correct format but it is not exhaustive. See L{generalFuzzControl} 
        for more information on generalFuzz.
        
        """
        if( not self.checkComm()):
            return
        try: #make sure the data is the correct form
            Fuzzes = int(self.generalFuzzData["Fuzzes"].get())
            period = float(self.generalFuzzData["period"].get())
            writesPerFuzz = int(self.generalFuzzData["writesPerFuzz"].get())
        except:            
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input. Values are not Integers')
            print "Invalid Input. Please check input and try again"
            return
        
        thread.start_new_thread(self.generalFuzzControl, \
                                (self.getRate(),Fuzzes,period,writesPerFuzz))
        
    def generalFuzzControl(self, freq,Fuzzes, period, writesPerFuzz):
        """
        The method will inject properly formatted, randomly generated messages at a 
        given period for a I{writesPerFuzz} number of times. A new random standard id will 
        be chosen with each newly generated packet. IDs will be chosen from the full
        range of potential ids ranging from 0 to 4095. The packets that are injected
        into the bus will all be saved in the following path
        DATALOCATION/InjectedData/(today's date (YYYYMMDD))_GenerationFuzzedPackets.csv. 
        An example filename would be 20130222_GenerationFuzzedPackets.csv
        Where DATALOCATION is provided when the class is initiated. The data will be saved 
        as integers. This method will call L{experiments.generalFuzz} to perform this
        Each row will be formatted in the following form::
                     row = [time of injection, standardID, 8, db0, db1, db2, db3, db4, db5, db6, db7]
        
        @type  freq: number
        @param freq: The frequency at which the bus is communicating
        @type period: number
        @param period: The time gap between packet inejctions given in milliseconds
        @type writesPerFuzz: integer
        @param writesPerFuzz: This will be the number of times that each randomly generated packet will be injected onto the bus
                              before a new packet is generated
        @type Fuzzes: integer
        @param Fuzzes: The number of packets to be generated and injected onto bus
        
        @rtype: None
        @return: This method does not return anything
                         
        """
        self.setRunning()
        self.comm.generalFuzz(freq,Fuzzes,period,writesPerFuzz)
        self.unsetRunning()
        
    def packetResponse(self):
        """
        This method compiles the user input for running the Packet Response method. This will
        perform loose error checking to ensure that the messages are the correct type, it will
        then pass all the information on as a thread to L{packetResponseControl}. See this method
        for more information.
        
        """
        if( not self.checkComm()):
            return
        try:
            time = int(self.packetResponseData['time'].get())
            repeats = int(self.packetResponseData['repeats'].get())
            period = float(self.packetResponseData["period"].get())
            responseID = int(self.packetResponseData['responseID'].get())
            listenID = int(self.packetResponseData['listenID'].get())
            responsePacket = []
            listenPacket = []
            for k in range(0,8):
                idx_listen = 'Listen_db%d'%k
                idx_response = 'Response_db%d'%k
                listenStr = self.packetResponseData[idx_listen].get()
                if( listenStr == ""):
                    listenPacket = None
                else:
                    listenPacket.append(int(listenStr))
                        
                responsePacket.append(int(self.packetResponseData[idx_response].get()))
                    
        except:
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input.')
            returns
        #start thread
        thread.start_new_thread(self.packetResponseControl, (self.getRate(), \
                                                             time,repeats,period,responseID,\
                                                             responsePacket,listenID,listenPacket))
        
    def packetResponseControl(self, freq, time, repeats, period,  responseID, \
                                                        respondPacket,listenID, listenPacket = None):
        """
        This method will allow the user to listen for a specific packet and then respond 
        with a given message. If no listening packet is included then the method will only 
        listen for the id and respond with the specified packet when it receives a message 
        from that id. This process will continue for the given amount of time (in seconds). 
        and with each message received that matches the listenPacket and ID the transmit message
        will be sent the I{repeats} number of times at the specified I{period}. This message assumes
        a packet length of 8 for both messages, although the listenPacket can be None. This
        method will call L{experiments.packetRespond} to perform this experiment. 
        
        @type freq: number
        @param freq: Frequency of the CAN bus
        @type time: number
        @param time: Length of time to perform the packet listen/response in seconds.
        @type repeats: Integer
        @param repeats: The number of times the response packet will be injected onto the bus 
                        after the listening criteria has been met.
        @type period: number
        @param period: The time interval between messages being injected onto the CAN bus. 
                       This will be specified in milliseconds
        @type responseID: Integer
        @param responseID: The standard ID of the message that we want to inject
        @type respondPacket: List of integers
        @param respondPacket: The data we wish to inject into the bus. In the format where 
                              respondPacket[0] = databyte 0 ... respondPacket[7] = databyte 7
                              This assumes a packet length of 8.
        @type listenID: Integer
        @param listenID: The standard ID of the messages that we are listening for. When we 
                         read the correct message from this ID off of the bus, the method will
                         begin re-injecting the responsePacket on the responseID
        @type listenPacket: List of Integers
        @param listenPacket: The data we wish to listen for before we inject packets. This will 
                             be a list of the databytes, stored as integers such that
                             listenPacket[0] = data byte 0, ..., listenPacket[7] = databyte 7. 
                             This assumes a packet length of 8. This input can be None and this
                             will lead to the program only listening for the standardID and injecting 
                             the response as soon as any message from that ID is given
        """
        
        self.setRunning()
        self.comm.packetRespond(freq, time,repeats,period,responseID,\
                                respondPacket,listenID,listenPacket)
        self.unsetRunning()
        
    def reInjectFuzzed(self):
        """
        This method compiles user input to be able to re-inject packets that were 
        injected as part of the fuzzing methods. There is loose
        error checking to ensure that the data is of the correct type 
        but is not very exhaustive. This method will then call L{reInjectFuzzed}
        as a thread to perform this action. See this method for more information on what it does.
        
        The date is input in the form YYYYMMDD. This is used to find the name of the file that contains 
        the fuzzed data that we are looking for.
        
        The startTime and endTime are input in the form HHMM. These are then converted to timestamp form. 
        """
        
        if( not self.checkComm()):
            return
        try:
            date = self.reInjectData["date"].get();
            if( date == ""):
                raise Exception
            startTimestr = self.reInjectData['startTime'].get()
            if( startTimestr == ""):
                startTime = None
            else:
                #startTime = int(startTimestr)
                #put it into time stamp format: tuple( year, month, day, hour, min, sec, wday,yday,isdst) -- leave the last ones 0
                startTime = float(time.mktime((int(date[0:4]), int(date[4:6]), int(date[6:8]),\
                                                int(startTimestr[0:2]), int(startTimestr[2:4]),0,0,0,0)))
            endTimestr = self.reInjectData['endTime'].get()
            if( endTimestr == ""): #if they did not input an end time (optional)
                endTime = None
            else:
                
                endTime = float(time.mktime((int(date[0:4]), int(date[4:6]), int(date[6:8]),\
                                              int(endTimestr[0:2]), int(endTimestr[2:4]),0,0,0,0)))
            idstr = self.reInjectData['sID'].get()
            if( idstr == ""): # they did not input an id (optional)
                id = None
            else:
                id = int(idstr)  
            
        except:
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input.')
            print "Invalid Input!"
            return
        injectLocation = self.dm.getInjectedLocation() #returns the path to the location where the file is
        filename = injectLocation + date + "_GenerationFuzzedPackets.csv"
#        print "filename ", filename
#        print "date ", date
#        print "id ", id
#        print " startTime ", startTime
#        print " endTime ", endTime

        # start a new thread
        thread.start_new_thread(self.reInjectFuzzedControl, (filename, startTime, endTime,id))
        
        
    def reInjectFuzzedControl(self, filename, startTime = None,endTime = None,id = None):
        """
        This method will re-inject data that was already injected to the bus as part of a Fuzzing method. 
        This will load the data searching for the specified arbID that it was given. The reInjectFuzzed will
        take the user's input of the date to find the filename that will contain the packets. 
        The other inputs are optional. If startTime is provided this will only re-inject messages that were
        written after the given time until the endTime (if specified). If the 
        endTime is not specified then it will re-inject all packets from the startTime (or start of file) to 
        the end of the file. Likewise the user could also specify the id to search for. if the id is specified 
        then this method will only re-inject packets that had this id.
        
        @type filename: String
        @param filename: path to the inejction file that we are going to read our data from
        
        @type startTime: timestamp
        @param startTime: Optional parameter that specifies an earliest injection time for packets to be re-injected
        
        @type endTime: timestamp
        @param endTime: Optional parameter that specifies the lastest injection time for packets to be re-injected
        
        @type id: Integer
        @param id: Optional parameter that specifies a specific arbitration id that we want to re-inject
        """
        self.setRunning()
        #load the data from the file
        data = self.dm.readInjectedFileDEC(filename,startTime,endTime,id)
        #inject the data 
        self.comm.writeData(data,self.freq)
        self.unsetRunning()
        
        
    def GenerationFuzz(self):
        """
        This method takes in the user inputs to perform generation fuzzing. There is loose error 
        checking to ensure that data is of the right type but little else. This method then calls 
        L{GenerationFuzzControl} as a thread. See this method for more information on 
        how it works.   
        """
        #print "Generation Fuzz"
        if( not self.checkComm()):
            return
        #sIDs = int(self.fuzzData['sID'].get())
        try:
            ids = self.fuzzData['sIDs'].get().split(",")
            sID = []
            for id in ids:
                sID.append(int(id))
            period = int(self.fuzzData['period'].get())
            writesPerFuzz = int(self.fuzzData['writesPerFuzz'].get())
            Fuzzes = int(self.fuzzData['Fuzzes'].get())
            dbInfo = {}
            for i in range(0,8):
                idx = 'db%d'%i
                dbValues = self.fuzzData.get(idx)
                dbInfo[idx] = [int(dbValues[0].get()), int(dbValues[1].get())]
        except:
            print "Invalid Input."
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input.')
            return
        #start the writing as a thread
        #self.GenerationFuzzControl(self.getRate(),sID,dbInfo,period,writesPerFuzz,Fuzzes)
        thread.start_new_thread(self.GenerationFuzzControl,(self.getRate(),sID, \
                                             dbInfo,period,writesPerFuzz,Fuzzes))
        
    def GenerationFuzzControl(self,freq, sID, dbInfo, period, writesPerFuzz, Fuzzes):
        """
        This method will perform generation based fuzzing on the bus. The method will inject
        properly formatted, randomly generated messages at a given period for a I{writesPerFuzz} 
        number of times. This method will call L{experiments.generationFuzzer} to perform this.
       
        
        
        The packets that are injected into the bus will all be saved in the following path
        DATALOCATION/InjectedData/(today's date (YYYYMMDD))_GenerationFuzzedPackets.csv. 
        An example filename would be::
        
                    20130222_GenerationFuzzedPackets.csv 
        
        Where DATALOCATION is provided when the class is initiated. 
        The data will be saved as integers. Each row will be formatted in the following form::
                     row = [time of injection, standardID, 8, db0, db1, db2, db3, db4, db5, db6, db7]
        
        @type  freq: number
        @param freq: The frequency at which the bus is communicating
        @type sID: list of integers
        @param sID: List of standard IDs the user wishes to fuzz on. An ID will randomly 
                            be chosen with every new random packet generated. If only 1 ID 
                            is input in the list then it will only fuzz on that one ID.
        @type  dbInfo: dictionary
        @param dbInfo: This is a dictionary that holds the limits of each bytes values. 
                         Each value in the dictionary will be a list containing the lowest 
                         possible value for the byte and the highest possible value. The form 
                         is shown below::
                            
                            dbInfo['db0'] = [low, high]
                            dbInfo['db1'] = [low, high]
                            ...
                            dbInfo['db7'] = [low, high] 
        
        @type period: number
        @param period: The time gap between packet inejctions given in milliseconds
        @type writesPerFuzz: integer
        @param writesPerFuzz: This will be the number of times that each randomly 
                              generated packet will be injected onto the bus
                              before a new packet is generated
        @type Fuzzes: integer
        @param Fuzzes: The number of packets to be generated and injected onto bus
        
        @rtype: None
        @return: This method does not return anything
                         
        """
        self.setRunning()
        self.comm.generationFuzzer(freq, sID,dbInfo, period, writesPerFuzz, Fuzzes)
        self.unsetRunning()
        
    def RTRsweepID(self):
        """
        This method takes in user inputs for a RTR sweep experiment. 
        There is loose error checking to ensure
        that the input data is of the right type but not very secure checking. 
        This will perform the RTR experiment
        by calling L{RTRsweepIDControl}. See this for more information on the method.
        """
        print "Sweep across given IDs requesting packets"
        if( not self.checkComm()):
            return
        sniffTime = self.sniffTime.get()
        low = self.lowSweep.get()
        high = self.HighSweep.get()
        attempts = self.attempts.get()
        verbose = True
        try: 
            sT = int(sniffTime)
            lowI = int(low)
            highI = int(high)
            attemptsI = int(attempts)
        except:
            tkMessageBox.showwarning('Invalid Input', \
                        'Incorrectly formatted input. Values are not Integers')
            print "Values are not integers. Please check inputs and try again."
            return
        thread.start_new_thread(self.RTRsweepIDControl, (self.getRate(), lowI,highI,attemptsI,sT,verbose))
 
    def RTRsweepIDControl(self, freq, lowI, highI,attemptsI, sT, verbose):
        """
        This method will sweep through the range of ids given by lowID to highID and
        send a remote transmissions request (RTR) to each id and then listen for a response. 
        The RTR will be repeated in the given number of attempts and will sniff for the given duration
        continuing to the next id.
        
        This method will perform this by calling L{experiments.rtrSweep}. 
        The user can specify the range of ids to sweep in a continuous integer region.
        The options are the number of attempts to request a response
        and the sniff time post request. 
        
        Any messages that are sniffed will be saved to a csv file. 
        The filename will be stored in the DATA_LOCATION folder
        with a filename that is the date (YYYYMMDD)_rtr.csv. 
        If the file already exists it will append to the end of the file
        The format will follow that of L{GoodFETMCPCANCommunication.sniff} 
        in that the columns will be as follows:
        
            1. timestamp:     as floating point number
            2. error boolean: 1 if there was an error detected of packet formatting 
                                (not exhaustive check). 0 otherwise
            3. comment tag:   comment about experiments as String
            4. duration:      Length of overall sniff
            5. filtering:     1 if there was filtering. 0 otherwise
            6. db0:           Integer
            
                ---
            7. db7:           Integer
        
        @type  freq: number
        @param freq: The frequency at which the bus is communicating
        @type   lowI: integer
        @param  lowI: The low end of the id sweep
        @type  highI: integer 
        @param highI: The high end of the id sweep
        @type attemptsI: integer
        @param attemptsI: The number of times a RTR will be repeated for a given standard id
        @type  sT: integer
        @param sT: The length of time that it will listen to the bus after sending an RTR
        @type verbose:  boolean
        @param verbose: When true, messages will be printed out to the terminal
        
        @rtype: None
        @return: Does not return anything
        """
        self.setRunning()
        #thread.start_new_thread(self.comm.rtrSweep,(self.dClass.getRate(), lowI, highI, attemptsI, sT, verbose))
        self.comm.rtrSweep(freq, lowI, highI, attemptsI, sT, verbose)
        self.unsetRunning()
 
    def sweepID(self):
        """
        This method will gather user inputs for sweeping through standard ids in the range of integers specified by the
        user inputs. The data will be gathered and loosely error checked to ensure that the data is of the correct type but 
        the checking is not very exhaustive. This will then call L{sweeIDControl} in a thread. See this method for more
        inforamtion on the method.
        
        """
        if( not self.checkComm()):
            return
        sniffTime = self.sniffTime.get()
        low = self.lowSweep.get()
        high = self.HighSweep.get()
        #try to convert the data to the correct form
        try:
            sT = int(sniffTime)
            lowI = int(low)
            highI = int(high)
        except:
            tkMessageBox.showwarning('Invalid Input', 'Values are not integers. Please check inputs and try again.')
            print "Values are not integers. Please check inputs and try again."
            return
        #check that the ids are in a valid range (i.e. the low end is lower than the high end
        if( highI < lowI  or sT <= 0):
            print "Incorrectly formated inputs! Please check that lower ID is less than higher ID"
        thread.start_new_thread(self.sweeIDControl, (self.getRate(),lowI,highI,sT))
    
    def sweeIDControl(self, freq, lowI, highI, sT):
        """
        This method will sweep through the range of standard ids given from low to high.
        This will actively filter for 6 ids at a time and sniff for the given amount of
        time in seconds. If at least one message is read in then it will go individually
        through the 6 ids and sniff only for that id for the given amount of time. All the
        data gathered will be saved.  This does not save any sniffed packets but the messages
        are printed out to the terminal. This method will call L{experiments.filterStdSweep}
        
        @type  freq: number
        @param freq: The frequency at which the bus is communicating
        @type   lowI: integer
        @param  lowI: The low end of the id sweep
        @type  highI: integer 
        @param highI: The high end of the id sweep
        @type  sT: number
        @param sT: Sniff time for each trial. Default is 5 seconds
        
        @rtype: list of numbers
        @return: A list of all IDs found during the sweep.
        """
        self.setRunning()
        print self.comm.filterStdSweep( freq, lowI, highI, sT )
        self.unsetRunning()
    
    #run the method
    def main(self):
        """
        This method is the loop that runs the display.
        """
        print 'Entering main loop'
        #lets everything just sit and listen
        self.root.mainloop()
        


class settingsDialog(Toplevel):
    """
    This class creates a dialog that allows the user to set the settings for the GUI. 
    These settings are saved in /Settings.ini which allows for persistent information 
    even after the user closes the window. 
    You can set the bus frequency, SQL information, data locations. 
    
    """
    #constructor method
    def __init__(self, parent, dClass, data, title = None):
        """
        Constructor method for the window. This is a child window of the mainDisplay
        
        @param parent: Tkinter.Tk() for the main window
        @param dClass: main window
        @param data: unused
        @param title: title for the child window
        
        """
        
        
        Toplevel.__init__(self, parent)
        self.transient(parent)
        #top = self.top = Toplevel(parent)
        if title:
            self.title(title)
        #set parent
        self.parent = parent
        #set Data
        self.data = data
        self.dClass = dClass
        
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
        """
        This method builds the main part of the window with 
        the settings options and input locations
        """
        
        i=0
        # i is the row number
        
        
        #connect
        connectButton = Tkinter.Button(master,text="Connect to Board",\
                                        command = self.dClass.connectBus,width=20)
        connectButton.grid(row=i,column=0, sticky=Tkinter.W,columnspan=3)
        i += 1
        
        #allows the user to set the rate
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Set Rate:"
        entryLabel.grid(row=i,column=0)
        self.rateChoice = Tkinter.StringVar()
        self.rateChoice.set(self.dClass.getRate());
        self.rateMenu = Tkinter.OptionMenu(master,self.rateChoice,\
                                           "83.3","100","125","250","500","1000")
        self.rateMenu.grid(row=i,column=1)
        rateButton = Tkinter.Button(master,text="Set Rate",command=self.setRate,width=10)
        rateButton.grid(row=i,column=2)
        i += 1
        
        
        # SQL database information
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "MYSQL Database information:"
        entryLabel.grid(row=i,column=0, columnspan=3, sticky=Tkinter.W)
        i += 1
        
        self.sqlDB = []
        
        #table
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Table:"
        entryLabel.grid(row=i,column=1, sticky = Tkinter.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_TABLE)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=Tkinter.W)
        entryWidget["width"] = 30
        i += 1
        
    
       
        #Name
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Name:"
        entryLabel.grid(row=i,column=1, sticky = Tkinter.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_NAME)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=Tkinter.W)
        entryWidget["width"] = 30
        i += 1
        
        #host
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Host:"
        entryLabel.grid(row=i,column=1, sticky = Tkinter.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_HOST)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=Tkinter.W)
        entryWidget["width"] = 30
        i += 1
        
        #username
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Username:"
        entryLabel.grid(row=i,column=1, sticky = Tkinter.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_USERNAME)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=Tkinter.W)
        entryWidget["width"] = 30
        i += 1
        
        #password
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Password:"
        entryLabel.grid(row=i,column=1, sticky = Tkinter.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_PASSWORD)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp, show="*")
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=Tkinter.W)
        entryWidget["width"] = 30
        i += 1
        
        #Database
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Database:"
        entryLabel.grid(row=i,column=1, sticky = Tkinter.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_DATABASE)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=Tkinter.W)
        entryWidget["width"] = 30
        i += 1
        
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "File storage location:"
        entryLabel.grid(row=i,column=0,columnspan=2,sticky=Tkinter.W)
        i += 1
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Path:"
        entryLabel.grid(row=i,column=1,sticky=Tkinter.W)
        self.fileLocation = Tkinter.StringVar()
        self.fileLocation.set(self.dClass.getDataLocation())
        entryWidget = Tkinter.Entry(master, textvariable=self.fileLocation)
        entryWidget.grid(row=i,column=2,columnspan=3,sticky=Tkinter.W)
        entryWidget["width"] = 30
        
        i+=1
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Car Module file locations:"
        entryLabel.grid(row=i,column=0,columnspan=2,sticky=tk.W)
        i+=1
        
        
        # EXPERIMENT MODULE FILE
        fileLocations = self.dClass.getExperimentFileLocations()
        
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Module File: "
        entryLabel.grid(row=i,column=1,columnspan=1,sticky=tk.W)
        self.experimentFileLocation = Tkinter.StringVar()
        if( fileLocations[0] == None):
            self.experimentFileLocation.set("")
        else:
            self.experimentFileLocation.set(fileLocations[0])
        
        entryWidget = Tkinter.Entry(master, textvariable=self.experimentFileLocation)
        entryWidget.grid(row=i,column=2,columnspan=3,sticky=tk.W)
        entryWidget["width"] = 30
        
        i += 1
        
        # GUI module file
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "GUI Module File:"
        entryLabel.grid(row=i,column=1,columnspan=1,sticky=tk.W)
        self.experimentGUIFileLocation = Tkinter.StringVar()
        if( fileLocations[1] == None):
            self.experimentGUIFileLocation.set("")
        else:
            self.experimentGUIFileLocation.set(fileLocations[1])
        entryWidget = Tkinter.Entry(master, textvariable = self.experimentGUIFileLocation)
        entryWidget.grid(row=i,column=2,columnspan=3,sticky=tk.W)
        entryWidget["width"] = 30
        
        i +=1
        
        # DELETE arb ID
        b = Tkinter.Button(master, command=self.dClass.deleteArbID,text="Delete ID from database")
        b.grid(row=i,column=0,columnspan=2)
        
    def setRate(self):
        """
        This will set the rate the GOODTHOPTER 10 listens to the CAN bus
        """
        rate = float(self.rateChoice.get())
        self.dClass.setRate(rate)
        
    
    #This is the cancel / ok button
    def buttonbox(self):
        """
        buttons in the display. Apply/Cancel buttons
        """
        #add standard button box
        box = Frame(self)
        
        #ok button
        w = Button(box, text="Apply", width = 10, command = self.ok, default=ACTIVE)
        w.pack(side=LEFT,padx=5,pady=5)
        # cancel button
        w = Button(box,text="Cancel", width=10,command = self.cancel)
        w.pack(side=LEFT,padx=5,pady=5)
        
        self.bind("<Return>",self.ok)
        self.bind("<Escape>",self.cancel)
        
        box.pack()
        
    # ok button will first validate the choices (see validate method) and then exit the dialog
    # if everything is ok 
    def ok(self, event = None):
        """
        This method will gather all the SQL information and save it to the settings file as well
        as update the information within the GUI itself for the current instance.
        """
        #print "Updating Configurations."
        if not self.validate():
            self.initial_focus.focus_set() #put focus back
            return
        fileLocation = self.fileLocation.get()
        self.dClass.setDataLocation(fileLocation)
        #table = "%s"% self.sqlDB[0].get()
        #print table
        table = self.sqlDB[0].get()
        name = self.sqlDB[1].get()
        host = self.sqlDB[2].get()
        username = self.sqlDB[3].get()
        password = self.sqlDB[4].get()
        database =self.sqlDB[5].get() 
        self.dClass.setDataManage(table = table, name = name, host = host, \
                                  username = username, password = password, database = database )
        
        self.dClass.setCarModule(self.experimentFileLocation.get(), self.experimentGUIFileLocation.get())
        
        
        
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.parent.focus_set()
        self.destroy()
        return 1
        
    # this is a cancel button which will just exit the dialog and should not plot anything
    def cancel(self, event = None):
        """
        Closes the window if the user wants to cancel settings changes
        """
        self.data.clear()
    
        #put focus back on parent window
        self.parent.focus_set()
        self.destroy()
        return 0
       
    #this tests to make sure that there are inputs 
    def validate(self):
        #returns 1 if everything is ok
        return 1
    
    #this method is called right before exiting. 
    #it will set the input dictionary with the information for
    # the display method to grab the data and graph it
    def apply(self):
        
            
        return

        
# executes everything to run
if __name__ == "__main__":
    dapp = DisplayApp()
    dapp.main()
