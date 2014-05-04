#obtained from: http://effbot.org/zone/tkinter-text-hyperlink.htm
# Copyright  1995-2010 by Fredrik Lundh

from Tkinter import *

class HyperlinkManager:
    """  Wrapper class for setting hyperlink bindings within the text box. This code was modified from the opensource
    website U{http://effbot.org/zone/tkinter-text-hyperlink.htm} and carries the following copyright:
    
    Copyright  1995-2010 by Fredrik Lundh
    
    See the website for additional information on the functionality of this class.
    
    """

    def __init__(self, text):

        self.text = text

        self.text.tag_config("hyper", foreground="black", underline=1)

        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)

        self.reset()

    def reset(self):
        """ remove all hyperlinks"""
        self.links = {}

    def add(self, action, id):
        """ 
        Add a new hyper link
        
        @param action: method that will be called for this hyperlink
        @param id: the arbitration id that we are associating this action.
        """
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = [action, id]
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        """ 
        If somebody clicks on the link it will find the method to call
        """
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag][0](self.links[tag][1])
                return
