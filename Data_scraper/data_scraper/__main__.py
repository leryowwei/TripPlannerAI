""" Data_scraper python package's main enry point code

    To run the package, please use command:
        python -m data_scraper [-h] [--api] [--test]
"""
import spacy
import os
import argparse
import math
from datetime import datetime
from selenium import webdriver
from .user import User
from .search_google import define_googlequery, request_urls
from .scrape_web import scrape_page
from .data_cleaning import clean_data
from .utils import read_json_file, write_output_csv, get_gsheet, logger, read_pickle_file, str2bool
from .get_locationinfo import get_locationinfo
from . import constants
from func_timeout import func_timeout, FunctionTimedOut

def main(api_type, keyword, headless):
    """ Main function for data scraping tool 
        
        Calls relevant functions and go through the whole process
        (1) initialisation by setting up relevant models/ drivers
        (2) Check if testing mode is on or not. If keyword is specified, means it is on
        
        (A) With testing mode
        ---------------------
        (1) Access APIs and TripAdvisor to build database of the keyword specified
        (2) output final data as CSV     
        
        (B) Normal mode
        ---------------
        (1) Check if TMP files exists. If exist, continue from where has been left off. 
        
        If TMP files do not exist,
        (1) google search to find out all the websites
        (2) loop through all urls and scrape each website - only store headers and paragraphs
        (3) data cleaning - find out whether the headers are valid or not. If yes, build a dictionary
        (4) Access APIs and TripAdvisor to build database of the location
        (5) output final data as CSV
        
        If TMP files exist,
        (1) Access APIs and TripAdvisor to build database of the location
        (2) output final data as CSV        
    """
    start = datetime.now()
    
    # set up relevant paths
    parent_path = os.path.abspath('..')
    nlp_folder_path = os.path.join(parent_path, 'NLP_ML', 'nlp_loc_model')
    webdriver_path = os.path.join(parent_path, 'Miscellaneous', 'chromedriver_win32', 'chromedriver.exe')
    misc_path = os.path.join(parent_path, 'Miscellaneous')
    output_path = os.path.join(parent_path, 'Data_scraper', 'output_data')
    
    # create output data folder
    if not os.path.exists(output_path):
        os.mkdir(output_path)    
    
    # setup user class
    user_class = User(constants.DEFAULT_USER)
    
    # log message for API
    logger.info('API: {} chosen by user. All data will be obtained from this API...'.format(api_type))

    # set up google sheet for API counter
    logger.info("Getting google sheet....")
    gsheet = get_gsheet(misc_path)
    
    # setup webdriver
    # Create a new instance of the driver
    logger.info('Setting up webdriver...')
    try:
        option = webdriver.ChromeOptions()
        if headless:            
            option.add_argument('headless')
            option.add_argument('window-size=1920x1080')
        else:
            logger.info('Selenium webdriver headless set to False. You will see chrome popping up automatically...')
        option.add_argument("--log-level=3")
        driver = webdriver.Chrome(executable_path = webdriver_path, options = option)
    except:
        raise ValueError ("Failed in setting up webdriver. Please check if webdriver is in Miscellaneous folder.")   

    # load NLP models - LOC
    logger.info("Loading Spacy LOC model...")
    try:
        nlp_loc = spacy.load(nlp_folder_path)
    except:
        raise ValueError ("NLP LOC model not found. Please check if the trained model is in {}.".format(nlp_folder_path) + 
                          "Otherwise, please run the script /NLP_ML/train_entity.py.")
    
    # check if testing mode is on - if on, get API data and tripadvisor data based on the keyword specified.
    # otherwise, run regular mode
    if not keyword:
        # check if code terminated before in the last run due to API limit - if yes, rerun from where we stopped
        # look for tmp files in the output directory
        tmp_loc_found = os.path.join(output_path, "{}.json".format(constants.TMP_LOCFOUND_NAME))
        tmp_loc_scraped = os.path.join(output_path, "{}.json".format(constants.TMP_LOCSCRAPED_NAME))
        
        if os.path.exists(tmp_loc_found) and os.path.exists(tmp_loc_scraped):
            logger.info('TMP files found in output directory. Code now continues accessing API to get info from where has been left off...')
            scraped_data = read_json_file(tmp_loc_scraped)        
            location_found = read_json_file(tmp_loc_found)
            
            # check how many keywords left
            logger.info('A total of {} keywords/headers left to get data from API...'.format(len(scraped_data)))
            
        else:
            # form keywords to search google based on user's input
            logger.info('Processing user input to form query list...')
            query_list = define_googlequery(user_class)    
        
            # get urls based on keywords
            logger.info('Searching google for urls...')    
            urls = request_urls(query_list, user_class, num_result=1, pause_time=1)
        
            # loop through all url results to get headers and paragraphs for each website
            # store as dictionary, key: header name, value: paragraph associated to header
            logger.info('Scraping all urls found...')
            websites_data = {}
            # sometimes beautiful soup hangs - so implement time check
            # if after 5 secs and still not yet finish scraping the one url, then terminate it
            for x in urls:
                try:
                    websites_data = func_timeout(5, scrape_page, args=(x, websites_data))
                except FunctionTimedOut:
                    logger.warning('Timed out when scraping url {}. Skipped...'.format(x))
                except Exception as e:
                    raise ValueError('Web scraping failed...')

            # go through all the headers collected and run nlp on them to recognise the
            # location entity that we are interested in
            logger.info('Data cleaning...')
            scraped_data = clean_data(websites_data, nlp_loc, user_class)
            
            # initialise empty list
            location_found = []
    else:
        logger.info('Testing mode on. Directly accessing API using keyword specified: {}...'.format(keyword))
        
        # build scraped_data dictionary using the keyword
        scraped_data = {keyword:{'website':'N/A', 'header':'N/A', 'paragraph':'N/A'}}
        location_found = []
        
    # Access APIS and Tripadvisor to build database
    logger.info('Accessing APIs and TripAdvisor to build database...')
    terminate_flag = get_locationinfo(scraped_data, location_found, user_class, driver, gsheet, api_type, output_path)

    # write final data to CSV if the code not terminated - put every n locations in one csv
    if not terminate_flag:
        # check if there is any TMP files. If yes, delete them
        try:
            if os.path.exists(tmp_loc_found):
                os.remove(tmp_loc_found)
 
            if os.path.exists(tmp_loc_scraped):
                os.remove(tmp_loc_scraped)
        except:
            pass
            
        # write data out in CSV format
        logger.info('Writing CSV data...')
        files_count = 0
        count = 0
        output_dict = {}
        
        # count how many files are there
        for filename in os.listdir(output_path):
            # only look at pickle files
            if filename.endswith('.pkl'):
                files_count += 1
                
        for filename in os.listdir(output_path):
            # only look at pickle files
            if filename.endswith('.pkl'):
                tmp_dict = read_pickle_file(os.path.join(output_path, filename))
                output_dict[tmp_dict['name']] = tmp_dict
                count += 1

            # every n files, write them out
            if count != 0 and (count % constants.NUM_LOC_PER_CSV == 0 or count == files_count): 
                write_output_csv(output_dict, output_path, "CSV_DATA_Set{}".format(math.ceil(count / constants.NUM_LOC_PER_CSV)))
                # reset
                output_dict = {}
    
    # close webdriver
    driver.quit()

    # record time taken 
    end = datetime.now()
    time_taken = end - start
    logger.info('Process completed...')
    logger.info('Time taken for the process: {}'.format(time_taken))

if __name__ == "__main__": 
    # setup argparser
    parser = argparse.ArgumentParser(description = 'Data scraping engine for trip planner AI tool...')
    parser.add_argument('--api', type=str, default='foursquare', 
                        choices=['foursquare', 'foursquare_detail', 'here'],
                        help='Default is foursquare. User can choose from the list: foursquare, foursquare_detail and here.')

    parser.add_argument('--test', type=str, default=None,
                        help='This is testing mode. Insert the keyword to find out the API information for this location')

    parser.add_argument('--headless', type=str2bool, default=True, 
                        help='Default is True. If set to False, selenium window will be shown. Otherwise, headless option will be used. Setting to TRUE will slow things down')
    
    args = parser.parse_args()
    
    # call main function
    main(args.api, args.test, args.headless)
    
