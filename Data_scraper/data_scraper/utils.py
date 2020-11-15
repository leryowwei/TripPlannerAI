""" This module contains all the common functions that can be used in all main engines """

import pickle
import os
import csv

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