""" This module scraps a particular website to get the headers and paragraphs
"""
import requests
from utils import logger
from bs4 import BeautifulSoup

def get_title(html):
    """Scrape page title."""
    title = None
    if html.title.string:
        title = html.title.string
    elif html.find("meta", property="og:title"):
        title = html.find("meta", property="og:title").get('content')
    elif html.find("meta", property="twitter:title"):
        title = html.find("meta", property="twitter:title").get('content')
    elif html.find("h1"):
        title = html.find("h1").string
    return title

def scrape_page(url, websites_data):
    """Scrape target URL for useful information i.e. headers and paragraphs"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    r = requests.get(url, headers=headers)
    html = BeautifulSoup(r.content, 'html.parser')
    title_name = get_title(html)
    
    logger.info('Scraping {}'.format(url))

    # check if the same site has been scrapped before
    if title_name in websites_data:
        logger.info("    Website data already exists. Skipped.")
        return websites_data
    else:
        result = {}
        
        # find out all lines with headers and any paragraphs associated to them
        flag = ''
        for para in html.find_all():
          if para.name in ['h4', 'h3', 'h2', 'h1', 'h']:
            result[para.text] = ""
            flag = para.text
          
          if flag != '' and para.name == "p":
            result[flag] += para.text
            
        # store data to website data
        websites_data[title_name] = result
            
        return websites_data

