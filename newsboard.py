# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 21:27:31 2020

@author: Lionel TAILHARDAT

newsboard:
    GUI to display news coming from afp_poller.py
    Keyboard can control basic GUI's behavior.
    On Linux platforms, GUI's may also be controled with POSIX signals.
"""

import json
import logging
import os
import random
import platform
import signal
import sys

import time
import threading

#from tkinter import *  # https://python.doctor/page-tkinter-interface-graphique-python-tutoriel
import tkinter as tk


# =============================================================================
# GUI definitions

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

        logging.debug("MARQUEE:INIT:text=%s:font_size=%s", text, font_size)

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
# App definitions
   
class GuiPart:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        # Set up the GUI
        console = Tkinter.Button(master, text='Done', command=endCommand)
        console.pack()
        # Add more GUI stuff here

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                print msg
            except Queue.Empty:
                pass
            
class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master

        # Create the queue
        self.queue = Queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
    	self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following 2 lines with the real
            # thing.
            time.sleep(rand.random() * 0.3)
            msg = rand.random()
            self.queue.put(msg)

    def endApplication(self):
        self.running = 0
    
def random_news_index(data):
    """ Get a valid random index over retrieved news """
    return random.randint(0, len(data['docs']) - 1)


def make_marquee(parent_win, marquee_text, font_size, marquee_pady):
    """ Create a Marquee canvas on parent_win """
    marquee = Marquee(
            parent_win,
            text=marquee_text,
            borderwidth=0, relief="flat",
            font_size=font_size)
    marquee.pack(side="top", fill="x", pady=marquee_pady)


def delete_marquee_by_name(parent_win, name):
    """ Delete a Marquee canvas on parent_win by its name """

    if name in parent_win.children.keys():
        marquee_object = parent_win.children[name]
        marquee_object.destroy()
        done = True
    else:
        logging.warning("MARQUEE:DELETE_BY_NAME:name doesn't exist", name)
        done = False
    
    logging.debug("MARQUEE:DELETE_BY_NAME:name='%s':done=%s", name, done)
    return done


def delete_marquee_by_index(parent_win, index=None):
    """ Delete a Marquee canvas on parent_win by its index or randomly """

    # Retrieve object names as list
    object_list = list(parent_win.children.keys())

    # Compute a random object if index is not set
    if (index is None) and (len(object_list) > 0):
        index = random.randint(0, len(parent_win.children.keys()) - 1)
        logging.debug("MARQUEE:DELETE_BY_INDEX:index=%s:randomly selected", index)

    # Check that index is correct, then get corresponding object name
    if index < len(object_list):
        object_name = object_list[index]
        logging.debug("MARQUEE:DELETE_BY_INDEX:object_name=%s", object_name)
    else:
        logging.warning("MARQUEE:DELETE_BY_INDEX:incorrect index (must be between 0 and %s)", object_name, len(object_list) - 1)
        return False

    # Delete object by name
    return delete_marquee_by_name(parent_win, object_name)
    # TODO: smooth destroy()
    # TODO: keep window size constant when deleting



def add_marquee(
        data,
        parent_win):
    """ Add a Marquee canvas with text randomly selected from data """

    # TODO: export in a Class parameter
    base_font_size=10
    base_paddy=10

    # Prepare message to be shown
    random_index = random_news_index(data)
    # TODO: try not no draw a news that is already shown
    text_to_display = "{0} ({1})".format(
            data['docs'][random_index]['headline'],  # Alternatives: caption / headline
            data['docs'][random_index]['published'])
    logging.info("MARQUEE:ADD:random_index=%s:text_do_display=%s", random_index, text_to_display)
    
    # Call Marquee builder
    make_marquee(
            parent_win,
            text_to_display,
            font_size = base_font_size + random.randint(-base_font_size + 5, 40),
            marquee_pady = base_paddy + random.randint(-base_paddy + 1, base_paddy + 10))


def delete_and_add_marquee(data, parent_win):
    """ Random deletion of a Marquee and add a new one """
    delete_marquee_by_index(parent_win)
    add_marquee(data, parent_win)
    

def populate_with_marquees(data, parent_win, news_count=10):
    """ Add multiple Marquees canvas """
    for index in range(0, news_count):
        add_marquee(
                data,
                parent_win)


def remove_title_bar(parent_win):
    """ Remove GUI's title bar """

    if platform.system() == "Linux":
        # Tk 8.5 or above, Linux system
        root.wm_attributes('-type', 'splash')
    
    # TODO: remove title bar for Windows OS


