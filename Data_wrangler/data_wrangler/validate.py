"""This module validates the tripadvisor and API data against the google data"""

from fuzzywuzzy import fuzz
from streetaddress import StreetAddressParser
from .constants import ADDRESS_LIMIT, NAME_LIMIT
from .utils import logger

def compare_address(address_1, address_2):
    """Compare similarity between two addresses"""
    # parse the addresses
    addr_parser = StreetAddressParser()
    add_1 = addr_parser.parse(address_1)
    add_2 = addr_parser.parse(address_2)

    # compare house number and street full name to get an average score
    score = fuzz.token_sort_ratio(add_1['street_full'], add_2['street_full'])

    # check if it passes the limit
    if score >= ADDRESS_LIMIT:
        return True, score
    else:
        return False, score

def compare_name(name_1, name_2):
    """Compare similarity between two names"""
    score = fuzz.token_set_ratio(name_1, name_2)

    # check if it passes the limit
    if score >= NAME_LIMIT:
        return True, score
    else:
        return False, score

def validate_per_data(data_to_validate, google_data, data_type):
    """Validate trip advisor data"""
    # assign variables
    name_google = google_data['name']
    address_google = google_data['address']
    address_data = None
    name_data = None

    if data_type == 'tripadvisor':
        # if reviews are not empty, then assign the variables
        if data_to_validate['reviews']:
            address_data = data_to_validate['address']
            name_data = data_to_validate['name']
    elif data_type == 'foursquare_detail':
        # only assign when the API data exists
        if data_to_validate:
            address_data = ', '.join(data_to_validate['response']['venue']['location']['formattedAddress'])
            name_data = data_to_validate['response']['venue']['name']
    else:
        raise ValueError('Data type {} not recognised...'.format(data_type))

    # invalid terms to ignore
    invalid_terms = [None, 'N/A']

    # either name or address check is correct then allow to go through
    if name_data not in invalid_terms and name_google not in invalid_terms:
        result_name, score_name = compare_name(name_data, name_google)
    else:
        result_name = False
        score_name = 'N/A'

    if address_data not in invalid_terms and address_google not in invalid_terms:
        result_add, score_add = compare_address(address_data, address_google)
    else:
        result_add = False
        score_add = 'N/A'

    # invalid data then return empty dict
    if result_name or result_add:
        logger.info('Valid: {} data correct. Name Score: {}. Address Score: {} ...'.format(data_type, score_name, score_add))
        return data_to_validate
    else:
        logger.info('Invalid: {} data wrong. Name Score: {}. Address Score: {} ...'.format(data_type, score_name, score_add))
        return {}

def validate_data(loc_dict):
    """Validates the trip advisor and API data against google data"""

    # unpack dictionary first
    google_data = loc_dict['Google_data']
    api_used = loc_dict['API_used']

    # (1) validate tripadvisor data
    loc_dict['TripAdvisor_data'] = validate_per_data(loc_dict['TripAdvisor_data'], google_data, 'tripadvisor')

    # (2) validate api data
    # For API data, this function is only built for foursquare detail/premium at the moment.
    # If other API is used, log error and set the api dictionary to be empty
    if api_used != 'foursquare_detail':
        logger.warning('API {} not supported for location {}. Setting API data to empty dict...'.format(api_used, loc_dict['name']))
        loc_dict['API_data'] = {}
    else:
        loc_dict['API_data'] = validate_per_data(loc_dict['API_data'], google_data, api_used)

    return loc_dict
