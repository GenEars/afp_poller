# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 21:27:31 2020

@author: lione
"""

import requests
import logging
import random

#from tkinter import *  # https://python.doctor/page-tkinter-interface-graphique-python-tutoriel
import tkinter as tk


# =============================================================================
# Initialisation du loggeur
loggingFormatString = '%(asctime)s:%(levelname)s:%(threadName)s:%(funcName)s:%(message)s'
logging.basicConfig(format=loggingFormatString, level=logging.DEBUG)

# Initialisation des URL
url_auth = "https://api.afp.com/oauth/token?grant_type=anonymous"
url_search = "https://api.afp.com:443/v1/api/search?wt=xml&access_token="

# =============================================================================
# Démarrage  du traitement

logging.info('INIT')

# =============================================================================
# Récupération du jeton d'authentification
r_auth = requests.get(url_auth)

logging.info("AUTH:status_code=%s", r_auth.status_code)

# =============================================================================
# Récupération des news

max_rows = 50

payload = """<?xml version="1.0"?>
<Parameters>
  <dateRange>
    <from>now-3d</from>
    <to>now</to>
  </dateRange>
  <lang>fr</lang>
  <maxRows>50</maxRows>
</Parameters>
"""
# TODO : include max_rows dans payload

headers = { 'Content-Type': 'application/xml'}

url_search_full = url_search + r_auth.json()['access_token']
r_search = requests.post(url_search_full, data=payload, headers=headers)

logging.info("SEARCH:status_code=%s", r_search.status_code)

# =============================================================================
# Traitement des news

r_search_response = r_search.json()['response']

for news in r_search_response['docs']:
    
    logging.info("NEWS:headline=%s", news['headline'])


# =============================================================================
# Marquee
# Source: https://stackoverflow.com/questions/47224061/how-to-make-marquee-on-tkinter-in-label


class Marquee(tk.Canvas):
    def __init__(self, parent, text, margin=2, borderwidth=0,
                 relief='flat', fps=30,
                 bg='black', fg='white',
                 font_name="Arial", font_size=10,
                 index=0):

        logging.debug("MARQUEE:INIT:text=%s:index=%s:font_size=%s", text, index, font_size)

        tk.Canvas.__init__(self,
                           parent,
                           borderwidth=borderwidth,
                           relief=relief,
                           background=bg)
        self.fps = fps
        self.index = index

        # start by drawing the text off screen, then asking the canvas
        # how much space we need. Use that to compute the initial size
        # of the canvas. 
        text = self.create_text(
                0, -1000,
                text=text,
                anchor="w",
                font=(font_name, font_size),
                tags=("text_%s" % index,),
                fill=fg)
        (x0, y0, x1, y1) = self.bbox("text_%s" % index)
        
        width = (x1 - x0) + (2*margin) + (2*borderwidth)
        height = (y1 - y0) + (2*margin) + (2*borderwidth)
        
        self.configure(width=width, height=height)

        # start the animation
        self.animate()

    def animate(self):
        (x0, y0, x1, y1) = self.bbox("text_%s" % self.index)
        if x1 < 0 or y0 < 0:
            # everything is off the screen; reset the X
            # to be just past the right margin
            x0 = self.winfo_width()
            y0 = int(self.winfo_height()/2)
            self.coords("text_%s" % self.index, x0, y0)
        else:
            self.move("text_%s" % self.index, -1, 0)

        # do again in a few milliseconds
        self.after_id = self.after(int(1000/self.fps), self.animate)


def random_news_index():
    return random.randint(0, len(r_search_response['docs']) - 1)


def make_marquee(parent_win, marquee_text, font_size, marquee_pady, index):
    marquee = Marquee(
            parent_win,
            text=marquee_text,
            borderwidth=0, relief="flat",
            font_size=font_size,
            index=index)
    marquee.pack(side="top", fill="x", pady=marquee_pady)


def clavier(event):
    touche = event.keysym
    logging.debug("EVENT:clavier:touche=%s", touche)

    if touche == "Escape":
        pass
    elif touche == "space":
        pass
        
# =============================================================================

root = tk.Tk()
root.configure(bg='black')
root.bind("<Key>", clavier)

base_font_size=10
base_paddy=10

for index in range(0, 10):
    make_marquee(
            root,
            r_search_response['docs'][random_news_index()]['headline'],
            font_size = base_font_size + random.randint(-base_font_size + 5, 40),
            marquee_pady = base_paddy + random.randint(-base_paddy + 1, base_paddy + 10),
            index=index)

root.mainloop()

# TODO: update des news
# TODO: update des marquee
# TODO: dimensionnement max
# TODO: disparition de la tête de fenêtre
# TODO: appel à distance
# TODO: gestion de la fermeture

# =============================================================================

logging.info('END')
# TODO: __main()__
