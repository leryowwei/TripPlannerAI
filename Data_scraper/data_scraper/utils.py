""" This module contains all the common functions that can be used in all main engines """

import pickle
import os
import csv
import logging
import json
from . import constants
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
from pathvalidate import sanitize_filename, is_valid_filename

def check_filename(output_file_name):
    """Check filename is valid or not. If invalid, convert the file"""

    if not is_valid_filename(output_file_name):
        new_file_name = sanitize_filename(output_file_name)
        logger.warning('File name {} invalid. New file name is {}.pkl.'.format(output_file_name, new_file_name))
    else:
        new_file_name = output_file_name

    return new_file_name

def read_pickle_file(filename):
    """read python dict back from the file"""
    
    pkl_file = open(filename, 'rb')
    mydict = pickle.load(pkl_file)
    pkl_file.close()
    
    return mydict

def write_output_pickle(data, output_dir, output_file_name):
    """ Writes output data as pickle format """
  
    # check filename
    output_file_name = check_filename(output_file_name)
    
    # write python dict to a file
    output = open(os.path.join(output_dir, '{}.pkl'.format(output_file_name)), 'wb')
    pickle.dump(data, output)
    output.close()
    
    logger.info('Successfully created pickle file {}.pkl...'.format(output_file_name))
    
    return None

def write_output_csv(data, output_dir, output_file_name):
    """ Writes output data as csv format """

    # check filename
    output_file_name = check_filename(output_file_name)
    
    # write python dict to csv
    with open(os.path.join(output_dir,'{}.csv'.format(output_file_name)),'w', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerows(data.items())
    
    logger.info('Successfully created csv file {}.csv...'.format(output_file_name))
    
    return None

def write_output_json(data, output_dir, output_file_name):
    """Writes output file as json format """

    # check filename
    output_file_name = check_filename(output_file_name)
      
    with open(os.path.join(output_dir, "{}.json".format(output_file_name)), 'w') as file_handle:
        json.dump(data, file_handle)
    
    logger.info('Successfully created json file {}.json...'.format(output_file_name))
    
    return None

def read_json_file(filepath):
    """Read json file """
    
    with open(filepath, 'r') as file_handle:
        data = json.load(file_handle)
    
    return data

def get_gsheet(path):
    """Get google sheet using credentials set up"""

    token_path = os.path.join(path, 'token.pickle')
    cred_path = os.path.join(path, 'credentials.json')
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, constants.SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    
    return sheet

def read_cell(gsheet, api_name, field):
    """ Read value from a cell in a googlesheet """
    
    # establish range name
    try:
        range_name = constants.GSHEET_DICT[api_name][field]
    except:
        raise ValueError('Range name not found from the dictionary in constants.py. Please check if the keys are correct.')
    
    # read data
    result = gsheet.values().get(spreadsheetId=constants.SPREADSHEET_ID, 
                                                 range=range_name).execute()
    # return string from nested list
    return result.get('values')[0][0]

def write_cell(gsheet, api_name, field, input_value):
    """ Write value to a cell in a googlesheet """
    
    # establish range name
    try:
        range_name = constants.GSHEET_DICT[api_name][field]
    except:
        raise ValueError('Range name not found from the dictionary in constants.py. Please check if the keys are correct.')

    # write data
    values = [[input_value],]
    body = {'values': values}

    # write data
    gsheet.values().update(spreadsheetId=constants.SPREADSHEET_ID, range=range_name, 
                           valueInputOption='RAW', body=body).execute()
    
    return gsheet

def str2bool(v):
    """Convert string to boolean"""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ValueError('Boolean value expected.')

def setup_logging():
    """ Get logger. Can be called in each module"""    

    log_file_name = 'DataScraper_{}.log'.format(datetime.today().strftime('%Y%m%d_%H%M%S'))
    
    try:
        if os.path.exists(log_file_name):
            os.remove(log_file_name)
    except:
        pass

    # create logger
    log = logging.getLogger('DATA')
    log.setLevel(logging.DEBUG)
    
    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_file_name, 'w', 'utf-8')
    fh.setLevel(logging.INFO)
    
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)
    
    # first log message
    log.info("Setup logger...")
        
    return log

logger = setup_logging()