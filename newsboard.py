# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 21:27:31 2020

@author: Lionel TAILHARDAT

newsboard:
    GUI to display news coming from afp_poller.py
    Keyboard can control basic GUI's behavior.
    On Linux platforms, GUI's may also be controled with POSIX signals.
"""

import datetime
import json
import logging
#import os
import random
import platform
import signal
import sys
import tkinter as tk  # https://python.doctor/page-tkinter-interface-graphique-python-tutoriel


# =============================================================================
# Marquee class

class Marquee(tk.Canvas):
    """
        Marquee class
        Source: https://stackoverflow.com/questions/47224061/how-to-make-marquee-on-tkinter-in-label
    """
    def __init__(self, parent, text, margin=2, borderwidth=0,
                 fps=30,
                 relief='flat',
                 bg='black',
                 fg='white',
                 font_name="Arial",
                 font_size=10):
        """ Class constructor """

        logging.debug("MARQUEE:INIT:text='%s':font_size=%s", text, font_size)

        tk.Canvas.__init__(self,
                           parent,
                           borderwidth=borderwidth,
                           relief=relief,
                           background=bg,
                           highlightthickness=0)
        self.fps = fps

        # start by drawing the text off screen, then asking the canvas
        # how much space we need. Use that to compute the initial size
        # of the canvas. 
        text = self.create_text(
                0, -1000,
                text=text,
                anchor="w",
                font=(font_name, font_size),
                tags=("text",),
                fill=fg)
        (x0, y0, x1, y1) = self.bbox("text")
        
        width = (x1 - x0) + (2*margin) + (2*borderwidth)
        height = (y1 - y0) + (2*margin) + (2*borderwidth)
        
        self.configure(width=width, height=height)

        # start the animation
        self.animate()

    def animate(self):
        (x0, y0, x1, y1) = self.bbox("text")
        if x1 < 0 or y0 < 0:
            # everything is off the screen; reset the X
            # to be just past the right margin
            x0 = self.winfo_width()
            y0 = int(self.winfo_height()/2)
            self.coords("text", x0, y0)
        else:
            self.move("text", -1, 0)

        # do again in a few milliseconds
        self.after_id = self.after(int(1000/self.fps), self.animate)

            
# =============================================================================
# Gui class
   
class GuiPart:
    def __init__(self, parent_win, end_command):
        """ Class constructor """
        
        # Object properties
        self.parent_win = parent_win
        self.end_command = end_command
        self.base_font_size = 10
        self.base_paddy = 10
        self.expected_marquee_count = 10
        self.data_file_path = "afp_poller.json"
        self.docs_count = 0

        self.news_data = None

        # Set up the App
        parent_win.bind("<Key>", self.clavier)
        self.remove_title_bar()

        # Initial data load
        if self.load_data() == False:
            sys.exit(1)

        # Populate the GUI
        for index in range(0, self.expected_marquee_count):
            self.add_marquee()
        self.last_refresh_date = datetime.datetime.now()


    def __str__(self):
        """ Class string function """
        return "GuiPart object:docs_count=%s:data_file_path=%s:last_refresh_date=%s" % (self.docs_count, self.data_file_path, self.last_refresh_date)


    def remove_title_bar(self):
        """ Remove GUI's title bar """
    
        if platform.system() == "Linux":
            # Tk 8.5 or above, Linux system
            self.parent_win.wm_attributes('-type', 'splash')
        
        # TODO: remove title bar for Windows OS
          
        
    def load_data(self):
        """ Load data from file """
        
        # Get data
        try:        
            with open(self.data_file_path, "r") as fh:
                self.news_data = json.load(fh)
        except IOError as e:
            logging.error("NEWS:LOAD:data_file_path='%s':error=%s", self.data_file_path, e)
            return False
        
        # Get stats
        if 'docs' in self.news_data.keys():
            self.docs_count = len(self.news_data['docs'])
        else:
            self.docs_count = 0
        
        # Report and return data
        logging.info("NEWS:LOAD:data_file_path=%s:docs_count=%s", self.data_file_path, self.docs_count)
        return True


    def clavier(self, event):
        """ GUI's keyboard event handler """
        
        touche = event.keysym
        logging.debug("EVENT:clavier:touche=%s", touche)
    
        if touche == "Escape":
            self.parent_win.destroy()
        elif touche == "space":
            self.delete_marquee_by_index()
        elif touche == "Return":
            self.add_marquee()
        elif touche == "Tab":
            self.refresh_content()
        elif touche == "l":
            if self.load_data() == False:
                sys.exit(1)
        else:
            logging.debug("EVENT:clavier:touche=%s:%s", touche, 'not handled')


    def random_news_index(self):
        """ Get a valid random index over retrieved news """
        return random.randint(0, len(self.news_data['docs']) - 1)
    
    
    def make_marquee(self, marquee_text, font_size, marquee_pady):
        """ Create a Marquee canvas on parent_win """
        marquee = Marquee(
                self.parent_win,
                text=marquee_text,
                borderwidth=0, relief="flat",
                font_size=font_size)
        marquee.pack(side="top", fill="x", pady=marquee_pady)

    
    def add_marquee(self):
        """ Add a Marquee canvas with text randomly selected from data """
        
        # Prepare message to be shown
        random_index = self.random_news_index()
        # TODO: try not no draw a news that is already shown
        text_to_display = "{0} ({1})".format(
                self.news_data['docs'][random_index]['headline'],  # Alternatives: caption / headline
                self.news_data['docs'][random_index]['published'])
        logging.info("MARQUEE:ADD:random_index=%s:text_do_display=%s", random_index, text_to_display)
        
        # Call Marquee builder
        self.make_marquee(
                text_to_display,
                font_size = self.base_font_size + random.randint(-self.base_font_size + 5, 40),
                marquee_pady = self.base_paddy + random.randint(-self.base_paddy + 1, self.base_paddy + 10))

    
    def delete_marquee_by_name(self, name, fade=True):
        """ Delete a Marquee canvas on parent_win by its name """
    
        # TODO: smooth destroy
        if name in self.parent_win.children.keys():
            marquee_object = self.parent_win.children[name]
            marquee_object.destroy()
            done = True
        else:
            logging.warning("MARQUEE:DELETE_BY_NAME:name doesn't exist", name)
            done = False
        
        logging.debug("MARQUEE:DELETE_BY_NAME:name='%s':done=%s", name, done)
        return done
    
    
    def delete_marquee_by_index(self, index=None):
        """ Delete a Marquee canvas on parent_win by its index or randomly """
    
        # Retrieve object names as list
        object_list = list(self.parent_win.children.keys())
    
        # Compute a random object if index is not set
        if (index is None) and (len(object_list) > 0):
            index = random.randint(0, len(self.parent_win.children.keys()) - 1)
            logging.debug("MARQUEE:DELETE_BY_INDEX:index=%s:randomly selected", index)
    
        # Check that index is correct, then get corresponding object name
        if index < len(object_list):
            object_name = object_list[index]
            logging.debug("MARQUEE:DELETE_BY_INDEX:object_name=%s", object_name)
        else:
            logging.warning("MARQUEE:DELETE_BY_INDEX:incorrect index (must be between 0 and %s)", object_name, len(object_list) - 1)
            return False
    
        # Delete object by name
        return self.delete_marquee_by_name(object_name)
        # TODO: smooth destroy()
    
    
    def refresh_content(self):
        """ Random deletion of a Marquee and add a new one """
        logging.debug("MARQUEE:refresh_content")
        self.delete_marquee_by_index()
        self.add_marquee()
        self.last_refresh_date = datetime.datetime.now()

        
