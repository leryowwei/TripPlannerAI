""" Data_scraper python package's main enry point code

    To run the package, please use command:
        python data_scraper [-h] [--api]
"""

import spacy
import constants
import os
import argparse
from datetime import datetime
from selenium import webdriver
from user import User
from search_google import define_googlequery, request_urls
from scrape_web import scrape_page
from data_cleaning import clean_data
from utils import write_output_pickle, write_output_csv, get_gsheet, read_cell, write_cell
from get_locationinfo import get_locationinfo
from extract_gmaps import extract_gmaps

def main(api_type):
    """ Main function for data scraping tool 
        
        Calls relevant functions and go through the whole process
        (1) initialisation by setting up relevant models/ drivers
        (2) google search to find out all the websites
        (3) loop through all urls and scrape each website - only store headers and paragraphs
        (4) data cleaning - find out whether the headers are valid or not. If yes, build a dictionary
        (5) Access APIs and TripAdvisor to build database of the location
        (6) output data as CSV and pickle files
    """
    # Initialisation
    start = datetime.now()
    
    # set up relevant paths
    parent_path = os.path.abspath('..')
    nlp_folder_path = os.path.join(parent_path, 'NLP_ML', 'nlp_loc_model')
    webdriver_path = os.path.join(parent_path, 'Miscellaneous', 'chromedriver_win32', 'chromedriver.exe')
    misc_path = os.path.join(parent_path, 'Miscellaneous')
    
    # setup user class
    user_class = User(constants.DEFAULT_USER)

    # set up google sheet for API counter
    print ("Getting google sheet....")
    #gsheet = get_gsheet(misc_path)
    
    # setup webdriver
    # Create a new instance of the driver
    print ('Setting up webdriver...')
    try:
        option = webdriver.ChromeOptions()
        #option.add_argument('headless')
        #option.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome(executable_path = webdriver_path, options = option)
    except:
        raise ValueError ("Failed in setting up webdriver. Please check if webdriver is in Miscellaneous folder.")        

    extract_gmaps('haji lane', user_class, driver)

    # load NLP models - LOC
    #print ("Loading Spacy LOC model...")
    #try:
    #    nlp_loc = spacy.load(nlp_folder_path)
    #except:
    #    raise ValueError ("NLP LOC model not found. Please check if the trained model is in {}.".format(nlp_folder_path) + 
    #                      "Otherwise, please run the script /NLP_ML/train_entity.py.")

    
    # form keywords to search google based on user's input
    #print ('Processing user input to form query list...')
    #query_list = define_googlequery(user_class)    

    # get urls based on keywords
    #print ('Searching google for urls...')    
    #urls = request_urls(query_list, user_class, num_result=1, pause_time=1)


    # loop through all url results to get headers and paragraphs for each website
    # store as dictionary, key: header name, value: paragraph associated to header
    # websites_data = {}
    # for x in urls:
    #     websites_data = scrape_page(x, websites_data)

    # go through all the headers collected and run nlp on them to recognise the
    # location entity that we are interested in
    print('Data cleaning...')
    #location_data = clean_data(websites_data, nlp_loc, user_class)
    
    # Access APIS and Tripadvisor to build database
    print ('Accessing APIs and TripAdvisor to build database...')
    #location_data = get_locationinfo(location_data, user_class, driver, gsheet, api_type)

    # write data - CSV and pickle
    print ('Writing data...')
    #write_output_csv(location_data)
    #write_output_pickle(location_data)
            
    # record time taken 
    end = datetime.now()
    time_taken = end - start
    print ('Process completed...')
    print('Time taken for the process: ', time_taken)

if __name__ == "__main__": 
    # setup argparser
    parser = argparse.ArgumentParser(description = 'Data scraping engine for trip planner AI tool...')
    parser.add_argument('--api', type=str, default='foursquare', 
                        choices=['foursquare', 'foursquare_detail', 'here'],
                        help='Default is foursquare. User can choose from the list: foursquare, foursquare_detail and here.')
    
    args = parser.parse_args()
    
    # call main function
    main(args.api)
    
