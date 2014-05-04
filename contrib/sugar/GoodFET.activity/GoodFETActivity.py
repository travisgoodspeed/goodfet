from sugar.activity import activity
import logging

import sys, os
import gtk

from GoodFETCCSPI import GoodFETCCSPI;

client = GoodFETCCSPI();

class GoodFETActivity(activity.Activity):
     def butConnectClicked(self, widget, data=None):
         logging.info('Attempting to connect.');
         client.serInit();
         client.setup();
         logging.info("Connected.");
         self.butConnect.set_label("Connected to %s" % client.identstr());
 
     def __init__(self, handle):
         print "running activity init", handle
         activity.Activity.__init__(self, handle)
         print "activity running"
 
         # Creates the Toolbox. It contains the Activity Toolbar, which is the
         # bar that appears on every Sugar window and contains essential
         # functionalities, such as the 'Collaborate' and 'Close' buttons.
         toolbox = activity.ActivityToolbox(self)
         self.set_toolbox(toolbox)
         toolbox.show()
 
         # Creates a new button with the label "Hello World".
         self.butConnect = gtk.Button("connect")
     
         # When the button receives the "clicked" signal, it will call the
         # function hello() passing it None as its argument.  The hello()
         # function is defined above.
         self.butConnect.connect("clicked", self.butConnectClicked, None)
     
         # Set the button to be our canvas. The canvas is the main section of
         # every Sugar Window. It fills all the area below the toolbox.
         self.set_canvas(self.butConnect)
     
         # The final step is to display this newly created widget.
         self.butConnect.show()
     
         print "AT END OF THE CLASS"