# =============================================================================
# ThreadedClient class

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread.
    periodicCall and endApplication could reside in the GUI part,
    but putting them here means that you have all the thread controls 
    in a single place.
    """
    def __init__(self, master, refresh_period=30000):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI.
        """
        
        # Register POSIX signals callback on Linux platforms
        if platform.system() == "Linux":
            self.register_signals()

        # Set up the GUI part
        self.refresh_period = refresh_period  # [ms]
        self.master = master
        self.gui = GuiPart(master, self.endApplication)

        # Threaded flags
        self.running = 1

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """ Refresh news every refresh_period """
        self.gui.refresh_content()
        if not self.running:
            logging.info("END:periodicCall.running=%s", self.running)
            self.master.destroy()
        self.master.after(self.refresh_period, self.periodicCall)


    def endApplication(self):
        self.running = 0
    

    def readConfiguration(self, signalNumber, frame):
        """ Signal handling: SIGHUP """
        logging.debug("SIGNAL:Received=%s", '(SIGHUP) reading configuration')
        # TODO: return info
        return
    

    def terminateProcess(self, signalNumber, frame):
        """ Signal handling: SIGTERM """
        logging.debug("SIGNAL:Received=%s", '(SIGTERM) terminating the process')
        sys.exit()
        

    def userDefinedCondition1(self, signalNumber, frame):
        """ Signal handling: SIGUSR1, gui.refresh_content() """
        logging.debug("SIGNAL:Received=%s", '(SIGUSR1) refresh GUI content')
        self.gui.refresh_content()

    def userDefinedCondition2(self, signalNumber, frame):
        """ Signal handling: SIGUSR2, gui.load_data() """
        logging.debug("SIGNAL:Received=%s", '(SIGUSR2) load data')
        if self.gui.load_data() == False:
            sys.exit(1)


    def receiveSignal(self, signalNumber, frame):
        """ Signal handling: echo signal """
        logging.debug("SIGNAL:Received=%s", signalNumber)
        return
    

    def register_signals(self):
        """
            Signal handling: register the signals to be caught
            Source: https://www.stackabuse.com/handling-unix-signals-in-python/
        """
        signal.signal(signal.SIGHUP, self.readConfiguration)
        signal.signal(signal.SIGINT, self.receiveSignal)
        signal.signal(signal.SIGQUIT, self.receiveSignal)
        signal.signal(signal.SIGILL, self.receiveSignal)
        signal.signal(signal.SIGTRAP, self.receiveSignal)
        signal.signal(signal.SIGABRT, self.receiveSignal)
        signal.signal(signal.SIGBUS, self.receiveSignal)
        signal.signal(signal.SIGFPE, self.receiveSignal)
        #signal.signal(signal.SIGKILL, self.receiveSignal)
        signal.signal(signal.SIGUSR1, self.userDefinedCondition1)
        signal.signal(signal.SIGSEGV, self.receiveSignal)
        signal.signal(signal.SIGUSR2, self.userDefinedCondition2)
        signal.signal(signal.SIGPIPE, self.receiveSignal)
        signal.signal(signal.SIGALRM, self.receiveSignal)
        signal.signal(signal.SIGTERM, self.terminateProcess)


# =============================================================================

def main():
    """ Init, start GUI and listen to events """    
    
    # Initialisation du loggeur
    loggingFormatString = '%(asctime)s:%(levelname)s:%(threadName)s:%(funcName)s:%(message)s'
    logging.basicConfig(format=loggingFormatString, level=logging.DEBUG)
    
    
    # Démarrage  du traitement    
    logging.info('INIT')    
    logging.info("INIT:platform.system=%s", platform.system())

    # GUI init
    root = tk.Tk()

    root.configure(bg='black')
    root.title(__file__)
    root.state("zoomed")
    root.pack_propagate(0)
  
    client = ThreadedClient(root)
    root.mainloop()
    
    # TODO: news par défaut
    # TODO: argparse avec log level
    # TODO: fps dans argparse
    # TODO: logging dans syslog
    
    
    logging.info('END')
    return 0  # TODO: gérer les exceptions et le code retour

# =============================================================================

if __name__ == '__main__':
    ret_code = main()
    sys.exit(ret_code)
