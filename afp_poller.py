# coding: utf-8
"""
Created on Mon Nov  9 21:27:31 2020

@author: Lionel TAILHARDAT

afp_poller:
    News polling from the AFP webservice (https://developers.afp.com/)
    and save to file for later processing.
"""

from __future__ import unicode_literals

import json
import logging
import os
import platform
import requests
import sys

# =============================================================================

if sys.version_info[0] < 3:
    import codecs
    import warnings
    def open(file, mode='r', buffering=1, encoding=None,
             errors=None, newline=None, closefd=True, opener=None):
        if newline is not None:
            warning.warn('newline is not supported in py2')
        if not closefd:
            warning.warn('closefd is not supported in py2')
        if opener is not None:
            warning.warn('opener is not supported in py2')
        return codecs.open(filename=file, mode=mode, encoding=encoding,
               errors=errors, buffering=buffering)

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
        max_rows=10):
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
    #logging.debug("SEARCH:r_search_response=%s", r_search_response)
    
    return r_search_response


    
# =============================================================================

def main():
    """ News polling and save to file """    
    
    # Initialisation du loggeur
    loggingFormatString = '%(asctime)s:%(levelname)s:%(threadName)s:%(funcName)s:%(message)s'
    logging.basicConfig(format=loggingFormatString, level=logging.DEBUG)
    
    
    # Démarrage  du traitement    
    logging.info('INIT')    
    logging.info("INIT:platform.system=%s", platform.system())

    # News polling
    news_data = ws_get_news(access_token=ws_auth_token())
    logging.info("NEWS:status=%s", news_data['status'])
    logging.info("NEWS:numFound=%s", news_data['numFound'])
    
    # TODO: construire le dossier de destination
    out_file_path = "afp_poller.json"
    with open(out_file_path, "w", encoding='utf-8') as fh:
        json_string = json.dumps(news_data, ensure_ascii=False)  # HACK: fh.write(json.dump(news_data, ensure_ascii=False))
        logging.debug("NEWS:type(json_string)=%s", type(json_string))

        #json_string = json_string.encode('utf8')  # HACK: python2
        fh.write(json_string)
    logging.info("NEWS:out_file_path=%s", out_file_path)

    # TODO: request par défaut
    # TODO: argparse avec log level
    # TODO: logging dans syslog

    logging.info('END')
    return 0  # TODO: gérer les exceptions et le code retour

# =============================================================================

if __name__ == '__main__':
    ret_code = main()
    sys.exit(ret_code)
