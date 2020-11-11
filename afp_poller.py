# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 21:27:31 2020

@author: lione
"""

import requests
import logging
import random
import platform


#from tkinter import *  # https://python.doctor/page-tkinter-interface-graphique-python-tutoriel
import tkinter as tk


# =============================================================================
# Initialisation du loggeur
loggingFormatString = '%(asctime)s:%(levelname)s:%(threadName)s:%(funcName)s:%(message)s'
logging.basicConfig(format=loggingFormatString, level=logging.DEBUG)


# =============================================================================
# Démarrage  du traitement

logging.info('INIT')

logging.info("INIT:platform.system=%s", platform.system())

# =============================================================================

def ws_auth_token(
        ws_url="https://api.afp.com/oauth/token?grant_type=anonymous"):
    """ Récupération du jeton d'authentification """  

    r_auth = requests.get(ws_url)
    logging.info("AUTH:status_code=%s", r_auth.status_code)
    
    r_auth_token = r_auth.json()['access_token']
    logging.debug("AUTH:access_token=%s", r_auth_token)
    
    return r_auth_token


def ws_get_news(
        ws_url="https://api.afp.com:443/v1/api/search?wt=xml&access_token=",
        access_token=None,
        max_rows=50):
    """ Récupération des news """

    # Request parameters
    payload = """<?xml version="1.0"?>
    <Parameters>
      <dateRange>
        <from>now-3d</from>
        <to>now</to>
      </dateRange>
      <lang>fr</lang>
      <maxRows>{max_rows}</maxRows>
    </Parameters>
    """.format(max_rows=max_rows)
    
    headers = { 'Content-Type': 'application/xml'}
    url_search_full = ws_url + access_token
    
    # Request
    r_search = requests.post(url_search_full, data=payload, headers=headers)
    logging.info("SEARCH:status_code=%s", r_search.status_code)

    r_search_response = r_search.json()['response']
    logging.debug("SEARCH:r_search_response=%s", r_search_response)
    
    return r_search_response


def random_news_index(data):
    """ Get a valid random index over retrieved news """
    return random.randint(0, len(data['docs']) - 1)


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
        parent_win,
        index=0):
    """ Add a Marquee canvas with text randomly selected from data """

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


def populate_with_marquees(data, parent_win, news_count=10):
    """ Add multiple Marquees canvas """
    for index in range(0, news_count):
        add_marquee(
                data,
                parent_win,
                index)


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

# News polling
news_data = ws_get_news(access_token=ws_auth_token())
# TODO: get news from file
for news in news_data['docs']:
    
    logging.debug("NEWS:headline=%s", news['headline'])

# GUI init
root = tk.Tk()
root.configure(bg='black')
root.title(__file__)
root.state("zoomed")
remove_title_bar(root)
root.bind("<Key>", clavier)

base_font_size=10
base_paddy=10

root.after(0, populate_with_marquees(news_data, root))

root.mainloop()

# TODO: update des news
# TODO: update des marquee
# TODO: appel à distance
# TODO: argparse avec log level
# TODO: fps dans argparse
# TODO: logging dans syslog

# =============================================================================

logging.info('END')
# TODO: __main()__
