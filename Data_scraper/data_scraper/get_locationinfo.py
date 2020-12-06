""" This module gets information of a specific location by accessing APIs and
    scraping trip advisor.
"""

from access_api import check_location_foursquare, check_location_foursquare_detail
from access_api import check_location_google, check_location_here
from utils import read_cell, write_cell

def get_locationinfo(location_data, user_class, driver, gsheet, api_type):
    """ Access APIs and tripadvisor to build location's information
    
        Note: if the API limits are reached, code will be terminated and a progress
        file will be produced so that the process can be continued again the next day.
    
    """
    # get attributes from user class
    place = user_class.place
    country = user_class.country
    
    new_location = {}
    
    for keyword in location_data:
        # check google api limit
        gapi_date = read_cell(gsheet, 'google', 'DATE')
        gapi_count = read_cell(gsheet, 'google', 'COUNT')
        
        
        
        # get basic results from google api based on keyword
        googleapi_results = check_location_google(keyword, place, country)
        
        # got result means we will use the google api name to search foursquare/here api and tripadvisor
        # all results will be stored in a new dictionary
        if googleapi_results:
            place_name = googleapi_results['name']
    
            # make sure no repeatitive data        
            if place_name not in new_location:
                print ("Valid location. Keyword {} found to be {}. Building location's database now....".format(keyword, place_name))
                
                # check APi limit of the day
                
                # get data from api depending on user input
                if api_type == 'foursquare':
                    check_location_foursquare()
                elif api_type == 'foursquare_detail':
                    check_location_foursquare_detail()
                elif api_type == 'here':
                    check_location_here()
    
                # scrap trip advisor website to get reviews and hours
                tripadvisor_results = extract_ta_data(place_name, user_class, driver)
    
                # store everything in dictionary
                # get existing data from the old dictionary
                new_location[place_name] = location_data[keyword]      
                # form api key based on api_type
                api_key = "{} API".format(api_type)
                new_location[place_name] = {'name': place_name,
                                            'google API': googleapi_results,
                                            'four square API': foursquareapi_results,
                                            'trip advisor': tripadvisor_results}
                
    return new_location