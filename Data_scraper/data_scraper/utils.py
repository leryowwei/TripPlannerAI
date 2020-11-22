""" This module contains all the common functions that can be used in all main engines """

import pickle
import os
import csv
import pickle
import constants
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def read_pickle_file(filename):
  """read python dict back from the file"""
  pkl_file = open(filename, 'rb')
  mydict = pickle.load(pkl_file)
  pkl_file.close()

  return mydict

def write_output_pickle(data, output_dir, output_file_name):
  """ Writes output data as pickle format """

  # write python dict to a file
  output = open(os.path.join(output_dir, '{}.pkl'.format(output_file_name)), 'wb')
  pickle.dump(data, output)
  output.close()

  print ('Successfully created pickle file...')

  return None

def write_output_csv(data, output_dir, output_file_name):
  """ Writes output data as csv format """
  
  # write python dict to csv
  with open(os.path.join(output_dir,'{}.csv'.format(output_file_name)),'w', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerows(data.items())

  print ('Successfully created csv file...')

  return None

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
        
    gsheet.values().update(spreadsheetId=constants.SPREADSHEET_ID, range='Sheet1!B2', valueInputOption='RAW', body=body).execute()

    # write data
    gsheet.values().update(spreadsheetId=constants.SPREADSHEET_ID, range=range_name, 
                           valueInputOption='RAW', body=body).execute()
    
    return gsheet