def clavier(event):
    """ GUI's keyboard event handler """
    
    touche = event.keysym
    logging.debug("EVENT:clavier:touche=%s", touche)

    if touche == "Escape":
        root.destroy()
    elif touche == "space":
        delete_marquee_by_index(root)
    elif touche == "Return":
        add_marquee(news_data, root)
        
    
# =============================================================================
def readConfiguration(signalNumber, frame):
    logging.debug("SIGNAL:Received=%s", '(SIGHUP) reading configuration')
    return

def terminateProcess(signalNumber, frame):
    logging.debug("SIGNAL:Received=%s", '(SIGTERM) terminating the process')
    sys.exit()
    
def receiveSignal(signalNumber, frame):
    logging.debug("SIGNAL:Received=%s", signalNumber)
    return

def register_signals():
    # register the signals to be caught
    signal.signal(signal.SIGHUP, readConfiguration)
    signal.signal(signal.SIGINT, receiveSignal)
    signal.signal(signal.SIGQUIT, receiveSignal)
    signal.signal(signal.SIGILL, receiveSignal)
    signal.signal(signal.SIGTRAP, receiveSignal)
    signal.signal(signal.SIGABRT, receiveSignal)
    signal.signal(signal.SIGBUS, receiveSignal)
    signal.signal(signal.SIGFPE, receiveSignal)
    #signal.signal(signal.SIGKILL, receiveSignal)
    signal.signal(signal.SIGUSR1, receiveSignal)
    signal.signal(signal.SIGSEGV, receiveSignal)
    signal.signal(signal.SIGUSR2, receiveSignal)
    signal.signal(signal.SIGPIPE, receiveSignal)
    signal.signal(signal.SIGALRM, receiveSignal)
    signal.signal(signal.SIGTERM, terminateProcess)


# =============================================================================
def load_data(data_file_path="afp_poller.json"):
    """ Load data from file """
    
    # Get data
    data = None
    try:        
        with open(data_file_path, "r") as fh:
            data = json.load(fh)
    except IOError as e:
        logging.error("NEWS:LOAD:data_file_path=%s:error=%s", data_file_path, e)
        return None
    
    # Get stats
    if 'docs' in data.keys():
        docs_count = len(data['docs'])
    else:
        docs_count = 0
    
    # Report and return data
    logging.info("NEWS:LOAD:data_file_path=%s:docs_count=%s", data_file_path, docs_count)
    return data


def main():
    """ Load data, start GUI and listen to events """    
    
    # Initialisation du loggeur
    loggingFormatString = '%(asctime)s:%(levelname)s:%(threadName)s:%(funcName)s:%(message)s'
    logging.basicConfig(format=loggingFormatString, level=logging.DEBUG)
    
    
    # Démarrage  du traitement    
    logging.info('INIT')    
    logging.info("INIT:platform.system=%s", platform.system())

    # Register POSIX signals callback on Linux platforms
    if platform.system() == "Linux":
        register_signals()

    # Load data
    news_data = load_data()
    if news_data is None:
        sys.exit(1)
    
    # GUI init
    root = tk.Tk()
    root.configure(bg='black')
    root.title(__file__)
    root.state("zoomed")
    root.pack_propagate(0)
    remove_title_bar(root)
    root.bind("<Key>", clavier)
    
    
    root.after(0, populate_with_marquees(news_data, root))
    # root.after(5000, delete_and_add_marquee(news_data, root))  # TODO: periodic refresh
    
    root.mainloop()
    
    # TODO: news par défaut
    # TODO: update des news
    # TODO: update des marquee
    # TODO: appel à distance
    # TODO: argparse avec log level
    # TODO: fps dans argparse
    # TODO: logging dans syslog
    
    
    logging.info('END')
    return 0  # TODO: gérer les exceptions et le code retour

# =============================================================================

if __name__ == '__main__':
    ret_code = main()
    sys.exit(ret_code)
