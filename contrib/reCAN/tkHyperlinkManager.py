# obtained from: http://effbot.org/zone/tkinter-text-hyperlink.htm
# Copyright  1995-2010 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its 
# associated documentation, you agree that you have read, understood,
#  and will comply with the following terms and conditions:

# Permission to use, copy, modify, and distribute this software and 
# its associated documentation for any purpose and without fee is hereby 
# granted, provided that the above copyright notice appears in all copies, 
# and that both that copyright notice and this permission notice appear in 
# supporting documentation, and that the name of Secret Labs AB or the author
#  not be used in advertising or publicity pertaining to distribution of the
# software without specific, written prior permission.

# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS 
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. 
# IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.

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
