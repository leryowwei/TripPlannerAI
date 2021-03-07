""" This module contains all the common functions that can be used in all main engines """

import pickle
import os
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathvalidate import sanitize_filename, is_valid_filename
from .constants import STRING_TO_TIME_MAPPING, TIME_PERIOD


def convert_12hr_to_24hr_timerange(x):
    """Convert 12 hour system range of time to 24 hour system"""

    if not x:
        return None
    elif ('CLOSED' in x.upper()) or ('NONE' in x.upper()):
        return None
    elif '24 HOURS' in x.upper():
        return "00:00–24:00"
    else:
        modified_time = []

        # split to list
        range_of_time = x.upper().split("–")

        # only work with a list of two items
        if len(range_of_time) != 2:
            raise ValueError("Unable to work with this type of time range format {}".format(x))

        for ite, time in enumerate(range_of_time):
            # remove all spacing
            time = time.replace(" ", "")

            # check if it's actual time or phrase like noon or midnight
            if time in STRING_TO_TIME_MAPPING:
                modified_time.append(STRING_TO_TIME_MAPPING[time])
            else:
                try:
                    # if AM or PM exists in second item but not first, add that into first item too
                    if ite == 0:
                        if not any(period in time for period in TIME_PERIOD) and \
                                any(period in range_of_time[1] for period in TIME_PERIOD):
                            time = "{}{}".format(time, range_of_time[1][-2:])

                    # try different methods to strip time (e.g. 3:00PM, 3PM)
                    try:
                        temp_time = datetime.strptime(time, "%I:%M%p")
                    except ValueError:
                        temp_time = datetime.strptime(time, "%I%p")
                    modified_time.append(datetime.strftime(temp_time, "%H:%M"))

                except ValueError:
                    raise ValueError("Unrecognised time {}".format(x))

        return "–".join(modified_time)


def find_maxnum_in_str(x):
    """ find max number in string """
    l = []

    for t in x:
        if t:
            # in case the string is in words like one, two, three.. convert to arabic numbers
            t = text2int(t)

            # add numbers to list
            try:
                l.append(float(t))
            except ValueError:
                pass

    # always return the maximum number
    try:
        return max(l)
    except:
        return None


def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):  numwords[word] = (1, idx)
        for idx, word in enumerate(tens):       numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales): numwords[word] = (10 ** (idx * 3 or 2), 0)

    ordinal_words = {'first': 1, 'second': 2, 'third': 3, 'fifth': 5, 'eighth': 8, 'ninth': 9, 'twelfth': 12}
    ordinal_endings = [('ieth', 'y'), ('th', '')]

    textnum = textnum.replace('-', ' ')

    current = result = 0
    curstring = ""
    onnumber = False
    for word in textnum.split():
        if word in ordinal_words:
            scale, increment = (1, ordinal_words[word])
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
            onnumber = True
        else:
            for ending, replacement in ordinal_endings:
                if word.endswith(ending):
                    word = "%s%s" % (word[:-len(ending)], replacement)

            if word not in numwords:
                if onnumber:
                    curstring += repr(result + current) + " "
                curstring += word + " "
                result = current = 0
                onnumber = False
            else:
                scale, increment = numwords[word]

                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0
                onnumber = True

    if onnumber:
        curstring += repr(result + current)

    return curstring


def reject_outliers(data, max_deviations=1):
    """Use this to reject outliers from list
    """
    # only filter more than one element, otherwise return the data back
    if len(data) > 1:
        # find out outliers and remove them
        mean = np.mean(data)
        standard_deviation = np.std(data)
        distance_from_mean = abs(data - mean)
        not_outlier = distance_from_mean < max_deviations * standard_deviation
        new_data = [ele for i, ele in enumerate(data) if not_outlier[i]]

        # if empty list comes back then return the original data again
        if not new_data:
            new_data = data

        return new_data

    else:
        return data


def take_closest_num(num, col):
    """ find the element in list which is closest to the number"""
    return min(col, key=lambda x: abs(x - num))


def form_str(inp_list):
    """Take in a list of inputs and combine them into one big string

        each item of the list can be a str or list
    """
    para = ""
    for inp in inp_list:
        # only if the variable exists/is not none
        if inp:
            if isinstance(inp, list):
                para += " ".join(inp) + " "
            elif isinstance(inp, str):
                para += inp + " "
            else:
                raise TypeError("Form_str function does not support instances type other than list or str...")
    return para


def check_filename(output_file_name):
    """Check filename is valid or not. If invalid, convert the file"""

    if not is_valid_filename(output_file_name):
        new_file_name = sanitize_filename(output_file_name)
        logger.warning('File name {} invalid. New file name is {}.pkl.'.format(output_file_name, new_file_name))
    else:
        new_file_name = output_file_name

    return new_file_name


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


def read_json_file(filepath):
    """Read json file """

    with open(filepath, 'r') as file_handle:
        data = json.load(file_handle)

    return data


def read_excel_as_df(path, sheet_name, lower=False, upper=False):
    """Read in excel file and save sheet as dataframe
       User can convert dataframe to lowercase/uppercase by setting lower=True or upper=True
    """

    try:
        df = pd.read_excel(open(path, 'rb'), sheet_name=sheet_name)

        if lower and not upper:
            df = df.apply(lambda x: x.astype(str).str.lower())
        elif upper and not lower:
            df = df.apply(lambda x: x.astype(str).str.upper())
        elif upper and lower:
            raise ValueError('Function does not allow both lower and upper to be set as True')

    except:
        raise ValueError('Sheet name: {} not found in {}'.format(sheet_name, path))

    return df


def setup_logging():
    """ Get logger. Can be called in each module"""

    log_file_name = 'DataWrangler_{}.log'.format(datetime.today().strftime('%Y%m%d_%H%M%S'))

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
